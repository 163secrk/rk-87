from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from typing import Optional, Tuple, List
from app.models.loan_application import LoanApplication, LoanStatus
from app.models.approval_record import ApprovalRecord, ApprovalAction
from app.models.user import User, UserRole
from app.models.customer import Customer
from .risk_assessment import RiskAssessmentService


class ApprovalService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.risk_service = RiskAssessmentService(db)

    async def _generate_application_no(self) -> str:
        today = datetime.now().strftime("%Y%m%d")
        result = await self.db.execute(
            select(func.count(LoanApplication.id)).where(
                func.date(LoanApplication.created_at) == func.date(func.now())
            )
        )
        count = result.scalar() or 0
        return f"JD{today}{count + 1:06d}"

    async def create_application(
        self,
        customer: Customer,
        application_data: dict,
        current_user: User
    ) -> Tuple[LoanApplication, List[ApprovalRecord]]:
        application_no = await self._generate_application_no()

        application = LoanApplication(
            application_no=application_no,
            customer_id=customer.id,
            loan_type=application_data["loan_type"],
            loan_amount=application_data["loan_amount"],
            loan_term=application_data["loan_term"],
            interest_rate=application_data["interest_rate"],
            repayment_method=application_data.get("repayment_method"),
            purpose=application_data.get("purpose"),
            remark=application_data.get("remark"),
            status=LoanStatus.PENDING,
            created_by=current_user.id
        )

        self.db.add(application)
        await self.db.flush()

        records = []

        submit_record = ApprovalRecord(
            loan_application_id=application.id,
            action=ApprovalAction.SUBMIT,
            operator_id=current_user.id,
            operator_name=current_user.full_name,
            operator_role=current_user.role,
            comment="提交贷款申请"
        )
        records.append(submit_record)

        assessment_result = await self.risk_service.assess_risk(customer, application)

        application.risk_score = assessment_result.risk_score
        application.risk_level = assessment_result.risk_level
        application.auto_decision = assessment_result.auto_decision
        application.auto_decision_reason = assessment_result.auto_decision_reason

        if assessment_result.auto_decision == "approve":
            application.status = LoanStatus.AUTO_APPROVED
            auto_record = ApprovalRecord(
                loan_application_id=application.id,
                action=ApprovalAction.AUTO_APPROVE,
                operator_name="系统自动审批",
                operator_role="system",
                comment=assessment_result.auto_decision_reason,
                risk_score_before=600,
                risk_score_after=assessment_result.risk_score,
                risk_level_before="medium",
                risk_level_after=assessment_result.risk_level
            )
            records.append(auto_record)
        elif assessment_result.auto_decision == "reject":
            application.status = LoanStatus.AUTO_REJECTED
            auto_record = ApprovalRecord(
                loan_application_id=application.id,
                action=ApprovalAction.AUTO_REJECT,
                operator_name="系统自动审批",
                operator_role="system",
                comment=assessment_result.auto_decision_reason,
                risk_score_before=600,
                risk_score_after=assessment_result.risk_score,
                risk_level_before="medium",
                risk_level_after=assessment_result.risk_level
            )
            records.append(auto_record)
        else:
            application.status = LoanStatus.MANUAL_REVIEW
            auto_record = ApprovalRecord(
                loan_application_id=application.id,
                action=ApprovalAction.REVIEW,
                operator_name="系统自动审批",
                operator_role="system",
                comment=assessment_result.auto_decision_reason,
                risk_score_before=600,
                risk_score_after=assessment_result.risk_score,
                risk_level_before="medium",
                risk_level_after=assessment_result.risk_level
            )
            records.append(auto_record)

        for record in records:
            self.db.add(record)

        await self.db.commit()
        await self.db.refresh(application)

        return application, records

    async def manual_review(
        self,
        application_id: int,
        action: ApprovalAction,
        comment: str,
        current_user: User
    ) -> Optional[LoanApplication]:
        result = await self.db.execute(
            select(LoanApplication).where(LoanApplication.id == application_id)
        )
        application = result.scalar_one_or_none()
        if not application:
            return None

        old_score = application.risk_score
        old_level = application.risk_level

        record = ApprovalRecord(
            loan_application_id=application.id,
            action=action,
            operator_id=current_user.id,
            operator_name=current_user.full_name,
            operator_role=current_user.role,
            comment=comment,
            risk_score_before=old_score,
            risk_score_after=old_score,
            risk_level_before=old_level,
            risk_level_after=old_level
        )

        if action == ApprovalAction.APPROVE:
            application.status = LoanStatus.APPROVED
            application.final_decision = "approved"
            application.final_decision_reason = comment
            application.approver_id = current_user.id
            application.approver_name = current_user.full_name
            application.approved_at = datetime.now()
        elif action == ApprovalAction.REJECT:
            application.status = LoanStatus.REJECTED
            application.final_decision = "rejected"
            application.final_decision_reason = comment
            application.approver_id = current_user.id
            application.approver_name = current_user.full_name
            application.approved_at = datetime.now()
        elif action == ApprovalAction.RETURN:
            application.status = LoanStatus.PENDING
            application.final_decision = None
            application.final_decision_reason = None
        elif action == ApprovalAction.CANCEL:
            application.status = LoanStatus.CANCELLED

        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(application)

        return application

    async def get_approval_records(self, application_id: int) -> List[ApprovalRecord]:
        result = await self.db.execute(
            select(ApprovalRecord)
            .where(ApprovalRecord.loan_application_id == application_id)
            .order_by(ApprovalRecord.created_at)
        )
        return result.scalars().all()
