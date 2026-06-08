from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.loan_application import LoanApplication, LoanStatus
from app.models.approval_record import ApprovalRecord, ApprovalAction
from app.schemas.loan_application import (
    LoanApplicationCreate,
    LoanApplicationUpdate,
    LoanApplicationResponse,
    LoanApplicationListResponse,
    RiskAssessmentResult,
    ReviewRequest,
)
from app.schemas.common import APIResponse, PaginatedResponse
from app.services.approval_service import ApprovalService
from app.services.risk_assessment import RiskAssessmentService

router = APIRouter(prefix="/loan-applications", tags=["贷款申请"])


@router.get("", response_model=PaginatedResponse[LoanApplicationListResponse])
async def get_loan_applications(
    page: int = 1,
    page_size: int = 20,
    status: LoanStatus = None,
    keyword: str = None,
    start_date: str = None,
    end_date: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = select(LoanApplication, Customer).join(Customer, LoanApplication.customer_id == Customer.id)
    count_query = select(func.count(LoanApplication.id)).select_from(LoanApplication).join(Customer, LoanApplication.customer_id == Customer.id)

    if status:
        query = query.where(LoanApplication.status == status)
        count_query = count_query.where(LoanApplication.status == status)

    if keyword:
        keyword_filter = (
            Customer.name.contains(keyword) |
            Customer.id_card.contains(keyword) |
            Customer.phone.contains(keyword) |
            LoanApplication.application_no.contains(keyword)
        )
        query = query.where(keyword_filter)
        count_query = count_query.where(keyword_filter)

    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.where(LoanApplication.created_at >= start_dt)
        count_query = count_query.where(LoanApplication.created_at >= start_dt)

    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        query = query.where(LoanApplication.created_at <= end_dt)
        count_query = count_query.where(LoanApplication.created_at <= end_dt)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(LoanApplication.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    items = []
    for app, customer in rows:
        item = LoanApplicationListResponse.model_validate(app)
        item.customer_name = customer.name
        item.customer_id_card = customer.id_card
        item.customer_phone = customer.phone
        items.append(item)

    return PaginatedResponse(
        code=200,
        message="success",
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    )


@router.get("/{application_id}", response_model=APIResponse[LoanApplicationResponse])
async def get_loan_application(
    application_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(LoanApplication).where(LoanApplication.id == application_id)
    )
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="申请不存在")
    return APIResponse(code=200, message="success", data=LoanApplicationResponse.model_validate(application))


@router.get("/{application_id}/approval-records", response_model=APIResponse[List])
async def get_approval_records(
    application_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ApprovalService(db)
    records = await service.get_approval_records(application_id)
    return APIResponse(code=200, message="success", data=[
        {
            "id": r.id,
            "action": r.action,
            "operator_name": r.operator_name,
            "operator_role": r.operator_role,
            "comment": r.comment,
            "risk_score_before": r.risk_score_before,
            "risk_score_after": r.risk_score_after,
            "risk_level_before": r.risk_level_before,
            "risk_level_after": r.risk_level_after,
            "created_at": r.created_at
        } for r in records
    ])


@router.post("/{application_id}/assess", response_model=APIResponse[RiskAssessmentResult])
async def assess_application(
    application_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(LoanApplication, Customer)
        .join(Customer, LoanApplication.customer_id == Customer.id)
        .where(LoanApplication.id == application_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="申请不存在")

    application, customer = row

    service = RiskAssessmentService(db)
    assessment = await service.assess_risk(customer, application)

    return APIResponse(code=200, message="success", data=assessment)


@router.post("", response_model=APIResponse[LoanApplicationResponse])
async def create_loan_application(
    application_data: LoanApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(Customer).where(Customer.id == application_data.customer_id)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    service = ApprovalService(db)
    application, _ = await service.create_application(
        customer,
        application_data.model_dump(),
        current_user
    )

    return APIResponse(code=201, message="创建成功", data=LoanApplicationResponse.model_validate(application))


@router.post("/{application_id}/review", response_model=APIResponse[LoanApplicationResponse])
async def review_application(
    application_id: int,
    review_data: ReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if review_data.action not in [ApprovalAction.APPROVE, ApprovalAction.REJECT, ApprovalAction.RETURN, ApprovalAction.CANCEL]:
        raise HTTPException(status_code=400, detail="无效的审批动作")

    service = ApprovalService(db)
    application = await service.manual_review(
        application_id,
        review_data.action,
        review_data.comment,
        current_user
    )

    if not application:
        raise HTTPException(status_code=404, detail="申请不存在")

    return APIResponse(code=200, message="审批完成", data=LoanApplicationResponse.model_validate(application))


@router.put("/{application_id}", response_model=APIResponse[LoanApplicationResponse])
async def update_loan_application(
    application_id: int,
    application_data: LoanApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(LoanApplication).where(LoanApplication.id == application_id)
    )
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="申请不存在")

    if application.status not in [LoanStatus.PENDING, LoanStatus.MANUAL_REVIEW]:
        raise HTTPException(status_code=400, detail="当前状态不允许修改")

    update_data = application_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)

    await db.commit()
    await db.refresh(application)

    return APIResponse(code=200, message="更新成功", data=LoanApplicationResponse.model_validate(application))
