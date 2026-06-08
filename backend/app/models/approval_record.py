from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ApprovalAction(str, enum.Enum):
    SUBMIT = "submit"
    AUTO_APPROVE = "auto_approve"
    AUTO_REJECT = "auto_reject"
    REVIEW = "review"
    APPROVE = "approve"
    REJECT = "reject"
    RETURN = "return"
    CANCEL = "cancel"


class ApprovalRecord(Base):
    __tablename__ = "approval_records"

    id = Column(Integer, primary_key=True, index=True)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False)
    action = Column(Enum(ApprovalAction), nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    operator_name = Column(String(50), nullable=True)
    operator_role = Column(String(20), nullable=True)
    comment = Column(Text, nullable=True)
    risk_score_before = Column(Integer, nullable=True)
    risk_score_after = Column(Integer, nullable=True)
    risk_level_before = Column(String(20), nullable=True)
    risk_level_after = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    loan_application = relationship("LoanApplication")
    operator = relationship("User")
