from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.models.risk_rule import RiskRule
from app.schemas.risk_rule import RiskRuleCreate, RiskRuleUpdate, RiskRuleResponse
from app.schemas.common import APIResponse, PaginatedResponse

router = APIRouter(prefix="/risk-rules", tags=["风控规则"])


@router.get("", response_model=PaginatedResponse[RiskRuleResponse])
async def get_risk_rules(
    page: int = 1,
    page_size: int = 50,
    category: str = None,
    is_enabled: bool = None,
    keyword: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = select(RiskRule)
    count_query = select(func.count(RiskRule.id))

    if category:
        query = query.where(RiskRule.category == category)
        count_query = count_query.where(RiskRule.category == category)

    if is_enabled is not None:
        query = query.where(RiskRule.is_enabled == is_enabled)
        count_query = count_query.where(RiskRule.is_enabled == is_enabled)

    if keyword:
        keyword_filter = (
            RiskRule.rule_code.contains(keyword) |
            RiskRule.rule_name.contains(keyword) |
            RiskRule.description.contains(keyword)
        )
        query = query.where(keyword_filter)
        count_query = count_query.where(keyword_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(RiskRule.priority, RiskRule.id).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rules = result.scalars().all()

    return PaginatedResponse(
        code=200,
        message="success",
        data={
            "items": [RiskRuleResponse.model_validate(r) for r in rules],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    )


@router.get("/all", response_model=APIResponse[List[RiskRuleResponse]])
async def get_all_risk_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(RiskRule).where(RiskRule.is_enabled == True).order_by(RiskRule.priority, RiskRule.id)
    )
    rules = result.scalars().all()
    return APIResponse(
        code=200,
        message="success",
        data=[RiskRuleResponse.model_validate(r) for r in rules]
    )


@router.get("/{rule_id}", response_model=APIResponse[RiskRuleResponse])
async def get_risk_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(RiskRule).where(RiskRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    return APIResponse(code=200, message="success", data=RiskRuleResponse.model_validate(rule))


@router.post("", response_model=APIResponse[RiskRuleResponse])
async def create_risk_rule(
    rule_data: RiskRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="无权限创建规则")

    result = await db.execute(
        select(RiskRule).where(RiskRule.rule_code == rule_data.rule_code)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="规则编码已存在")

    rule = RiskRule(**rule_data.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)

    return APIResponse(code=201, message="创建成功", data=RiskRuleResponse.model_validate(rule))


@router.put("/{rule_id}", response_model=APIResponse[RiskRuleResponse])
async def update_risk_rule(
    rule_id: int,
    rule_data: RiskRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="无权限修改规则")

    result = await db.execute(select(RiskRule).where(RiskRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    update_data = rule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    await db.commit()
    await db.refresh(rule)

    return APIResponse(code=200, message="更新成功", data=RiskRuleResponse.model_validate(rule))


@router.delete("/{rule_id}", response_model=APIResponse)
async def delete_risk_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="无权限删除规则")

    result = await db.execute(select(RiskRule).where(RiskRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    rule.is_enabled = False
    await db.commit()

    return APIResponse(code=200, message="删除成功")
