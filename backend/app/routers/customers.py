from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.schemas.common import APIResponse, PaginatedResponse

router = APIRouter(prefix="/customers", tags=["客户管理"])


@router.get("", response_model=PaginatedResponse[CustomerResponse])
async def get_customers(
    page: int = 1,
    page_size: int = 20,
    keyword: str = None,
    risk_level: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = select(Customer)
    count_query = select(func.count(Customer.id))

    if keyword:
        keyword_filter = (
            Customer.name.contains(keyword) |
            Customer.id_card.contains(keyword) |
            Customer.phone.contains(keyword)
        )
        query = query.where(keyword_filter)
        count_query = count_query.where(keyword_filter)

    if risk_level:
        query = query.where(Customer.risk_level == risk_level)
        count_query = count_query.where(Customer.risk_level == risk_level)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Customer.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    customers = result.scalars().all()

    return PaginatedResponse(
        code=200,
        message="success",
        data={
            "items": [CustomerResponse.model_validate(c) for c in customers],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    )


@router.get("/{customer_id}", response_model=APIResponse[CustomerResponse])
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    return APIResponse(code=200, message="success", data=CustomerResponse.model_validate(customer))


@router.post("", response_model=APIResponse[CustomerResponse])
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(Customer).where(Customer.id_card == customer_data.id_card)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="该身份证号已存在")

    credit_score = 600
    risk_level = "medium"

    if customer_data.monthly_income and customer_data.monthly_income >= 20000:
        credit_score += 30
    if customer_data.education in ["博士", "硕士", "研究生", "本科"]:
        credit_score += 20
    if customer_data.has_house:
        credit_score += 30
    if customer_data.has_car:
        credit_score += 15
    if customer_data.work_years and customer_data.work_years >= 5:
        credit_score += 20

    if credit_score >= 750:
        risk_level = "low"
    elif credit_score >= 650:
        risk_level = "medium_low"
    elif credit_score >= 550:
        risk_level = "medium"
    elif credit_score >= 450:
        risk_level = "medium_high"
    else:
        risk_level = "high"

    customer = Customer(
        **customer_data.model_dump(),
        credit_score=credit_score,
        risk_level=risk_level
    )

    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    return APIResponse(code=201, message="创建成功", data=CustomerResponse.model_validate(customer))


@router.put("/{customer_id}", response_model=APIResponse[CustomerResponse])
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    update_data = customer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)

    credit_score = 600
    if customer.monthly_income and customer.monthly_income >= 20000:
        credit_score += 30
    if customer.education in ["博士", "硕士", "研究生", "本科"]:
        credit_score += 20
    if customer.has_house:
        credit_score += 30
    if customer.has_car:
        credit_score += 15
    if customer.work_years and customer.work_years >= 5:
        credit_score += 20

    customer.credit_score = credit_score
    if credit_score >= 750:
        customer.risk_level = "low"
    elif credit_score >= 650:
        customer.risk_level = "medium_low"
    elif credit_score >= 550:
        customer.risk_level = "medium"
    elif credit_score >= 450:
        customer.risk_level = "medium_high"
    else:
        customer.risk_level = "high"

    await db.commit()
    await db.refresh(customer)

    return APIResponse(code=200, message="更新成功", data=CustomerResponse.model_validate(customer))


@router.delete("/{customer_id}", response_model=APIResponse)
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="无权限删除客户")

    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    await db.delete(customer)
    await db.commit()

    return APIResponse(code=200, message="删除成功")
