"""Transaction model"""
from sqlalchemy import Column, String, DateTime, Integer, Enum as SQLEnum, Index
from sqlalchemy.sql import func
from app.database import Base
from app.models.enums import (
    ProductType, TransactionStatus, BackOfficeStatus,
    SettlementMethod, ConfirmationType, TransactionSource,
    MatchStatus, Direction
)


class Transaction(Base):
    """交易表"""
    __tablename__ = 'transactions'
    
    # 标识信息
    external_id = Column(String(100), primary_key=True, comment='外部流水号')
    transaction_id = Column(String(100), unique=True, nullable=False, index=True, comment='交易流水号')
    parent_transaction_id = Column(String(100), nullable=True, index=True, comment='父交易流水号')
    
    # 基本信息
    entry_date = Column(DateTime, nullable=False, comment='录入日')
    trade_date = Column(DateTime, nullable=False, index=True, comment='交易日')
    value_date = Column(DateTime, nullable=False, index=True, comment='起息日')
    maturity_date = Column(DateTime, nullable=False, index=True, comment='到期日')
    
    # 交易详情
    account = Column(String(100), nullable=False, comment='账户')
    product = Column(SQLEnum(ProductType), nullable=False, index=True, comment='产品类型')
    direction = Column(SQLEnum(Direction), nullable=False, comment='买卖方向')
    underlying = Column(String(200), nullable=False, comment='标的物')
    counterparty = Column(String(200), nullable=False, index=True, comment='交易对手')
    
    # 状态信息
    status = Column(SQLEnum(TransactionStatus), nullable=False, index=True, comment='交易状态')
    back_office_status = Column(SQLEnum(BackOfficeStatus), nullable=False, index=True, comment='后线处理状态')
    
    # 清算证实信息
    settlement_method = Column(SQLEnum(SettlementMethod), nullable=False, index=True, comment='清算方式')
    confirmation_number = Column(String(100), nullable=True, comment='证实编号')
    confirmation_type = Column(SQLEnum(ConfirmationType), nullable=False, index=True, comment='证实方式')
    confirmation_match_type = Column(String(50), nullable=True, comment='证实匹配方式')
    confirmation_match_status = Column(SQLEnum(MatchStatus), nullable=True, index=True, comment='证实匹配状态')
    
    # 其他信息
    nature = Column(String(100), nullable=False, comment='交易性质')
    source = Column(SQLEnum(TransactionSource), nullable=False, index=True, comment='交易来源')
    latest_event_type = Column(String(50), nullable=True, comment='最新事件类型')
    operating_institution = Column(String(200), nullable=False, index=True, comment='运营机构')
    business_institution = Column(String(200), nullable=True, comment='业务机构')
    trader = Column(String(100), nullable=False, comment='交易员')
    
    # 并发控制
    version = Column(Integer, nullable=False, default=1, comment='版本号（乐观锁）')
    last_modified_date = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment='最后修改日期')
    last_modified_by = Column(String(100), nullable=False, comment='最后修改人')
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_trade_date_status', 'trade_date', 'status'),
        Index('idx_counterparty_product', 'counterparty', 'product'),
        Index('idx_operating_institution_trade_date', 'operating_institution', 'trade_date'),
    )
