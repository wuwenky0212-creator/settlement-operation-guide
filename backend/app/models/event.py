"""Event record model"""
from sqlalchemy import Column, String, DateTime, Index, ForeignKey
from app.database import Base
from sqlalchemy import Enum as SQLEnum
from app.models.enums import ProductType, TransactionStatus, BackOfficeStatus, MatchStatus


class EventRecord(Base):
    """事件表"""
    __tablename__ = 'events'
    
    # 主键
    event_id = Column(String(100), primary_key=True, comment='事件ID')
    
    # 关联信息
    external_id = Column(String(100), ForeignKey('transactions.external_id'), nullable=False, index=True, comment='外部流水号')
    transaction_id = Column(String(100), nullable=False, index=True, comment='交易流水号')
    parent_transaction_id = Column(String(100), nullable=True, index=True, comment='父交易流水号')
    
    # 事件详情
    product = Column(SQLEnum(ProductType), nullable=False, comment='产品')
    account = Column(String(100), nullable=False, comment='账户')
    event_type = Column(String(50), nullable=False, index=True, comment='事件类型')
    transaction_status = Column(SQLEnum(TransactionStatus), nullable=False, comment='交易状态')
    
    # 日期信息
    entry_date = Column(DateTime, nullable=False, comment='录入日')
    trade_date = Column(DateTime, nullable=False, comment='交易日')
    modified_date = Column(DateTime, nullable=False, index=True, comment='修改日')
    
    # 状态信息
    back_office_status = Column(SQLEnum(BackOfficeStatus), nullable=False, comment='后线处理状态')
    confirmation_status = Column(String(50), nullable=True, comment='证实状态')
    confirmation_match_status = Column(SQLEnum(MatchStatus), nullable=True, comment='证实匹配状态')
    
    # 操作信息
    operator = Column(String(100), nullable=False, comment='操作用户')
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_external_id_modified_date', 'external_id', 'modified_date'),
        Index('idx_transaction_id_event_type', 'transaction_id', 'event_type'),
    )
