"""Enumeration types for the settlement operation guide system"""
from enum import Enum


class ProductType(str, Enum):
    """产品类型"""
    FX_SPOT = '外汇即期'
    FX_FORWARD = '外汇远期'
    FX_SWAP = '外汇掉期'
    INTERBANK_LENDING = '同业拆借'
    MONEY_MARKET_DEPOSIT = '货币市场存款'
    BOND_TRADING = '现券买卖'
    BUYOUT_REPO = '买断式回购'
    PLEDGE_REPO = '质押式回购'
    UNILATERAL_CASHFLOW = '单边现金流'


class TransactionStatus(str, Enum):
    """交易状态"""
    EFFECTIVE = '生效'
    MATURED = '到期'
    INVALID = '失效'


class BackOfficeStatus(str, Enum):
    """后线处理状态"""
    CONFIRMED = '已证实'
    SETTLED_PENDING_REPORT = '已清算待发报'
    REPORTED_PENDING_RECEIPT = '已发报待接收回执'
    COMPLETED = '已完成'


class SettlementMethod(str, Enum):
    """清算方式"""
    GROSS = '全额'
    NET = '净额'
    CENTRALIZED = '集中'
    NOT_REQUIRED = '无需'
    OUR_BANK_AGENT = '我行代理'
    OTHER_BANK_AGENT = '他行代理'


class ConfirmationType(str, Enum):
    """证实方式"""
    SWIFT = 'SWIFT'
    TEXT = '文本'
    NO_CONFIRMATION = '无证实'


class TransactionSource(str, Enum):
    """交易来源"""
    GIT = 'GIT'
    FXO = 'FXO'
    FXS = 'FXS'
    FXY = 'FXY'
    FXW = 'FXW'


class MatchStatus(str, Enum):
    """证实匹配状态"""
    MATCHED = '匹配成功'
    UNMATCHED = '匹配失败'
    PENDING = '等待匹配'


class CashFlowStatus(str, Enum):
    """现金流状态 - 4阶段流程"""
    # 阶段1: 清算轧差
    PENDING_NETTING = '待轧差'
    AUTO_NETTING_COMPLETE = '自动轧差完成'
    MANUAL_NETTING_COMPLETE = '手工轧差完成'
    PENDING_DISPATCH = '待发报'
    
    # 阶段2: 合规准入
    COMPLIANCE_CHECKING = '合规校验中'
    COMPLIANCE_APPROVED = '合规通过'
    COMPLIANCE_BLOCKED = '合规拦截'
    PENDING_APPROVAL = '待审批'
    APPROVAL_APPROVED = '审批通过'
    APPROVAL_REJECTED = '审批拒绝'
    ROUTE_DETERMINED = '路径已确定'
    
    # 阶段3: 结算执行与回执 - SWIFT路径
    RMC_SENDING = 'RMC发送中'
    RMC_SUCCESS = 'RMC发送成功'
    RMC_FAILED = 'RMC发送失败'
    FTM_SENDING = 'FTM发送中'
    FTM_SUCCESS = 'FTM发送成功'
    FTM_FAILED = 'FTM发送失败'
    
    # 阶段3: 结算执行与回执 - CBMNet路径
    PENDING_MANUAL_CONFIRM = '待人工确认'
    MANUAL_CONFIRM_APPROVED = '确认通过'
    MANUAL_CONFIRM_REJECTED = '确认拒绝'
    
    # 阶段3: 账务层回执（通用）
    CORE_PROCESSING = '核心入账处理中'
    CORE_SUCCESS = '结算完成'
    CORE_FAILED = '入账失败'
    CORE_UNKNOWN = '入账不明'
    
    # 阶段4: 结算撤销
    CANCEL_RMC_SENDING = '撤销RMC发送中'
    CANCEL_RMC_FAILED = '撤销RMC发送失败'
    CANCEL_FTM_SENDING = '撤销FTM发送中'
    CANCEL_FTM_FAILED = '撤销FTM发送失败'
    CANCEL_PROCESSING = '撤销处理中'
    CANCEL_SUCCESS = '撤销成功'
    CANCEL_FAILED = '撤销失败'


class Direction(str, Enum):
    """方向"""
    BUY = 'BUY'
    SELL = 'SELL'
    RECEIVE = 'RECEIVE'
    PAY = 'PAY'


class DebitCreditIndicator(str, Enum):
    """借贷方向"""
    DEBIT = 'DEBIT'
    CREDIT = 'CREDIT'
