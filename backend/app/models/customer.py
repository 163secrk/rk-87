from sqlalchemy import Column, Integer, String, DateTime, Date, Float, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    id_card = Column(String(18), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    gender = Column(String(10), nullable=True)
    birth_date = Column(Date, nullable=True)
    marital_status = Column(String(20), nullable=True)
    education = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    work_unit = Column(String(100), nullable=True)
    position = Column(String(50), nullable=True)
    monthly_income = Column(Float, default=0.0)
    total_assets = Column(Float, default=0.0)
    total_liabilities = Column(Float, default=0.0)
    credit_score = Column(Integer, default=0)
    risk_level = Column(String(20), default="medium")
    work_years = Column(Integer, default=0)
    has_house = Column(Boolean, default=False)
    has_car = Column(Boolean, default=False)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
