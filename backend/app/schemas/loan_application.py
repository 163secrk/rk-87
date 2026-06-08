from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.loan_application import LoanStatus, LoanType, RepaymentMethod
from app.models.approval_record import ApprovalAction


class LoanApplicationBase(BaseModel):
    customer_id: int = Field(..., description="客户ID")
    loan_type: LoanType = Field(..., description="贷款类型")
    loan_amount: float = Field(..., gt=0, description="贷款金额")
    loan_term: int = Field(..., gt=0, description="贷款期限(月)")
    interest_rate: float = Field(..., gt=0, lt=100, description="年利率(%)")
    repayment_method: RepaymentMethod = Field(
        default=RepaymentMethod.EQUAL_PRINCIPAL_INTEREST, description="还款方式"
    )
    purpose: Optional[str] = Field(None, max_length=255, description="贷款用途")
    remark: Optional[str] = Field(None, description="备注")


class LoanApplicationCreate(LoanApplicationBase):
    pass


class LoanApplicationUpdate(BaseModel):
    status: Optional[LoanStatus] = None
    final_decision: Optional[str] = None
    final_decision_reason: Optional[str] = None
    remark: Optional[str] = None


class RiskAssessmentResult(BaseModel):
    risk_score: int
    risk_level: str
    auto_decision: str
    auto_decision_reason: str
    matched_rules: List[str]
    triggered_rules: List[dict]


class LoanApplicationResponse(LoanApplicationBase):
    id: int
    application_no: str
    status: LoanStatus
    risk_score: int
    risk_level: str
    auto_decision: Optional[str] = None
    auto_decision_reason: Optional[str] = None
    final_decision: Optional[str] = None
    final_decision_reason: Optional[str] = None
    reviewer_id: Optional[int] = None
    reviewer_name: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    approver_id: Optional[int] = None
    approver_name: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoanApplicationListResponse(LoanApplicationResponse):
    customer_name: Optional[str] = None
    customer_id_card: Optional[str] = None
    customer_phone: Optional[str] = None


class ReviewRequest(BaseModel):
    action: ApprovalAction = Field(..., description="审批动作")
    comment: Optional[str] = Field("", description="审批意见")
