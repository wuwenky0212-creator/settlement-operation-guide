"""Accounting record schemas"""
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.enums import DebitCreditIndicator


class AccountingRecordBase(BaseModel):
    """Base accounting record schema"""
    voucher_id: str = Field(..., description='传票号')
    transaction_id: str = Field(..., description='交易流水号')
    
    actual_accounting_date: datetime = Field(..., description='实际记账日')
    planned_accounting_date: datetime = Field(..., description='计划记账日')
    
    event_number: str = Field(..., description='事件号')
    
    debit_credit_indicator: DebitCreditIndicator = Field(..., description='借贷方向')
    currency: str = Field(..., description='货币')
    account_subject: str = Field(..., description='科目')
    transaction_amount: float = Field(..., description='交易金额')
    
    class Config:
        from_attributes = True


class AccountingRecordCreate(AccountingRecordBase):
    """Schema for creating an accounting record"""
    pass


class AccountingRecordResponse(AccountingRecordBase):
    """Accounting record response"""
    pass


class PaymentInfo(BaseModel):
    """Payment information"""
    # 清算方式
    our_bank_name: str = Field(..., description='我行开户行')
    our_bank_code: str = Field(..., description='我行开户行号')
    our_account_name: str = Field(..., description='我行户名')
    our_account_number: str = Field(..., description='我行账号')
    
    counterparty_bank_name: str = Field(..., description='对手开户行')
    counterparty_bank_code: str = Field(..., description='对手开户行号')
    counterparty_account_name: str = Field(..., description='对手户名')
    counterparty_account_number: str = Field(..., description='对手账号')
    
    # 支付信息
    instruction_id: str = Field(..., description='指令ID')
    payment_date: datetime = Field(..., description='支付日期')
    message_type: str = Field(..., description='报文类型')
    currency: str = Field(..., description='币种')
    amount: float = Field(..., description='金额')
    message_sender: str = Field(..., description='报文发送人')
    message_send_time: datetime = Field(..., description='报文发送时间')
