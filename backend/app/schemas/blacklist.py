from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class BlacklistBase(BaseModel):
    name: str = Field(..., max_length=50, description="姓名")
    id_card: str = Field(..., max_length=18, description="身份证号")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    blacklist_type: str = Field(..., max_length=50, description="黑名单类型")
    reason: str = Field(..., description="拉黑原因")
    source: Optional[str] = Field(None, max_length=100, description="来源")
    customer_id: Optional[int] = Field(None, description="关联客户ID")
    remark: Optional[str] = Field(None, description="备注")


class BlacklistCreate(BlacklistBase):
    pass


class BlacklistUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    blacklist_type: Optional[str] = None
    reason: Optional[str] = None
    source: Optional[str] = None
    is_active: Optional[bool] = None
    remark: Optional[str] = None


class BlacklistResponse(BlacklistBase):
    id: int
    is_active: bool
    added_by: Optional[int] = None
    added_at: datetime
    removed_by: Optional[int] = None
    removed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
