"""Transaction schemas for API requests and responses"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import (
    ProductType, TransactionStatus, BackOfficeStatus,
    SettlementMethod, ConfirmationType, TransactionSource,
    MatchStatus, Direction
)


class TransactionBase(BaseModel):
    """Base transaction schema"""
    external_id: str = Field(..., description='外部流水号')
    transaction_id: str = Field(..., description='交易流水号')
    parent_transaction_id: Optional[str] = Field(None, description='父交易流水号')
    
    entry_date: datetime = Field(..., description='录入日')
    trade_date: datetime = Field(..., description='交易日')
    value_date: datetime = Field(..., description='起息日')
    maturity_date: datetime = Field(..., description='到期日')
    
    account: str = Field(..., description='账户')
    product: ProductType = Field(..., description='产品类型')
    direction: Direction = Field(..., description='买卖方向')
    underlying: str = Field(..., description='标的物')
    counterparty: str = Field(..., description='交易对手')
    
    status: TransactionStatus = Field(..., description='交易状态')
    back_office_status: BackOfficeStatus = Field(..., description='后线处理状态')
    
    settlement_method: SettlementMethod = Field(..., description='清算方式')
    confirmation_number: Optional[str] = Field(None, description='证实编号')
    confirmation_type: ConfirmationType = Field(..., description='证实方式')
    confirmation_match_type: Optional[str] = Field(None, description='证实匹配方式')
    confirmation_match_status: Optional[MatchStatus] = Field(None, description='证实匹配状态')
    
    nature: str = Field(..., description='交易性质')
    source: TransactionSource = Field(..., description='交易来源')
    latest_event_type: Optional[str] = Field(None, description='最新事件类型')
    operating_institution: str = Field(..., description='运营机构')
    business_institution: Optional[str] = Field(None, description='业务机构')
    trader: str = Field(..., description='交易员')
    
    version: int = Field(default=1, description='版本号')
    last_modified_date: datetime = Field(..., description='最后修改日期')
    last_modified_by: str = Field(..., description='最后修改人')
    
    class Config:
        from_attributes = True


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction"""
    pass


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction"""
    status: Optional[TransactionStatus] = None
    back_office_status: Optional[BackOfficeStatus] = None
    confirmation_number: Optional[str] = None
    confirmation_match_status: Optional[MatchStatus] = None
    latest_event_type: Optional[str] = None
    version: int = Field(..., description='当前版本号（用于乐观锁）')
    last_modified_by: str = Field(..., description='最后修改人')


class TransactionSummary(BaseModel):
    """Transaction summary for list view"""
    external_id: str
    transaction_id: str
    entry_date: datetime
    trade_date: datetime
    value_date: datetime
    maturity_date: datetime
    account: str
    product: ProductType
    direction: Direction
    underlying: str
    counterparty: str
    status: TransactionStatus
    back_office_status: BackOfficeStatus
    settlement_method: SettlementMethod
    confirmation_number: Optional[str]
    confirmation_type: ConfirmationType
    confirmation_match_type: Optional[str]
    nature: str
    source: TransactionSource
    latest_event_type: Optional[str]
    operating_institution: str
    trader: str
    
    class Config:
        from_attributes = True


class TransactionDetail(TransactionBase):
    """Detailed transaction information"""
    pass


class TransactionQueryCriteria(BaseModel):
    """Query criteria for transactions"""
    external_id: Optional[str] = Field(None, description='外部流水号')
    status: Optional[TransactionStatus] = Field(None, description='交易状态')
    trade_date_from: Optional[datetime] = Field(None, description='交易日起始')
    trade_date_to: Optional[datetime] = Field(None, description='交易日结束')
    value_date_from: Optional[datetime] = Field(None, description='起息日起始')
    value_date_to: Optional[datetime] = Field(None, description='起息日结束')
    maturity_date_from: Optional[datetime] = Field(None, description='到期日起始')
    maturity_date_to: Optional[datetime] = Field(None, description='到期日结束')
    counterparty: Optional[str] = Field(None, description='交易对手')
    product: Optional[ProductType] = Field(None, description='产品')
    currency: Optional[str] = Field(None, description='货币')
    operating_institution: Optional[str] = Field(None, description='运营机构')
    business_institution: Optional[str] = Field(None, description='业务机构')
    settlement_method: Optional[SettlementMethod] = Field(None, description='清算方式')
    confirmation_type: Optional[ConfirmationType] = Field(None, description='证实方式')
    source: Optional[TransactionSource] = Field(None, description='交易来源')
