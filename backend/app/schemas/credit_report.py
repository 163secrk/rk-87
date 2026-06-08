from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CreditReportBase(BaseModel):
    customer_id: int = Field(..., description="客户ID")
    report_no: Optional[str] = Field(None, max_length=50, description="报告编号")
    report_source: Optional[str] = Field("manual", max_length=50, description="报告来源")
    credit_score: int = Field(default=0, description="信用评分")
    credit_level: Optional[str] = Field(None, max_length=20, description="信用等级")
    total_loan_count: int = Field(default=0, description="贷款总笔数")
    total_loan_amount: Optional[float] = Field(None, description="贷款总金额")
    current_loan_count: int = Field(default=0, description="当前贷款笔数")
    current_loan_balance: float = Field(default=0.0, description="当前贷款余额")
    overdue_count: int = Field(default=0, description="逾期次数")
    overdue_amount: float = Field(default=0.0, description="逾期金额")
    max_overdue_days: int = Field(default=0, description="最大逾期天数")
    query_count_last_30d: Optional[int] = Field(None, description="近30天查询次数")
    query_count_last_90d: int = Field(default=0, description="近90天查询次数")
    query_count_last_180d: int = Field(default=0, description="近180天查询次数")
    public_records: Optional[str] = Field(None, description="公共记录")
    credit_card_info: Optional[str] = Field(None, description="信用卡信息")
    guarantee_info: Optional[str] = Field(None, description="担保信息")
    risk_tags: Optional[str] = Field(None, max_length=255, description="风险标签")
    report_data: Optional[str] = Field(None, description="报告原始数据")
    remark: Optional[str] = Field(None, description="备注")
    total_debt: Optional[float] = Field(None, description="负债总额")
    query_count: Optional[int] = Field(None, description="查询次数")
    report_detail: Optional[str] = Field(None, description="报告详情")


class CreditReportCreate(CreditReportBase):
    pass


class CreditReportResponse(CreditReportBase):
    id: int
    queried_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    customer_name: Optional[str] = None
    id_card: Optional[str] = None
    report_date: Optional[datetime] = None

    class Config:
        from_attributes = True
