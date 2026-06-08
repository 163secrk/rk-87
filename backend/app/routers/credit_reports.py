from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.models.credit_report import CreditReport
from app.models.customer import Customer
from app.schemas.credit_report import CreditReportCreate, CreditReportResponse
from app.schemas.common import APIResponse, PaginatedResponse

router = APIRouter(prefix="/credit-reports", tags=["信用报告"])


@router.get("", response_model=PaginatedResponse[CreditReportResponse])
async def get_credit_reports(
    page: int = 1,
    page_size: int = 20,
    customer_id: int = None,
    customer_name: str = None,
    id_card: str = None,
    report_source: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = select(CreditReport).join(Customer, CreditReport.customer_id == Customer.id)
    count_query = select(func.count(CreditReport.id)).join(Customer, CreditReport.customer_id == Customer.id)

    if customer_id:
        query = query.where(CreditReport.customer_id == customer_id)
        count_query = count_query.where(CreditReport.customer_id == customer_id)

    if customer_name:
        query = query.where(Customer.name.contains(customer_name))
        count_query = count_query.where(Customer.name.contains(customer_name))

    if id_card:
        query = query.where(Customer.id_card.contains(id_card))
        count_query = count_query.where(Customer.id_card.contains(id_card))

    if report_source:
        query = query.where(CreditReport.report_source == report_source)
        count_query = count_query.where(CreditReport.report_source == report_source)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(CreditReport.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    reports = result.scalars().all()

    response_items = []
    for r in reports:
        report_dict = CreditReportResponse.model_validate(r).model_dump()
        if r.customer:
            report_dict["customer_name"] = r.customer.name
            report_dict["id_card"] = r.customer.id_card
        report_dict["total_debt"] = r.total_loan_amount
        report_dict["query_count"] = r.query_count_last_30d
        report_dict["report_detail"] = r.report_data
        report_dict["report_date"] = r.created_at
        response_items.append(CreditReportResponse(**report_dict))

    return PaginatedResponse(
        code=200,
        message="success",
        data={
            "items": response_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    )


@router.get("/{report_id}", response_model=APIResponse[CreditReportResponse])
async def get_credit_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(CreditReport).join(Customer, CreditReport.customer_id == Customer.id)
        .where(CreditReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    report_dict = CreditReportResponse.model_validate(report).model_dump()
    if report.customer:
        report_dict["customer_name"] = report.customer.name
        report_dict["id_card"] = report.customer.id_card
    report_dict["total_debt"] = report.total_loan_amount
    report_dict["query_count"] = report.query_count_last_30d
    report_dict["report_detail"] = report.report_data
    report_dict["report_date"] = report.created_at
    report_dict["updated_at"] = report.created_at
    
    return APIResponse(code=200, message="success", data=CreditReportResponse(**report_dict))


@router.post("", response_model=APIResponse[CreditReportResponse])
async def create_credit_report(
    report_data: CreditReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(Customer).where(Customer.id == report_data.customer_id)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    import random
    from datetime import datetime

    if not report_data.report_no:
        report_no = f"CR{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
    else:
        report_no = report_data.report_no

    report_dict = report_data.model_dump(exclude_unset=True)

    if report_data.total_debt is not None:
        report_dict["total_loan_amount"] = report_data.total_debt
        report_dict.pop("total_debt", None)

    if report_data.query_count is not None:
        report_dict["query_count_last_30d"] = report_data.query_count
        report_dict.pop("query_count", None)

    if report_data.report_detail is not None:
        report_dict["report_data"] = report_data.report_detail
        report_dict.pop("report_detail", None)

    report_dict.pop("report_no", None)
    report_dict["report_no"] = report_no

    report = CreditReport(
        **report_dict,
        queried_by=current_user.id
    )

    db.add(report)
    await db.commit()
    await db.refresh(report)

    await db.refresh(report, ["customer"])
    
    report_dict = CreditReportResponse.model_validate(report).model_dump()
    if report.customer:
        report_dict["customer_name"] = report.customer.name
        report_dict["id_card"] = report.customer.id_card
    report_dict["total_debt"] = report.total_loan_amount
    report_dict["query_count"] = report.query_count_last_30d
    report_dict["report_detail"] = report.report_data
    report_dict["report_date"] = report.created_at
    report_dict["updated_at"] = report.created_at
    
    return APIResponse(code=201, message="创建成功", data=CreditReportResponse(**report_dict))


@router.post("/query/{customer_id}", response_model=APIResponse[CreditReportResponse])
async def query_credit_report(
    customer_id: int,
    report_source: str = "internal",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    import random
    from datetime import datetime

    report_no = f"CR{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"

    base_score = customer.credit_score
    random_factor = random.randint(-50, 50)
    credit_score = max(300, min(900, base_score + random_factor))

    if credit_score >= 800:
        credit_level = "A"
    elif credit_score >= 700:
        credit_level = "B"
    elif credit_score >= 600:
        credit_level = "C"
    elif credit_score >= 500:
        credit_level = "D"
    else:
        credit_level = "E"

    risk_tags = []
    if credit_score < 600:
        risk_tags.append("低信用评分")
    if customer.total_liabilities > customer.total_assets:
        risk_tags.append("资不抵债")
    if customer.monthly_income < 5000:
        risk_tags.append("低收入")

    report = CreditReport(
        customer_id=customer_id,
        report_no=report_no,
        report_source=report_source,
        credit_score=credit_score,
        credit_level=credit_level,
        total_loan_count=random.randint(0, 10),
        total_loan_amount=round(random.uniform(0, 500000), 2),
        current_loan_count=random.randint(0, 5),
        current_loan_balance=round(random.uniform(0, 300000), 2),
        overdue_count=random.randint(0, 3),
        overdue_amount=round(random.uniform(0, 50000), 2),
        max_overdue_days=random.randint(0, 90),
        query_count_last_30d=random.randint(0, 10),
        query_count_last_90d=random.randint(0, 20),
        query_count_last_180d=random.randint(0, 30),
        risk_tags=",".join(risk_tags) if risk_tags else None,
        queried_by=current_user.id,
        remark="系统自动生成的模拟信用报告"
    )

    db.add(report)
    await db.commit()
    await db.refresh(report)

    await db.refresh(report, ["customer"])
    
    report_dict = CreditReportResponse.model_validate(report).model_dump()
    if report.customer:
        report_dict["customer_name"] = report.customer.name
        report_dict["id_card"] = report.customer.id_card
    report_dict["total_debt"] = report.total_loan_amount
    report_dict["query_count"] = report.query_count_last_30d
    report_dict["report_detail"] = report.report_data
    report_dict["report_date"] = report.created_at
    report_dict["updated_at"] = report.created_at
    
    return APIResponse(code=200, message="查询成功", data=CreditReportResponse(**report_dict))
