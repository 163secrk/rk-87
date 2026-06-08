from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.risk_rule import RuleConditionOperator, RuleAction


class RiskRuleBase(BaseModel):
    rule_code: str = Field(..., max_length=50, description="规则编码")
    rule_name: str = Field(..., max_length=100, description="规则名称")
    description: Optional[str] = Field(None, description="规则描述")
    category: Optional[str] = Field(None, max_length=50, description="规则分类")
    priority: int = Field(default=0, description="优先级")
    condition_field: str = Field(..., max_length=100, description="条件字段")
    condition_operator: RuleConditionOperator = Field(..., description="条件运算符")
    condition_value: str = Field(..., max_length=255, description="条件值")
    action: RuleAction = Field(..., description="执行动作")
    action_value: Optional[str] = Field(None, max_length=255, description="动作值")
    is_enabled: bool = Field(default=True, description="是否启用")


class RiskRuleCreate(RiskRuleBase):
    pass


class RiskRuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[int] = None
    condition_field: Optional[str] = None
    condition_operator: Optional[RuleConditionOperator] = None
    condition_value: Optional[str] = None
    action: Optional[RuleAction] = None
    action_value: Optional[str] = None
    is_enabled: Optional[bool] = None


class RiskRuleResponse(RiskRuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
