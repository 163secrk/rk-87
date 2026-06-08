from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
import re


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="客户姓名")
    id_card: str = Field(..., min_length=15, max_length=18, description="身份证号")
    phone: str = Field(..., max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    birth_date: Optional[date] = Field(None, description="出生日期")
    marital_status: Optional[str] = Field(None, max_length=20, description="婚姻状况")
    education: Optional[str] = Field(None, max_length=50, description="学历")
    address: Optional[str] = Field(None, max_length=255, description="住址")
    work_unit: Optional[str] = Field(None, max_length=100, description="工作单位")
    position: Optional[str] = Field(None, max_length=50, description="职位")
    monthly_income: Optional[float] = Field(0.0, ge=0, description="月收入")
    total_assets: Optional[float] = Field(0.0, ge=0, description="总资产")
    total_liabilities: Optional[float] = Field(0.0, ge=0, description="总负债")
    work_years: Optional[int] = Field(0, ge=0, description="工作年限")
    has_house: Optional[bool] = Field(False, description="是否有房产")
    has_car: Optional[bool] = Field(False, description="是否有车产")
    remark: Optional[str] = Field(None, description="备注")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确，应为11位有效手机号')
        return v

    @field_validator('id_card')
    @classmethod
    def validate_id_card(cls, v):
        if v and not re.match(r'(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)', v):
            raise ValueError('身份证号格式不正确')
        return v


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    marital_status: Optional[str] = None
    education: Optional[str] = None
    address: Optional[str] = None
    work_unit: Optional[str] = None
    position: Optional[str] = None
    monthly_income: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    work_years: Optional[int] = None
    has_house: Optional[bool] = None
    has_car: Optional[bool] = None
    remark: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is not None and not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确，应为11位有效手机号')
        return v


class CustomerResponse(CustomerBase):
    id: int
    credit_score: int
    risk_level: str
    age: Optional[int] = None
    is_blacklisted: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
