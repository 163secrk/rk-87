from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class RuleConditionOperator(str, enum.Enum):
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    EQ = "eq"
    NEQ = "neq"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"


class RuleAction(str, enum.Enum):
    SCORE_PLUS = "score_plus"
    SCORE_MINUS = "score_minus"
    SET_SCORE = "set_score"
    AUTO_REJECT = "auto_reject"
    AUTO_APPROVE = "auto_approve"
    MANUAL_REVIEW = "manual_review"
    SET_RISK_LEVEL = "set_risk_level"


class RiskRule(Base):
    __tablename__ = "risk_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_code = Column(String(50), unique=True, index=True, nullable=False)
    rule_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    priority = Column(Integer, default=0)
    condition_field = Column(String(100), nullable=False)
    condition_operator = Column(Enum(RuleConditionOperator), nullable=False)
    condition_value = Column(String(255), nullable=False)
    action = Column(Enum(RuleAction), nullable=False)
    action_value = Column(String(255), nullable=True)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
