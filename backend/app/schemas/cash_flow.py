"""Cash flow schemas"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import SettlementMethod, CashFlowStatus, Direction


class AccountInfo(BaseModel):
    """Account information"""
    account_number: str = Field(..., description='账号')
    account_name: str = Field(..., description='户名')
    bank_name: str = Field(..., description='开户行')
    bank_code: str = Field(..., description='开户行号')


class CashFlowBase(BaseModel):
    """Base cash flow schema"""
    cash_flow_id: str = Field(..., description='现金流内部ID')
    transaction_id: str = Field(..., description='交易流水号')
    payment_info_id: Optional[str] = Field(None, description='收付信息ID')
    settlement_id: Optional[str] = Field(None, description='结算内部ID')
    
    direction: Direction = Field(..., description='方向')
    currency: str = Field(..., description='币种')
    amount: float = Field(..., description='金额')
    payment_date: datetime = Field(..., description='收付日期')
    
    account_number: str = Field(..., description='账号')
    account_name: str = Field(..., description='户名')
    bank_name: str = Field(..., description='开户行')
    bank_code: str = Field(..., description='开户行号')
    
    settlement_method: SettlementMethod = Field(..., description='结算方式')
    
    current_status: CashFlowStatus = Field(..., description='当前状态')
    progress_percentage: int = Field(default=0, description='进度百分比')
    
    version: int = Field(default=1, description='版本号')
    last_modified_date: datetime = Field(..., description='最后修改日期')
    
    class Config:
        from_attributes = True


class CashFlowCreate(CashFlowBase):
    """Schema for creating a cash flow"""
    pass


class CashFlowUpdate(BaseModel):
    """Schema for updating a cash flow"""
    current_status: Optional[CashFlowStatus] = None
    progress_percentage: Optional[int] = None
    version: int = Field(..., description='当前版本号（用于乐观锁）')


class CashFlowSummary(BaseModel):
    """Cash flow summary for list view"""
    cash_flow_id: str
    transaction_id: str
    direction: Direction
    currency: str
    amount: float
    payment_date: datetime
    account_number: str
    current_status: CashFlowStatus
    progress_percentage: int
    
    class Config:
        from_attributes = True


class CashFlowDetail(CashFlowBase):
    """Detailed cash flow information"""
    pass


class CashFlowQueryCriteria(BaseModel):
    """Query criteria for cash flows"""
    transaction_id: Optional[str] = Field(None, description='交易流水号')
    cash_flow_id: Optional[str] = Field(None, description='现金流内部ID')
    payment_info_id: Optional[str] = Field(None, description='收付信息ID')
    settlement_id: Optional[str] = Field(None, description='结算内部ID')
    direction: Optional[Direction] = Field(None, description='方向')
    currency: Optional[str] = Field(None, description='币种')
    amount_min: Optional[float] = Field(None, description='最小金额')
    amount_max: Optional[float] = Field(None, description='最大金额')
    payment_date_from: Optional[datetime] = Field(None, description='收付日期起始')
    payment_date_to: Optional[datetime] = Field(None, description='收付日期结束')
    status: Optional[CashFlowStatus] = Field(None, description='状态')
