from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Blacklist(Base):
    __tablename__ = "blacklists"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    name = Column(String(50), nullable=False)
    id_card = Column(String(18), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    blacklist_type = Column(String(50), nullable=False)
    reason = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    added_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    removed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    removed_at = Column(DateTime(timezone=True), nullable=True)
    remark = Column(Text, nullable=True)

    customer = relationship("Customer")
    added_by_user = relationship("User", foreign_keys=[added_by])
    removed_by_user = relationship("User", foreign_keys=[removed_by])
