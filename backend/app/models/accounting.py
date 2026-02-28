"""Accounting record model"""
from sqlalchemy import Column, String, DateTime, Float, Index, ForeignKey
from sqlalchemy import Enum as SQLEnum
from app.database import Base
from app.models.enums import DebitCreditIndicator


class AccountingRecord(Base):
    """账务记录表"""
    __tablename__ = 'accounting_records'
    
    # 主键
    voucher_id = Column(String(100), primary_key=True, comment='传票号')
    
    # 关联信息
    transaction_id = Column(String(100), ForeignKey('transactions.transaction_id'), nullable=False, index=True, comment='交易流水号')
    
    # 日期信息
    actual_accounting_date = Column(DateTime, nullable=False, index=True, comment='实际记账日')
    planned_accounting_date = Column(DateTime, nullable=False, comment='计划记账日')
    
    # 事件信息
    event_number = Column(String(100), nullable=False, comment='事件号')
    
    # 账务详情
    debit_credit_indicator = Column(SQLEnum(DebitCreditIndicator), nullable=False, comment='借贷方向')
    currency = Column(String(3), nullable=False, index=True, comment='货币')
    account_subject = Column(String(100), nullable=False, comment='科目')
    transaction_amount = Column(Float, nullable=False, comment='交易金额')
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_transaction_id_accounting_date', 'transaction_id', 'actual_accounting_date'),
        Index('idx_currency_debit_credit', 'currency', 'debit_credit_indicator'),
    )
