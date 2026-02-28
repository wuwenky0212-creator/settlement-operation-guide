"""Event record schemas"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import ProductType, TransactionStatus, BackOfficeStatus, MatchStatus


class EventRecordBase(BaseModel):
    """Base event record schema"""
    event_id: str = Field(..., description='事件ID')
    external_id: str = Field(..., description='外部流水号')
    transaction_id: str = Field(..., description='交易流水号')
    parent_transaction_id: Optional[str] = Field(None, description='父交易流水号')
    
    product: ProductType = Field(..., description='产品')
    account: str = Field(..., description='账户')
    event_type: str = Field(..., description='事件类型')
    transaction_status: TransactionStatus = Field(..., description='交易状态')
    
    entry_date: datetime = Field(..., description='录入日')
    trade_date: datetime = Field(..., description='交易日')
    modified_date: datetime = Field(..., description='修改日')
    
    back_office_status: BackOfficeStatus = Field(..., description='后线处理状态')
    confirmation_status: Optional[str] = Field(None, description='证实状态')
    confirmation_match_status: Optional[MatchStatus] = Field(None, description='证实匹配状态')
    
    operator: str = Field(..., description='操作用户')
    
    class Config:
        from_attributes = True


class EventRecordCreate(EventRecordBase):
    """Schema for creating an event record"""
    pass


class EventRecordResponse(EventRecordBase):
    """Event record response"""
    pass
