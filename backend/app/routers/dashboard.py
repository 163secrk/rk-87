from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.credit_service import CreditService

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/stats", response_model=APIResponse[dict])
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = CreditService(db)
    stats = await service.get_dashboard_stats()
    return APIResponse(code=200, message="success", data=stats)


@router.get("/trend", response_model=APIResponse[list])
async def get_trend_data(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = CreditService(db)
    data = await service.get_trend_data(days)
    return APIResponse(code=200, message="success", data=data)


@router.get("/loan-type-distribution", response_model=APIResponse[list])
async def get_loan_type_distribution(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = CreditService(db)
    data = await service.get_loan_type_distribution()
    return APIResponse(code=200, message="success", data=data)
