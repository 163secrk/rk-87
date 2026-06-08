from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from app.models.loan_application import LoanApplication, LoanStatus
from app.models.customer import Customer
from app.models.user import User
from app.models.approval_record import ApprovalRecord
from app.models.risk_rule import RiskRule
from app.models.blacklist import Blacklist


class CreditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_stats(self) -> Dict:
        today = datetime.now().date()
        thirty_days_ago = today - timedelta(days=30)

        total_applications = await self.db.execute(
            select(func.count(LoanApplication.id))
        )
        total_applications = total_applications.scalar() or 0

        total_amount = await self.db.execute(
            select(func.sum(LoanApplication.loan_amount))
        )
        total_amount = total_amount.scalar() or 0

        pending_count = await self.db.execute(
            select(func.count(LoanApplication.id)).where(
                LoanApplication.status.in_([
                    LoanStatus.PENDING,
                    LoanStatus.REVIEWING,
                    LoanStatus.MANUAL_REVIEW
                ])
            )
        )
        pending_count = pending_count.scalar() or 0

        approved_count = await self.db.execute(
            select(func.count(LoanApplication.id)).where(
                LoanApplication.status.in_([
                    LoanStatus.APPROVED,
                    LoanStatus.AUTO_APPROVED
                ])
            )
        )
        approved_count = approved_count.scalar() or 0

        rejected_count = await self.db.execute(
            select(func.count(LoanApplication.id)).where(
                LoanApplication.status.in_([
                    LoanStatus.REJECTED,
                    LoanStatus.AUTO_REJECTED
                ])
            )
        )
        rejected_count = rejected_count.scalar() or 0

        approved_amount = await self.db.execute(
            select(func.sum(LoanApplication.loan_amount)).where(
                LoanApplication.status.in_([
                    LoanStatus.APPROVED,
                    LoanStatus.AUTO_APPROVED
                ])
            )
        )
        approved_amount = approved_amount.scalar() or 0

        today_applications = await self.db.execute(
            select(func.count(LoanApplication.id)).where(
                func.date(LoanApplication.created_at) == today
            )
        )
        today_applications = today_applications.scalar() or 0

        blacklist_count = await self.db.execute(
            select(func.count(Blacklist.id)).where(
                Blacklist.is_active == True
            )
        )
        blacklist_count = blacklist_count.scalar() or 0

        pass_rate = approved_count / total_applications * 100 if total_applications > 0 else 0

        risk_distribution = {
            "low": 0,
            "medium_low": 0,
            "medium": 0,
            "medium_high": 0,
            "high": 0,
            "extreme_high": 0
        }

        risk_result = await self.db.execute(
            select(
                LoanApplication.risk_level,
                func.count(LoanApplication.id)
            )
            .group_by(LoanApplication.risk_level)
        )
        for level, count in risk_result.all():
            if level in risk_distribution:
                risk_distribution[level] = count

        return {
            "total_applications": total_applications,
            "total_amount": float(total_amount),
            "pending_count": pending_count,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "approved_amount": float(approved_amount),
            "today_applications": today_applications,
            "blacklist_count": blacklist_count,
            "pass_rate": round(pass_rate, 2),
            "risk_distribution": risk_distribution
        }

    async def get_trend_data(self, days: int = 30) -> List[Dict]:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        trend_data = []

        for i in range(days):
            current_date = start_date + timedelta(days=i)

            daily_stats = await self.db.execute(
                select(
                    func.count(LoanApplication.id).label("count"),
                    func.sum(LoanApplication.loan_amount).label("amount")
                ).where(
                    func.date(LoanApplication.created_at) == current_date
                )
            )
            count, amount = daily_stats.one()

            approved_stats = await self.db.execute(
                select(
                    func.count(LoanApplication.id)
                ).where(
                    func.date(LoanApplication.created_at) == current_date,
                    LoanApplication.status.in_([
                        LoanStatus.APPROVED,
                        LoanStatus.AUTO_APPROVED
                    ])
                )
            )
            approved = approved_stats.scalar() or 0

            rejected_stats = await self.db.execute(
                select(
                    func.count(LoanApplication.id)
                ).where(
                    func.date(LoanApplication.created_at) == current_date,
                    LoanApplication.status.in_([
                        LoanStatus.REJECTED,
                        LoanStatus.AUTO_REJECTED
                    ])
                )
            )
            rejected = rejected_stats.scalar() or 0

            trend_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "application_count": count or 0,
                "application_amount": float(amount or 0),
                "approved_count": approved,
                "rejected_count": rejected
            })

        return trend_data

    async def get_loan_type_distribution(self) -> List[Dict]:
        result = await self.db.execute(
            select(
                LoanApplication.loan_type,
                func.count(LoanApplication.id).label("count"),
                func.sum(LoanApplication.loan_amount).label("amount")
            )
            .group_by(LoanApplication.loan_type)
        )

        distribution = []
        for loan_type, count, amount in result.all():
            distribution.append({
                "loan_type": loan_type,
                "count": count,
                "amount": float(amount or 0)
            })

        return distribution
