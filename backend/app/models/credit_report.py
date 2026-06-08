from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class CreditReport(Base):
    __tablename__ = "credit_reports"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    report_no = Column(String(50), unique=True, index=True, nullable=False)
    report_source = Column(String(50), nullable=False)
    credit_score = Column(Integer, default=0)
    credit_level = Column(String(20), nullable=True)
    total_loan_count = Column(Integer, default=0)
    total_loan_amount = Column(Float, default=0.0)
    current_loan_count = Column(Integer, default=0)
    current_loan_balance = Column(Float, default=0.0)
    overdue_count = Column(Integer, default=0)
    overdue_amount = Column(Float, default=0.0)
    max_overdue_days = Column(Integer, default=0)
    query_count_last_30d = Column(Integer, default=0)
    query_count_last_90d = Column(Integer, default=0)
    query_count_last_180d = Column(Integer, default=0)
    public_records = Column(Text, nullable=True)
    credit_card_info = Column(Text, nullable=True)
    guarantee_info = Column(Text, nullable=True)
    risk_tags = Column(String(255), nullable=True)
    report_data = Column(Text, nullable=True)
    queried_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    remark = Column(Text, nullable=True)

    customer = relationship("Customer")
    queried_by_user = relationship("User")
