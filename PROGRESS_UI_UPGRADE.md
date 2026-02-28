# 进度跟踪UI升级说明

## 概述

本次升级将交易进度跟踪和结算支付进度跟踪的UI统一为卡片式流程图设计，提供更直观、更美观的用户体验。

## 改造内容

### 1. 结算支付进度跟踪 (SettlementPaymentProgress.vue)

**位置**: 交易详情 → 现金流信息标签页 → 底部

**展示阶段**:
1. 清算轧差 - 检查前置条件，自动/手工轧差
2. 合规准入 - 风险检查、反洗钱检查/审批
3. 报文发送分流 - SWIFT路径选择
4. SWIFT传输层 - RMC → FTM链路监控
5. 核心入账 - 账务处理
6. 结算完成 - Settled状态

**特性**:
- 卡片式设计，每个阶段独立展示
- 图标+状态指示（已完成/进行中/待处理/失败）
- 详细的操作提示和注意事项
- 响应式设计，移动端自动切换为垂直布局
- 流程箭头连接各阶段

### 2. 交易生命周期进度跟踪 (TransactionLifecycleProgress.vue)

**位置**: 交易详情 → 交易信息标签页 → 底部

**展示阶段**（严格按照功能6需求）:
1. 后台复核 - 结算员核对交易要素与清算路径
   - 复核通过：进入下一阶段
   - 交易已删除：流程终结
2. SWIFT证实回执状态 - 仅适用于外汇掉期和拆借交易
   - 子节点1: RMC发送（成功后触发FTM）
   - 子节点2: FTM处理（仅当RMC成功时显示）
   - RMC失败：流程阻断，无FTM回执
   - FTM失败：触发待办补发提醒
3. 证实匹配 - 系统或人工进行匹配处理
   - 匹配成功：流程闭环
   - 手工处理：需人工匹配或撤销

**特性**:
- 严格遵循后台复核 → SWIFT证实回执 → 证实匹配的顺序
- SWIFT证实回执内部遵循RMC → FTM的串行逻辑
- RMC失败时明确标注"流程已阻断，无FTM回执"
- FTM失败时提供"补发处理"操作指引
- 子节点状态独立显示（RMC和FTM）
- 阻断节点红色高亮显示
- 时间戳显示
- 状态实时更新

## UI设计特点

### 卡片布局
- 每个阶段使用独立卡片
- 卡片宽度: 280px (桌面端)
- 卡片包含: 图标区、内容区、状态区

### 颜色方案
- 已完成: 绿色 (#4CAF50)
- 进行中: 蓝色 (#2196F3)
- 待处理: 灰色 (#e0e0e0)
- 失败: 红色 (#F44336)
- 警告: 橙色 (#FF9800)

### 交互效果
- 卡片悬停: 阴影+上移效果
- 状态图标: 动态变化
- 流程箭头: 连接各阶段

### 响应式设计
- 桌面端: 水平排列，可横向滚动
- 移动端: 垂直排列，箭头旋转90度

## 文件清单

### 新增文件
1. `frontend/src/components/SettlementPaymentProgress.vue` - 结算支付进度组件
2. `frontend/src/components/TransactionLifecycleProgress.vue` - 交易生命周期进度组件
3. `PROGRESS_UI_UPGRADE.md` - 本说明文档

### 修改文件
1. `frontend/src/views/TransactionSummaryNew.vue` - 集成两个新组件
2. `frontend/src/views/CashFlowDetail.vue` - 集成结算支付进度组件
3. `frontend/src/components/index.js` - 注册新组件

## 使用方法

### 结算支付进度组件

```vue
<SettlementPaymentProgress 
  :current-stage="currentStage"
  :stage-statuses="stageStatuses"
/>
```

**Props**:
- `currentStage`: 当前阶段 (netting/compliance/routing/swift/accounting/completed)
- `stageStatuses`: 各阶段状态对象
  ```javascript
  {
    netting: 'completed',
    compliance: 'current',
    routing: 'pending',
    swift: 'pending',
    accounting: 'pending',
    completed: 'pending'
  }
  ```

### 交易生命周期进度组件

```vue
<TransactionLifecycleProgress 
  :transaction-id="transactionId"
  :product-type="productType"
  :stage-statuses="stageStatuses"
  :rmc-status="rmcStatus"
  :ftm-status="ftmStatus"
  :timestamps="timestamps"
/>
```

**Props**:
- `transactionId`: 交易流水号
- `productType`: 产品类型（用于判断是否显示SWIFT证实）
- `stageStatuses`: 主要阶段状态对象
  ```javascript
  {
    review: 'pending',      // 后台复核: pending/in-review/approved/deleted
    swift: 'pending',        // SWIFT证实: pending/processing/success/failed/blocked
    matching: 'pending'      // 证实匹配: pending/matching/success/manual
  }
  ```
- `rmcStatus`: RMC子节点状态 (pending/processing/success/failed)
- `ftmStatus`: FTM子节点状态 (pending/processing/success/failed)
- `timestamps`: 各阶段时间戳对象
  ```javascript
  {
    review: null,
    rmc: null,
    ftm: null,
    matching: null
  }
  ```

## 状态值说明

### 交易生命周期阶段状态

**后台复核 (review)**:
- `pending`: 待复核
- `in-review`: 复核中
- `approved`: 复核通过 - 绿色背景
- `deleted`: 交易已删除 - 红色背景，流程终结

**SWIFT证实回执 (swift)**:
- `pending`: 待处理 - 灰色背景
- `processing`: 处理中 - 蓝色背景
- `success`: 发送成功 - 绿色背景
- `failed`: 发送失败 - 红色背景
- `blocked`: 回执失败 - 红色背景，高亮显示

**SWIFT子节点状态 (rmcStatus/ftmStatus)**:
- `pending`: 待处理
- `processing`: 处理中
- `success`: 成功
- `failed`: 失败

**证实匹配 (matching)**:
- `pending`: 待匹配 - 灰色背景
- `matching`: 匹配中 - 蓝色背景
- `success`: 匹配成功 - 绿色背景
- `manual`: 手工处理 - 黄色背景

### 结算支付阶段状态 (stageStatuses)
- `completed`: 已完成 - 绿色背景，勾选图标
- `current`: 进行中 - 蓝色背景，沙漏图标
- `pending`: 待处理 - 灰色背景，圆圈图标
- `failed`: 失败 - 红色背景，叉号图标

## 后续优化建议

1. **数据联动**: 根据后端API返回的实际状态自动更新进度
2. **点击交互**: 点击卡片展开更多详情
3. **动画效果**: 添加阶段切换的过渡动画
4. **导出功能**: 支持导出进度报告
5. **历史记录**: 显示每个阶段的历史变更记录

## 测试建议

1. 测试不同状态下的显示效果
2. 测试响应式布局在不同设备上的表现
3. 测试数据为空时的显示
4. 测试长文本的处理
5. 测试浏览器兼容性

## 维护说明

- 组件采用Vue 3 Composition API编写
- 样式使用scoped CSS，避免全局污染
- 图标使用SVG，保证清晰度
- 颜色值统一管理，便于主题切换
