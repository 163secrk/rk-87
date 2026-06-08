from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.models.blacklist import Blacklist
from app.schemas.blacklist import BlacklistCreate, BlacklistUpdate, BlacklistResponse
from app.schemas.common import APIResponse, PaginatedResponse

router = APIRouter(prefix="/blacklist", tags=["黑名单"])


@router.get("", response_model=PaginatedResponse[BlacklistResponse])
async def get_blacklist(
    page: int = 1,
    page_size: int = 20,
    keyword: str = None,
    blacklist_type: str = None,
    is_active: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = select(Blacklist)
    count_query = select(func.count(Blacklist.id))

    if keyword:
        keyword_filter = (
            Blacklist.name.contains(keyword) |
            Blacklist.id_card.contains(keyword) |
            Blacklist.phone.contains(keyword)
        )
        query = query.where(keyword_filter)
        count_query = count_query.where(keyword_filter)

    if blacklist_type:
        query = query.where(Blacklist.blacklist_type == blacklist_type)
        count_query = count_query.where(Blacklist.blacklist_type == blacklist_type)

    if is_active is not None:
        query = query.where(Blacklist.is_active == is_active)
        count_query = count_query.where(Blacklist.is_active == is_active)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Blacklist.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        code=200,
        message="success",
        data={
            "items": [BlacklistResponse.model_validate(i) for i in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    )


@router.get("/check/{id_card}", response_model=APIResponse[bool])
async def check_blacklist(
    id_card: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(Blacklist).where(
            Blacklist.id_card == id_card,
            Blacklist.is_active == True
        )
    )
    exists = result.scalar_one_or_none() is not None
    return APIResponse(code=200, message="success", data=exists)


@router.get("/{item_id}", response_model=APIResponse[BlacklistResponse])
async def get_blacklist_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Blacklist).where(Blacklist.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="记录不存在")
    return APIResponse(code=200, message="success", data=BlacklistResponse.model_validate(item))


@router.post("", response_model=APIResponse[BlacklistResponse])
async def add_to_blacklist(
    item_data: BlacklistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="无权限操作")

    result = await db.execute(
        select(Blacklist).where(
            Blacklist.id_card == item_data.id_card,
            Blacklist.is_active == True
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="该身份证号已在黑名单中")

    item = Blacklist(
        **item_data.model_dump(),
        added_by=current_user.id
    )

    db.add(item)
    await db.commit()
    await db.refresh(item)

    return APIResponse(code=201, message="添加成功", data=BlacklistResponse.model_validate(item))


@router.put("/{item_id}", response_model=APIResponse[BlacklistResponse])
async def update_blacklist(
    item_id: int,
    item_data: BlacklistUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="无权限操作")

    result = await db.execute(select(Blacklist).where(Blacklist.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="记录不存在")

    update_data = item_data.model_dump(exclude_unset=True)

    if "is_active" in update_data and update_data["is_active"] == False and item.is_active:
        item.removed_by = current_user.id
        item.removed_at = datetime.now()

    for field, value in update_data.items():
        setattr(item, field, value)

    await db.commit()
    await db.refresh(item)

    return APIResponse(code=200, message="更新成功", data=BlacklistResponse.model_validate(item))


@router.post("/{item_id}/remove", response_model=APIResponse)
async def remove_from_blacklist(
    item_id: int,
    reason: str = "",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="无权限操作")

    result = await db.execute(select(Blacklist).where(Blacklist.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="记录不存在")

    item.is_active = False
    item.removed_by = current_user.id
    item.removed_at = datetime.now()
    if reason:
        item.remark = (item.remark or "") + f"\n移除原因: {reason}"

    await db.commit()

    return APIResponse(code=200, message="移除成功")
