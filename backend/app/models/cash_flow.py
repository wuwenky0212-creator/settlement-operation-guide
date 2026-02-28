"""Cash flow model"""
from sqlalchemy import Column, String, DateTime, Float, Integer, Index, ForeignKey
from sqlalchemy import Enum as SQLEnum
from app.database import Base
from app.models.enums import SettlementMethod, CashFlowStatus, Direction


class CashFlow(Base):
    """现金流表"""
    __tablename__ = 'cash_flows'
    
    # 主键
    cash_flow_id = Column(String(100), primary_key=True, comment='现金流内部ID')
    
    # 关联信息
    transaction_id = Column(String(100), ForeignKey('transactions.transaction_id'), nullable=False, index=True, comment='交易流水号')
    payment_info_id = Column(String(100), nullable=True, index=True, comment='收付信息ID')
    settlement_id = Column(String(100), nullable=True, index=True, comment='结算内部ID')
    
    # 现金流详情
    direction = Column(SQLEnum(Direction), nullable=False, index=True, comment='方向')
    currency = Column(String(3), nullable=False, index=True, comment='币种')
    amount = Column(Float, nullable=False, comment='金额')
    payment_date = Column(DateTime, nullable=False, index=True, comment='收付日期')
    
    # 账号信息
    account_number = Column(String(100), nullable=False, comment='账号')
    account_name = Column(String(200), nullable=False, comment='户名')
    bank_name = Column(String(200), nullable=False, comment='开户行')
    bank_code = Column(String(50), nullable=False, comment='开户行号')
    
    # 结算信息
    settlement_method = Column(SQLEnum(SettlementMethod), nullable=False, index=True, comment='结算方式')
    
    # 状态信息
    current_status = Column(SQLEnum(CashFlowStatus), nullable=False, index=True, comment='当前状态')
    progress_percentage = Column(Integer, nullable=False, default=0, comment='进度百分比')
    
    # 并发控制
    version = Column(Integer, nullable=False, default=1, comment='版本号')
    last_modified_date = Column(DateTime, nullable=False, comment='最后修改日期')
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_transaction_id_direction', 'transaction_id', 'direction'),
        Index('idx_payment_date_status', 'payment_date', 'current_status'),
        Index('idx_currency_direction', 'currency', 'direction'),
    )
