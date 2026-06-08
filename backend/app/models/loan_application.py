from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class LoanStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWING = "reviewing"
    AUTO_APPROVED = "auto_approved"
    AUTO_REJECTED = "auto_rejected"
    MANUAL_REVIEW = "manual_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LoanType(str, enum.Enum):
    PERSONAL = "personal"
    BUSINESS = "business"
    MORTGAGE = "mortgage"
    CAR = "car"
    CONSUMER = "consumer"


class RepaymentMethod(str, enum.Enum):
    EQUAL_PRINCIPAL_INTEREST = "equal_principal_interest"
    EQUAL_PRINCIPAL = "equal_principal"
    BULLET_REPAYMENT = "bullet_repayment"
    INTEREST_FIRST = "interest_first"


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    application_no = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    loan_type = Column(Enum(LoanType), nullable=False)
    loan_amount = Column(Float, nullable=False)
    loan_term = Column(Integer, nullable=False)
    interest_rate = Column(Float, nullable=False)
    repayment_method = Column(Enum(RepaymentMethod), default=RepaymentMethod.EQUAL_PRINCIPAL_INTEREST)
    purpose = Column(String(255), nullable=True)
    status = Column(Enum(LoanStatus), default=LoanStatus.PENDING)
    risk_score = Column(Integer, default=0)
    risk_level = Column(String(20), default="medium")
    auto_decision = Column(String(20), nullable=True)
    auto_decision_reason = Column(Text, nullable=True)
    final_decision = Column(String(20), nullable=True)
    final_decision_reason = Column(Text, nullable=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewer_name = Column(String(50), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approver_name = Column(String(50), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    remark = Column(Text, nullable=True)

    customer = relationship("Customer", foreign_keys=[customer_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    approver = relationship("User", foreign_keys=[approver_id])
