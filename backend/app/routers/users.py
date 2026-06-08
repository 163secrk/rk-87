from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import get_current_active_user, get_password_hash
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import APIResponse, PaginatedResponse

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("", response_model=PaginatedResponse[UserResponse])
async def get_users(
    page: int = 1,
    page_size: int = 20,
    role: UserRole = None,
    keyword: str = None,
    name: str = None,
    status: str = None,
    username: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = select(User)
    count_query = select(func.count(User.id))

    if role:
        query = query.where(User.role == role)
        count_query = count_query.where(User.role == role)

    if keyword:
        keyword_filter = (
            User.username.contains(keyword) |
            User.full_name.contains(keyword) |
            User.phone.contains(keyword)
        )
        query = query.where(keyword_filter)
        count_query = count_query.where(keyword_filter)

    if username:
        query = query.where(User.username.contains(username))
        count_query = count_query.where(User.username.contains(username))

    if name:
        query = query.where(User.full_name.contains(name))
        count_query = count_query.where(User.full_name.contains(name))

    if status is not None:
        is_active = status == "active"
        query = query.where(User.is_active == is_active)
        count_query = count_query.where(User.is_active == is_active)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()

    response_items = []
    for u in users:
        user_dict = UserResponse.model_validate(u).model_dump()
        user_dict["name"] = u.full_name
        user_dict["status"] = "active" if u.is_active else "inactive"
        response_items.append(UserResponse(**user_dict))

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


@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user_response_dict = UserResponse.model_validate(user).model_dump()
    user_response_dict["name"] = user.full_name
    user_response_dict["status"] = "active" if user.is_active else "inactive"

    return APIResponse(code=200, message="success", data=UserResponse(**user_response_dict))


@router.post("", response_model=APIResponse[UserResponse])
async def create_user(
    user_data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="无权限创建用户")

    user_dict = user_data.copy()
    if "name" in user_dict:
        user_dict["full_name"] = user_dict.pop("name")
    if "status" in user_dict:
        user_dict["is_active"] = user_dict.pop("status") == "active"

    user_create = UserCreate(**user_dict)

    result = await db.execute(
        select(User).where(
            (User.username == user_create.username) |
            (User.email == user_create.email)
        )
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")

    user = User(
        username=user_create.username,
        email=user_create.email,
        full_name=user_create.full_name,
        phone=user_create.phone,
        role=user_create.role,
        department=user_create.department,
        is_active=user_dict.get("is_active", True),
        password_hash=get_password_hash(user_create.password)
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    user_response_dict = UserResponse.model_validate(user).model_dump()
    user_response_dict["name"] = user.full_name
    user_response_dict["status"] = "active" if user.is_active else "inactive"

    return APIResponse(code=201, message="创建成功", data=UserResponse(**user_response_dict))


@router.put("/{user_id}", response_model=APIResponse[UserResponse])
async def update_user(
    user_id: int,
    user_data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="无权限修改此用户")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user_dict = user_data.copy()
    if "name" in user_dict:
        user_dict["full_name"] = user_dict.pop("name")
    if "status" in user_dict:
        user_dict["is_active"] = user_dict.pop("status") == "active"

    user_update = UserUpdate(**user_dict)

    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    user_response_dict = UserResponse.model_validate(user).model_dump()
    user_response_dict["name"] = user.full_name
    user_response_dict["status"] = "active" if user.is_active else "inactive"

    return APIResponse(code=200, message="更新成功", data=UserResponse(**user_response_dict))


@router.delete("/{user_id}", response_model=APIResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="无权限删除用户")

    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.is_active = False
    await db.commit()

    return APIResponse(code=200, message="删除成功")
