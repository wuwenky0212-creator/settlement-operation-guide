# 设计文档：操作指导功能

## 概述

操作指导功能是GIT-RG系统中的核心模块，用于支持交易确认书的查询、状态跟踪和操作指引。该系统通过可视化的方式展示交易生命周期的各个阶段，并根据当前状态动态生成操作指引，帮助用户高效处理交易后续流程。

系统采用前后端分离架构：
- **前端**: Vue.js框架，类似murex系统的UI风格
- **后端**: Python (Flask/FastAPI)，提供RESTful API服务

核心功能包括：
- 多条件交易查询与分页展示
- 交易详情的多维度展示（标签页方式）
- 交易生命周期状态实时跟踪
- 基于状态的动态操作指引
- 现金流收付进度跟踪
- 数据导出功能

## 架构设计

### 系统架构

系统采用三层架构：

```
┌─────────────────────────────────────────────────────────┐
│              表示层 (Presentation - Vue.js)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 交易汇总页面  │  │ 交易详情页面  │  │ 现金流查询页面 │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │ HTTP/REST
                            ↓
┌─────────────────────────────────────────────────────────┐
│            业务逻辑层 (Business - Python)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 查询服务      │  │ 状态跟踪服务  │  │ 操作指引服务  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 导出服务      │  │ 事件服务      │  │ 账务服务      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────┐
│            数据访问层 (Data Access - Python)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 交易仓储      │  │ 事件仓储      │  │ 账务仓储      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ 现金流仓储    │  │ 并发控制      │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────┐
│                      数据库 (Database)                    │
│         交易表 | 事件表 | 账务表 | 现金流表               │
└─────────────────────────────────────────────────────────┘
```

### 外部系统集成

```
┌─────────────────────────────────────────────────────────┐
│                    操作指导系统                           │
└─────────────────────────────────────────────────────────┘
         │              │              │              │
         ↓              ↓              ↓              ↓
    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
    │ SWIFT  │    │  核心  │    │ 反洗钱 │    │ 内部账 │
    │  系统  │    │  系统  │    │  系统  │    │  系统  │
    └────────┘    └────────┘    └────────┘    └────────┘
```

## 组件与接口

### 核心组件

#### 1. 查询服务 (QueryService)

负责处理交易和现金流的查询请求。

**接口**:
```python
from typing import Protocol, List
from dataclasses import dataclass

class QueryService(Protocol):
    """查询服务接口"""
    
    def query_transactions(
        self, 
        criteria: TransactionQueryCriteria
    ) -> PagedResult[TransactionSummary]:
        """查询交易汇总列表"""
        ...
    
    def get_transaction_detail(
        self, 
        external_id: str
    ) -> TransactionDetail:
        """查询交易详情"""
        ...
    
    def query_cash_flows(
        self, 
        criteria: CashFlowQueryCriteria
    ) -> PagedResult[CashFlowSummary]:
        """查询现金流列表"""
        ...
    
    def get_cash_flow_detail(
        self, 
        cash_flow_id: str
    ) -> CashFlowDetail:
        """查询现金流详情"""
        ...
```

#### 2. 状态跟踪服务 (StatusTrackingService)

负责跟踪交易和现金流的生命周期状态。

**接口**:
```python
class StatusTrackingService(Protocol):
    """状态跟踪服务接口"""
    
    def get_transaction_progress(
        self, 
        transaction_id: str
    ) -> LifecycleProgress:
        """获取交易生命周期进度"""
        ...
    
    def get_cash_flow_progress(
        self, 
        cash_flow_id: str
    ) -> PaymentProgress:
        """获取现金流收付进度"""
        ...
    
    def subscribe_status_updates(
        self, 
        transaction_id: str, 
        callback: Callable[[StatusUpdate], None]
    ) -> Subscription:
        """订阅状态更新（实时推送）"""
        ...
```

#### 3. 操作指引服务 (OperationGuideService)

根据当前状态生成操作指引。

**接口**:
```python
class OperationGuideService(Protocol):
    """操作指引服务接口"""
    
    def get_transaction_guide(
        self, 
        transaction_id: str, 
        current_status: TransactionStatus
    ) -> OperationGuide:
        """获取交易操作指引"""
        ...
    
    def get_cash_flow_guide(
        self, 
        cash_flow_id: str, 
        current_status: CashFlowStatus
    ) -> OperationGuide:
        """获取现金流操作指引"""
        ...
```

#### 4. 事件服务 (EventService)

管理交易事件记录。

**接口**:
```python
class EventService(Protocol):
    """事件服务接口"""
    
    def query_events(
        self, 
        transaction_id: str, 
        pagination: PaginationParams
    ) -> PagedResult[EventRecord]:
        """查询事件列表"""
        ...
    
    def record_event(
        self, 
        event: EventRecord
    ) -> None:
        """记录新事件"""
        ...
```

#### 5. 账务服务 (AccountingService)

管理账务信息。

**接口**:
```python
class AccountingService(Protocol):
    """账务服务接口"""
    
    def get_payment_info(
        self, 
        transaction_id: str
    ) -> PaymentInfo:
        """查询支付信息"""
        ...
    
    def query_accounting_records(
        self, 
        transaction_id: str, 
        pagination: PaginationParams
    ) -> PagedResult[AccountingRecord]:
        """查询账务记录列表"""
        ...
```

#### 6. 导出服务 (ExportService)

处理数据导出请求。

**接口**:
```python
from enum import Enum

class ExportFormat(Enum):
    """导出格式"""
    EXCEL = "excel"
    CSV = "csv"

class ExportService(Protocol):
    """导出服务接口"""
    
    def export_transactions(
        self, 
        criteria: TransactionQueryCriteria, 
        format: ExportFormat, 
        fields: Optional[List[str]] = None
    ) -> ExportResult:
        """导出交易列表"""
        ...
    
    def export_cash_flows(
        self, 
        criteria: CashFlowQueryCriteria, 
        format: ExportFormat
    ) -> ExportResult:
        """导出现金流列表"""
        ...
```

### 数据访问层组件

#### 7. 交易仓储 (TransactionRepository)

**接口**:
```python
class TransactionRepository(Protocol):
    """交易仓储接口"""
    
    def find_by_criteria(
        self, 
        criteria: TransactionQueryCriteria, 
        pagination: PaginationParams
    ) -> PagedResult[Transaction]:
        """根据条件查询交易"""
        ...
    
    def find_by_external_id(
        self, 
        external_id: str
    ) -> Optional[Transaction]:
        """根据外部流水号查询交易"""
        ...
    
    def update_status(
        self, 
        transaction_id: str, 
        status: TransactionStatus, 
        version: int
    ) -> None:
        """更新交易状态"""
        ...
```

#### 8. 并发控制 (ConcurrencyControl)

**接口**:
```python
@dataclass
class Lock:
    """锁对象"""
    entity_id: str
    version: int
    acquired_at: datetime

class ConcurrencyControl(Protocol):
    """并发控制接口"""
    
    def acquire_optimistic_lock(
        self, 
        entity_id: str, 
        version: int
    ) -> Lock:
        """获取乐观锁"""
        ...
    
    def release_lock(
        self, 
        lock: Lock
    ) -> None:
        """释放锁"""
        ...
    
    def detect_conflict(
        self, 
        entity_id: str, 
        expected_version: int
    ) -> bool:
        """检测并发冲突"""
        ...
```

## 数据模型

### 核心实体

#### 交易 (Transaction)

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

@dataclass
class Transaction:
    """交易实体"""
    # 标识信息
    external_id: str              # 外部流水号
    transaction_id: str           # 交易流水号
    parent_transaction_id: Optional[str] = None  # 父交易流水号
    
    # 基本信息
    entry_date: datetime          # 录入日
    trade_date: datetime          # 交易日
    value_date: datetime          # 起息日
    maturity_date: datetime       # 到期日
    
    # 交易详情
    account: str                  # 账户
    product: 'ProductType'        # 产品类型
    direction: 'Direction'        # 买卖方向
    underlying: str               # 标的物
    counterparty: str             # 交易对手
    
    # 状态信息
    status: 'TransactionStatus'   # 交易状态
    back_office_status: 'BackOfficeStatus'  # 后线处理状态
    
    # 清算证实信息
    settlement_method: 'SettlementMethod'  # 清算方式
    confirmation_number: Optional[str] = None  # 证实编号
    confirmation_type: 'ConfirmationType'  # 证实方式
    confirmation_match_type: Optional[str] = None  # 证实匹配方式
    confirmation_match_status: Optional['MatchStatus'] = None  # 证实匹配状态
    
    # 其他信息
    nature: str                   # 交易性质
    source: 'TransactionSource'   # 交易来源
    latest_event_type: Optional[str] = None  # 最新事件类型
    operating_institution: str    # 运营机构
    trader: str                   # 交易员
    
    # 并发控制
    version: int                  # 版本号（乐观锁）
    last_modified_date: datetime  # 最后修改日期
    last_modified_by: str         # 最后修改人
```

#### 事件记录 (EventRecord)

```python
@dataclass
class EventRecord:
    """事件记录实体"""
    event_id: str                 # 事件ID
    external_id: str              # 外部流水号
    transaction_id: str           # 交易流水号
    parent_transaction_id: Optional[str] = None  # 父交易流水号
    
    product: 'ProductType'        # 产品
    account: str                  # 账户
    event_type: str               # 事件类型
    transaction_status: 'TransactionStatus'  # 交易状态
    
    entry_date: datetime          # 录入日
    trade_date: datetime          # 交易日
    modified_date: datetime       # 修改日
    
    back_office_status: 'BackOfficeStatus'  # 后线处理状态
    confirmation_status: Optional[str] = None  # 证实状态
    confirmation_match_status: Optional['MatchStatus'] = None  # 证实匹配状态
    
    operator: str                 # 操作用户
```

#### 现金流 (CashFlow)

```python
@dataclass
class AccountInfo:
    """账号信息"""
    account_number: str
    account_name: str
    bank_name: str
    bank_code: str

@dataclass
class CashFlow:
    """现金流实体"""
    cash_flow_id: str             # 现金流内部ID
    transaction_id: str           # 交易流水号
    payment_info_id: Optional[str] = None  # 收付信息ID
    settlement_id: Optional[str] = None  # 结算内部ID
    
    direction: str                # 方向 ('RECEIVE' | 'PAY')
    currency: str                 # 币种
    amount: float                 # 金额
    payment_date: datetime        # 收付日期
    
    account_info: AccountInfo     # 账号信息
    settlement_method: 'SettlementMethod'  # 结算方式
    
    current_status: 'CashFlowStatus'  # 当前状态
    progress_percentage: int      # 进度百分比
    
    version: int                  # 版本号
```

#### 账务记录 (AccountingRecord)

```python
@dataclass
class AccountingRecord:
    """账务记录实体"""
    voucher_id: str               # 传票号
    actual_accounting_date: datetime  # 实际记账日
    planned_accounting_date: datetime  # 计划记账日
    event_number: str             # 事件号
    
    debit_credit_indicator: str   # 借贷方向 ('DEBIT' | 'CREDIT')
    currency: str                 # 货币
    account_subject: str          # 科目
    transaction_amount: float     # 交易金额
```

### 枚举类型

```python
from enum import Enum

class ProductType(Enum):
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

class TransactionStatus(Enum):
    """交易状态"""
    EFFECTIVE = '生效'
    MATURED = '到期'
    INVALID = '失效'

class BackOfficeStatus(Enum):
    """后线处理状态"""
    CONFIRMED = '已证实'
    SETTLED_PENDING_REPORT = '已清算待发报'
    REPORTED_PENDING_RECEIPT = '已发报待接收回执'
    COMPLETED = '已完成'

class SettlementMethod(Enum):
    """清算方式"""
    GROSS = '全额'
    NET = '净额'
    CENTRALIZED = '集中'
    NOT_REQUIRED = '无需'
    OUR_BANK_AGENT = '我行代理'
    OTHER_BANK_AGENT = '他行代理'

class ConfirmationType(Enum):
    """证实方式"""
    SWIFT = 'SWIFT'
    TEXT = '文本'
    NO_CONFIRMATION = '无证实'

class TransactionSource(Enum):
    """交易来源"""
    GIT = 'GIT'
    FXO = 'FXO'
    FXS = 'FXS'
    FXY = 'FXY'
    FXW = 'FXW'

class MatchStatus(Enum):
    """证实匹配状态"""
    MATCHED = '匹配成功'
    UNMATCHED = '匹配失败'
    PENDING = '等待匹配'

class CashFlowStatus(Enum):
    """现金流状态"""
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
```

### 查询条件模型

```typescript
interface TransactionQueryCriteria {
  externalId?: string;             // 外部流水号（必填）
  status?: TransactionStatus;      // 交易状态
  tradeDate?: DateRange;           // 交易日
  valueDate?: DateRange;           // 起息日
  maturityDate?: DateRange;        // 到期日
  counterparty?: string;           // 交易对手
  product?: ProductType;           // 产品
  currency?: string;               // 货币
  operatingInstitution?: string;   // 运营机构
  businessInstitution?: string;    // 业务机构
  settlementMethod?: SettlementMethod;  // 清算方式
  confirmationType?: ConfirmationType;  // 证实方式
  source?: TransactionSource;      // 交易来源
}

interface CashFlowQueryCriteria {
  transactionId?: string;          // 交易流水号
  cashFlowId?: string;             // 现金流内部ID
  paymentInfoId?: string;          // 收付信息ID
  settlementId?: string;           // 结算内部ID
  direction?: 'RECEIVE' | 'PAY';   // 方向
  currency?: string;               // 币种
  amountRange?: AmountRange;       // 金额范围
  paymentDate?: DateRange;         // 收付日期
  status?: CashFlowStatus;         // 状态
}

interface PaginationParams {
  page: number;                    // 页码（从1开始）
  pageSize: number;                // 每页记录数
  sortBy?: string;                 // 排序字段
  sortOrder?: 'ASC' | 'DESC';      // 排序方向
}

interface DateRange {
  from?: Date;
  to?: Date;
}

interface AmountRange {
  min?: number;
  max?: number;
}
```

### 响应模型

```typescript
interface PagedResult<T> {
  data: T[];                       // 当前页数据
  pagination: {
    currentPage: number;           // 当前页码
    totalPages: number;            // 总页数
    totalRecords: number;          // 记录总数
    pageSize: number;              // 每页记录数
  };
  summary?: QuerySummary;          // 查询条件摘要
}

interface LifecycleProgress {
  currentStage: string;            // 当前阶段
  currentStatus: string;           // 当前状态
  progressPercentage: number;      // 进度百分比
  stageCompletionTime?: Date;      // 阶段完成时间
  
  statusReceipts: StatusReceipt[]; // 状态回执详情
  flowVisualization: FlowNode[];   // 流程可视化数据
}

interface StatusReceipt {
  stage: string;                   // 阶段名称
  status: 'SUCCESS' | 'FAILED' | 'WAITING' | 'PROCESSING';  // 状态
  timestamp?: Date;                // 时间戳
  message?: string;                // 状态消息
  canProceed: boolean;             // 是否可继续后续流程
}

interface FlowNode {
  id: string;                      // 节点ID
  name: string;                    // 节点名称
  status: 'COMPLETED' | 'CURRENT' | 'PENDING' | 'FAILED' | 'BLOCKED' | 'WAITING_APPROVAL';  // 节点状态
  timestamp?: Date;                // 完成时间
}

interface PaymentProgress {
  currentStage: string;            // 当前阶段（清算轧差/合规准入/结算执行/结算撤销）
  currentStatus: string;           // 当前状态
  sendingRoute: 'SWIFT' | 'CBMNet' | 'INTERNAL';  // 发送路径
  progressPercentage: number;      // 进度百分比
  
  // 阶段1: 清算轧差
  nettingStage?: {
    prerequisiteCheck: {          // 前置触发校验
      productType: string;        // 产品类型（外汇/拆借/现券/回购）
      requiredCondition: string;  // 需满足的条件
      conditionMet: boolean;      // 条件是否满足
    };
    nettingType: 'AUTO' | 'MANUAL';  // 轧差类型
    status: string;               // 阶段状态
    timestamp?: Date;             // 完成时间
  };
  
  // 阶段2: 合规准入
  complianceStage?: {
    amlCheck: {                   // 反洗钱检查
      status: 'CHECKING' | 'APPROVED' | 'BLOCKED';
      timestamp?: Date;
      message?: string;
    };
    routeDecision: {              // 路径决策
      route: 'SWIFT' | 'CBMNet' | 'INTERNAL';
      timestamp?: Date;
    };
    manualApproval?: {            // 人工审批（如配置）
      status: 'PENDING' | 'APPROVED' | 'REJECTED';
      timestamp?: Date;
      approver?: string;
    };
  };
  
  // 阶段3: 结算执行与回执
  settlementStage?: {
    transmissionLayer?: {         // 传输层回执（SWIFT路径）
      rmc: {
        status: 'SENDING' | 'SUCCESS' | 'FAILED';
        timestamp?: Date;
        message?: string;
      };
      ftm?: {                     // 仅当RMC成功时存在
        status: 'SENDING' | 'SUCCESS' | 'FAILED';
        timestamp?: Date;
        message?: string;
      };
    };
    manualConfirm?: {             // 人工确认（CBMNet路径）
      status: 'PENDING' | 'APPROVED' | 'REJECTED';
      timestamp?: Date;
      operator?: string;
    };
    accountingLayer: {            // 账务层回执
      mode: 'AUTO' | 'MANUAL';
      status: 'PROCESSING' | 'SUCCESS' | 'FAILED' | 'UNKNOWN';
      timestamp?: Date;
      message?: string;
    };
  };
  
  // 阶段4: 结算撤销
  cancellationStage?: {
    transmissionLayer?: {         // 传输层（SWIFT路径）
      rmc: {
        status: 'SENDING' | 'SUCCESS' | 'FAILED';
        timestamp?: Date;
      };
      ftm?: {
        status: 'SENDING' | 'SUCCESS' | 'FAILED';
        timestamp?: Date;
      };
    };
    reversalProcessing: {         // 资金冲正
      status: 'PROCESSING' | 'SUCCESS' | 'FAILED';
      timestamp?: Date;
      message?: string;
    };
  };
  
  flowVisualization: FlowNode[];   // 流程可视化数据
  operationGuide?: OperationGuide; // 操作指引
}

interface OperationGuide {
  nextAction: string;              // 下一步操作
  actionEntry?: ActionEntry;       // 操作入口
  notes?: string;                  // 注意事项
  estimatedTime?: string;          // 预计时间
}

interface ActionEntry {
  type: 'BUTTON' | 'LINK';         // 入口类型
  label: string;                   // 显示文本
  url?: string;                    // 链接地址
  action?: string;                 // 操作标识
}
```

## 正确性属性

*属性是一个特征或行为，应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*


### 查询与分页属性

**属性1: 查询条件组合处理**
*对于任意*有效的查询条件组合，系统应该能够处理并返回符合条件的结果，不会因条件组合而失败。
**验证：功能1.1**

**属性2: 查询结果排序一致性**
*对于任意*交易查询结果，返回的列表应该按交易日期降序排列，即对于列表中任意相邻的两条记录，前一条的交易日期应该大于或等于后一条的交易日期。
**验证：功能1.2**

**属性3: 分页参数正确应用**
*对于任意*有效的分页参数（页码、每页记录数），返回的结果应该包含正确数量的记录，且分页元数据（当前页、总页数、总记录数）应该与实际数据一致。
**验证：功能1.3, 1.5**

**属性4: 导出数据一致性**
*对于任意*查询条件，导出的数据应该与查询结果完全一致，不受分页限制影响。
**验证：功能1.7**

### 数据完整性属性

**属性5: 交易详情完整性**
*对于任意*有效的交易ID，返回的交易详情应该包含所有必需字段（外部流水号、交易流水号、交易日、起息日、到期日、产品、状态等），且字段值不为空。
**验证：功能2.5**

**属性6: 事件记录字段完整性**
*对于任意*事件记录，应该包含完整的14个字段（外部流水号、交易流水号、父交易流水号、产品、账户、事件类型、交易状态、录入日、交易日、修改日、后线处理状态、证实状态、证实匹配状态、操作用户）。
**验证：功能3.1**

**属性7: 事件记录排序一致性**
*对于任意*交易的事件记录列表，应该按修改日降序排列，即对于列表中任意相邻的两条记录，前一条的修改日应该大于或等于后一条的修改日。
**验证：功能3.2**

**属性8: 账务信息完整性**
*对于任意*有效的交易ID，返回的账务信息应该包含清算方式（我行和对手方的完整账户信息）和支付信息（指令ID、日期、金额、报文类型等关键字段）。
**验证：功能4.1, 4.2, 4.3**

**属性9: 支付记录列表完整性**
*对于任意*有多条支付记录的交易，返回的支付记录列表应该包含所有支付记录，不应遗漏任何记录。
**验证：功能4.4**

**属性10: 账务记录字段完整性**
*对于任意*账务记录，应该包含完整的8个字段（传票号、实际记账日、计划记账日、事件号、借贷方向、货币、科目、交易金额）。
**验证：功能5.1**

**属性11: 账务记录排序一致性**
*对于任意*交易的账务记录列表，应该按实际记账日降序排列，即对于列表中任意相邻的两条记录，前一条的实际记账日应该大于或等于后一条的实际记账日。
**验证：功能5.2**

**属性12: 账务金额汇总正确性**
*对于任意*交易的账务记录列表，按币种汇总的借贷金额应该等于该币种所有借方金额之和减去所有贷方金额之和。
**验证：功能5.6**

### 生命周期跟踪属性

**属性13: 生命周期阶段识别准确性**
*对于任意*交易，系统应该能够根据交易的当前状态和回执信息，准确识别交易所处的生命周期阶段（SWIFT证实、证实匹配、收付发报等）。
**验证：功能6.1**

**属性14: 状态回执顺序一致性**
*对于任意*交易的状态回执列表，应该严格按照预定义的顺序排列（SWIFT证实 → 证实匹配 → 收付发报），不应出现顺序错乱。
**验证：功能6.2**

**属性15: 流程路径条件正确性**
*对于任意*交易，根据其结算方式（SWIFT/HKSWIFT/内部账），系统应该展示对应的流程路径，不同结算方式的流程路径应该符合预定义规则。
**验证：功能6.3**

**属性16: 阶段状态明确性**
*对于任意*交易的每个生命周期阶段，应该有明确的状态标识（成功/失败/等待/处理中），不应出现状态不明的情况。
**验证：功能6.4**

**属性17: 失败节点原因完整性**
*对于任意*状态为失败或阻塞的节点，应该包含明确的失败原因或阻塞原因，不应为空。
**验证：功能6.5**

**属性18: 流程图数据结构正确性**
*对于任意*交易的流程可视化数据，应该包含所有必需的节点信息（节点ID、名称、状态、时间戳），且节点状态应该与实际状态一致。
**验证：功能6.6**

### 操作指引属性

**属性19: 操作指引动态生成正确性**
*对于任意*交易状态，系统应该能够生成对应的操作指引，且操作指引的内容应该与该状态的预定义规则一致。
**验证：功能7.1**

**属性20: 人工处理入口完整性**
*对于任意*需要人工处理的交易状态（如证实匹配失败、反洗钱检查失败等），操作指引应该包含明确的操作入口信息（类型、标签、URL或操作标识）。
**验证：功能7.2**

**属性21: 操作指引字段完整性**
*对于任意*操作指引，应该包含下一步操作、注意事项和预计时间字段，且字段值不应为空。
**验证：功能7.4, 7.5**

**属性22: 操作指引状态一致性**
*对于任意*交易，其操作指引应该与当前的生命周期状态保持一致，不应出现操作指引与状态不匹配的情况。
**验证：功能7.6**

### 现金流查询属性

**属性23: 现金流查询条件处理**
*对于任意*有效的现金流查询条件组合，系统应该能够处理并返回符合条件的结果，不会因条件组合而失败。
**验证：功能8.1**

**属性24: 现金流记录完整性**
*对于任意*现金流记录，应该包含完整的现金流信息（现金流ID、交易流水号、方向、币种、金额、收付日期、账号信息、当前状态、进度指示）。
**验证：功能8.2, 8.3**

**属性25: 现金流金额汇总正确性**
*对于任意*现金流查询结果，按币种和方向汇总的金额应该等于该币种该方向所有现金流金额之和。
**验证：功能8.6**

**属性26: 结算支付阶段识别准确性**
*对于任意*现金流，系统应该能够根据现金流的当前状态和回执信息，准确识别现金流所处的结算支付阶段（清算轧差/合规准入/结算执行/结算撤销）。
**验证：功能7.1**

**属性27: 结算支付流程路径条件正确性**
*对于任意*现金流，根据其发送路径（SWIFT/CBMNet），系统应该展示对应的处理流程，不同发送路径的流程应该符合预定义规则。
**验证：功能7.2**

**属性28: 结算支付阶段状态明确性**
*对于任意*现金流的每个结算支付阶段，应该有明确的状态标识（待处理/处理中/成功/失败/待审批/已阻断），不应出现状态不明的情况。
**验证：功能7.3**

**属性29: 结算支付失败节点信息完整性**
*对于任意*状态为失败或阻断的结算支付节点，应该包含明确的失败原因和处理方式，不应为空。
**验证：功能7.4**

**属性30: 结算支付操作指引正确性**
*对于任意*现金流状态，系统应该能够生成对应的操作指引，且操作指引的内容应该与该状态的预定义规则一致。
**验证：功能7.5**

**属性31: 结算支付流程图数据结构正确性**
*对于任意*现金流的流程可视化数据，应该包含所有必需的节点信息（节点ID、名称、状态、时间戳），且节点状态应该与实际状态一致。
**验证：功能7.6**

**属性32: 清算轧差前置条件验证正确性**
*对于任意*现金流，系统应该能够根据产品类型（外汇/拆借 vs 现券/回购）正确验证前置触发条件（证实匹配成功 vs 文本证实通过）。
**验证：功能7.1**

**属性33: 合规硬拦截机制有效性**
*对于任意*合规校验失败或待定的现金流，系统应该硬性阻断后续流程，不允许进入发报环节。
**验证：功能7.2**

**属性34: SWIFT传输层串行逻辑正确性**
*对于任意*使用SWIFT路径的现金流，RMC失败时不应触发FTM处理，RMC成功时才应触发FTM处理。
**验证：功能7.3**

**属性35: CBMNet人工确认机制有效性**
*对于任意*使用CBMNet路径的现金流，未经人工确认通过不应进行核心扣划账处理。
**验证：功能7.3**

**属性36: 资金冲正闭环控制正确性**
*对于任意*撤销流程，只有在核心系统反馈资金冲正成功后，原业务才应允许释放或重新处理。
**验证：功能7.4**

### 并发控制与持久化属性

**属性37: 数据持久化一致性**
*对于任意*数据操作（创建、更新、删除），操作成功后应该能够从数据库中读取到更新后的数据，且数据内容与操作参数一致。
**验证：功能9.1**

**属性38: 并发更新冲突检测**
*对于任意*两个并发的更新操作针对同一条记录，系统应该能够检测到并发冲突，且至少有一个操作返回并发冲突错误。
**验证：功能9.4**

**属性39: 并发读取不阻塞**
*对于任意*多个并发的查询操作，系统应该允许所有查询操作同时执行，不应因为锁机制而阻塞查询操作。
**验证：功能9.6**

**属性40: 事务原子性**
*对于任意*包含多个数据操作的复杂事务，要么所有操作都成功并持久化，要么所有操作都回滚，不应出现部分成功部分失败的情况。
**验证：功能9.7**

## 错误处理

### 错误类型

系统定义以下错误类型：

```typescript
enum ErrorCode {
  // 客户端错误 (4xx)
  INVALID_PARAMETER = 'INVALID_PARAMETER',           // 参数无效
  MISSING_REQUIRED_FIELD = 'MISSING_REQUIRED_FIELD', // 缺少必填字段
  RESOURCE_NOT_FOUND = 'RESOURCE_NOT_FOUND',         // 资源不存在
  UNAUTHORIZED = 'UNAUTHORIZED',                     // 未授权
  FORBIDDEN = 'FORBIDDEN',                           // 无权限
  
  // 服务器错误 (5xx)
  INTERNAL_ERROR = 'INTERNAL_ERROR',                 // 内部错误
  DATABASE_ERROR = 'DATABASE_ERROR',                 // 数据库错误
  EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR', // 外部服务错误
  
  // 业务错误
  CONCURRENT_CONFLICT = 'CONCURRENT_CONFLICT',       // 并发冲突
  EXPORT_LIMIT_EXCEEDED = 'EXPORT_LIMIT_EXCEEDED',   // 导出记录数超限
  TRANSACTION_ROLLBACK = 'TRANSACTION_ROLLBACK'      // 事务回滚
}
```

### 错误响应格式

```typescript
interface ErrorResponse {
  code: ErrorCode;                 // 错误代码
  message: string;                 // 错误消息
  details?: any;                   // 详细信息
  timestamp: Date;                 // 时间戳
  requestId: string;               // 请求ID（用于追踪）
}
```

### 错误处理策略

#### 1. 参数验证错误

**场景**: 用户提供的查询条件或参数不符合要求

**处理**:
- 返回 `INVALID_PARAMETER` 或 `MISSING_REQUIRED_FIELD` 错误
- 在 `details` 中列出所有无效的参数及原因
- HTTP状态码: 400

**示例**:
```json
{
  "code": "INVALID_PARAMETER",
  "message": "查询参数无效",
  "details": {
    "invalidFields": [
      {
        "field": "tradeDate",
        "reason": "日期格式不正确，应为YYYY-MM-DD"
      }
    ]
  },
  "timestamp": "2026-02-27T10:30:00Z",
  "requestId": "req-12345"
}
```

#### 2. 资源不存在错误

**场景**: 查询的交易、现金流或其他资源不存在

**处理**:
- 返回 `RESOURCE_NOT_FOUND` 错误
- 在 `message` 中说明哪个资源不存在
- HTTP状态码: 404

**示例**:
```json
{
  "code": "RESOURCE_NOT_FOUND",
  "message": "未找到对应的交易记录",
  "details": {
    "resourceType": "Transaction",
    "resourceId": "EXT-12345"
  },
  "timestamp": "2026-02-27T10:30:00Z",
  "requestId": "req-12346"
}
```

#### 3. 并发冲突错误

**场景**: 多个用户同时更新同一条记录

**处理**:
- 使用乐观锁机制检测冲突
- 返回 `CONCURRENT_CONFLICT` 错误
- 提示用户重试
- HTTP状态码: 409

**示例**:
```json
{
  "code": "CONCURRENT_CONFLICT",
  "message": "记录正在被其他用户修改，请稍后重试",
  "details": {
    "resourceId": "TXN-12345",
    "suggestedRetryAfter": 3
  },
  "timestamp": "2026-02-27T10:30:00Z",
  "requestId": "req-12347"
}
```

#### 4. 数据库错误

**场景**: 数据库操作失败（连接失败、查询超时等）

**处理**:
- 返回 `DATABASE_ERROR` 错误
- 记录详细错误日志
- 不向客户端暴露敏感的数据库信息
- HTTP状态码: 500

**示例**:
```json
{
  "code": "DATABASE_ERROR",
  "message": "数据库操作失败，请稍后重试",
  "timestamp": "2026-02-27T10:30:00Z",
  "requestId": "req-12348"
}
```

#### 5. 事务回滚错误

**场景**: 复杂操作中某个步骤失败，导致整个事务回滚

**处理**:
- 返回 `TRANSACTION_ROLLBACK` 错误
- 说明回滚原因
- 确保所有操作已回滚
- HTTP状态码: 500

**示例**:
```json
{
  "code": "TRANSACTION_ROLLBACK",
  "message": "操作失败，所有更改已回滚",
  "details": {
    "reason": "数据持久化失败"
  },
  "timestamp": "2026-02-27T10:30:00Z",
  "requestId": "req-12349"
}
```

#### 6. 导出限制错误

**场景**: 导出记录数超过系统限制

**处理**:
- 返回 `EXPORT_LIMIT_EXCEEDED` 错误
- 提示用户缩小查询范围
- HTTP状态码: 400

**示例**:
```json
{
  "code": "EXPORT_LIMIT_EXCEEDED",
  "message": "导出记录数超过限制，请缩小查询范围",
  "details": {
    "maxRecords": 10000,
    "requestedRecords": 15000
  },
  "timestamp": "2026-02-27T10:30:00Z",
  "requestId": "req-12350"
}
```

### 错误日志记录

所有错误都应该记录到系统日志，包含以下信息：
- 错误代码和消息
- 请求ID（用于追踪）
- 用户信息（用户ID、IP地址）
- 请求参数
- 堆栈跟踪（仅服务器错误）
- 时间戳

## 测试策略

### 测试方法

系统采用双重测试方法：
- **单元测试**: 验证特定示例、边界情况和错误条件
- **基于属性的测试**: 验证通用属性在所有输入下都成立

两种测试方法互补，共同确保系统的正确性：
- 单元测试捕获具体的错误
- 基于属性的测试验证通用的正确性

### 基于属性的测试配置

**测试库选择**: Python的Hypothesis库

**测试配置**:
- 每个属性测试至少运行 100 次迭代
- 每个测试必须引用设计文档中的属性
- 标签格式: `Feature: settlement-operation-guide, Property {number}: {property_text}`

**示例**:
```python
from hypothesis import given, strategies as st
import pytest

# Feature: settlement-operation-guide, Property 2: 查询结果排序一致性
@given(st.lists(transaction_generator(), min_size=2, max_size=100))
def test_transaction_query_results_sorted_by_trade_date_descending(transactions):
    """交易查询结果应按交易日期降序排列"""
    # 准备测试数据
    for txn in transactions:
        repository.save(txn)
    
    # 执行查询
    result = query_service.query_transactions(TransactionQueryCriteria())
    
    # 验证排序
    for i in range(len(result.data) - 1):
        assert result.data[i].trade_date >= result.data[i + 1].trade_date
```

### 单元测试策略

**测试覆盖范围**:
- 所有核心业务逻辑
- 边界情况（空列表、单条记录、大量记录）
- 错误条件（无效参数、资源不存在、并发冲突）
- 集成点（数据库操作、外部服务调用）

**测试组织**:
- 按功能模块组织测试文件
- 每个服务类对应一个测试文件
- 使用描述性的测试名称

**示例**:
```python
import pytest
from datetime import datetime

class TestQueryService:
    """查询服务测试"""
    
    def test_returns_empty_list_when_no_transactions_match_criteria(self):
        """当没有交易匹配条件时应返回空列表"""
        criteria = TransactionQueryCriteria(external_id='NON-EXISTENT')
        result = query_service.query_transactions(criteria)
        
        assert result.data == []
        assert result.pagination.total_records == 0
    
    def test_raises_error_when_required_field_is_missing(self):
        """当缺少必填字段时应抛出错误"""
        criteria = TransactionQueryCriteria()  # missing external_id
        
        with pytest.raises(ValueError, match='MISSING_REQUIRED_FIELD'):
            query_service.query_transactions(criteria)
```

### 集成测试

**测试范围**:
- API端点的完整请求-响应流程
- 数据库事务的原子性
- 并发场景的正确性
- 外部系统集成（使用mock或测试环境）

**测试环境**:
- 使用独立的测试数据库
- 每个测试前清理数据
- 使用测试数据生成器创建测试数据

### 性能测试

**测试目标**:
- 验证响应时间符合非功能性需求
- 验证系统能够处理预期的并发负载
- 识别性能瓶颈

**测试场景**:
- 交易汇总查询: < 500ms (1000条记录)
- 交易详情加载: < 300ms
- 事件信息查询: < 200ms
- 账务信息查询: < 200ms
- 导出功能: < 30秒 (1000条记录)
- 并发用户: 至少50个

### 测试数据生成

**生成器设计原则**:
- 生成符合业务规则的有效数据
- 覆盖各种边界情况
- 支持生成大量测试数据

**示例生成器**:
```python
from hypothesis import strategies as st
from datetime import datetime, timedelta

def transaction_generator():
    """交易数据生成器"""
    return st.builds(
        Transaction,
        external_id=st.text(min_size=1, max_size=50),
        transaction_id=st.uuids().map(str),
        trade_date=st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime.now()
        ),
        value_date=st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime.now()
        ),
        maturity_date=st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime.now()
        ),
        product=st.sampled_from(ProductType),
        status=st.sampled_from(TransactionStatus),
        # ... 其他字段
    )
```

## 实现注意事项

### 1. 数据库设计

**索引策略**:
- 在常用查询字段上创建索引（外部流水号、交易日、状态等）
- 使用复合索引优化多条件查询
- 定期分析查询性能并优化索引

**分区策略**:
- 考虑按交易日期对交易表进行分区
- 提高历史数据查询性能

**版本控制**:
- 使用版本号字段实现乐观锁
- 每次更新时递增版本号
- 更新时检查版本号是否匹配

### 2. 缓存策略

**缓存内容**:
- 交易详情（短期缓存，5分钟）
- 操作指引规则（长期缓存，1小时）
- 枚举值和配置数据（长期缓存，24小时）

**缓存失效**:
- 交易状态更新时，清除相关缓存
- 使用缓存版本号管理缓存一致性

### 3. 并发控制

**乐观锁实现**:
```python
from typing import Optional

async def update_transaction_status(
    transaction_id: str,
    new_status: TransactionStatus,
    expected_version: int
) -> None:
    """更新交易状态（使用乐观锁）"""
    query = """
        UPDATE transactions 
        SET status = %s, version = version + 1, last_modified_date = NOW()
        WHERE transaction_id = %s AND version = %s
    """
    
    result = await db.execute(query, [new_status.value, transaction_id, expected_version])
    
    if result.rowcount == 0:
        # 检查记录是否存在
        exists = await repository.exists(transaction_id)
        if not exists:
            raise ValueError('RESOURCE_NOT_FOUND')
        # 版本不匹配，并发冲突
        raise ValueError('CONCURRENT_CONFLICT')
```

### 4. 分页优化

**游标分页**:
- 对于大数据集，考虑使用游标分页代替偏移分页
- 提高深度分页的性能

**计数优化**:
- 缓存总记录数（短期缓存）
- 对于大数据集，提供估算值而非精确计数

### 5. 导出优化

**流式处理**:
- 使用流式处理避免内存溢出
- 分批读取数据并写入文件

**异步处理**:
- 对于大量数据导出，使用异步任务
- 提供任务状态查询接口
- 完成后通知用户下载

### 6. 实时更新

**轮询策略**:
- 前端定期轮询状态更新（10秒间隔）
- 仅轮询当前查看的交易或现金流

**WebSocket推送**:
- 考虑使用WebSocket实现实时推送
- 减少服务器负载和网络流量

### 7. 安全性

**权限验证**:
- 每个API调用都进行权限验证
- 使用基于角色的访问控制（RBAC）

**数据脱敏**:
- 对敏感信息（账号、金额）进行脱敏处理
- 根据用户权限决定脱敏级别

**审计日志**:
- 记录所有数据修改操作
- 包含操作人、操作时间、操作内容

### 8. 可扩展性

**模块化设计**:
- 各服务之间松耦合
- 使用依赖注入管理依赖关系

**配置化**:
- 操作指引规则配置化
- 流程路径配置化
- 便于后续扩展和修改

**API版本化**:
- 使用URL路径或请求头进行版本控制
- 保持向后兼容性
