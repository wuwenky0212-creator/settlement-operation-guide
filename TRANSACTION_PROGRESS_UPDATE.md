# 交易进度跟踪组件更新说明

## 更新概述

根据需求文档功能6的详细要求，已完成交易生命周期进度跟踪组件的内容修正。

## 主要变更

### 1. 阶段调整

**修改前**（5个阶段）:
- 交易点
- 证实点
- 收付点
- 账务点
- 生命周期完成

**修改后**（3个主要阶段，严格按照功能6需求）:
- 后台复核
- SWIFT证实回执状态（包含RMC和FTM两个子节点）
- 证实匹配

### 2. 核心逻辑变更

#### 后台复核阶段
- **复核通过**: 进入SWIFT证实阶段
- **交易已删除**: 流程终结，标记为红色

#### SWIFT证实回执状态阶段
这是最核心的变更，严格遵循串行逻辑：

**子节点1: RMC发送**
- 成功：自动触发FTM处理
- 失败：流程阻断，明确标注"无FTM回执"，红色高亮

**子节点2: FTM处理**
- 前提条件：RMC必须成功
- 仅当RMC成功时才显示FTM子节点
- 成功：报文正式出库，进入证实匹配阶段
- 失败：触发"待办补发"提醒，黄色警告

**关键特性**:
- RMC失败时，不显示FTM子节点
- RMC失败时，显示阻断提示："RMC失败，流程已阻断，无FTM回执"
- FTM失败时，显示操作指引："报文传输中断（FTM失败），请在待办中执行'补发处理'"

#### 证实匹配阶段
- **匹配成功**: 流程闭环，绿色标记
- **手工处理**: 需人工匹配或撤销，黄色标记

### 3. UI增强

#### 新增元素
1. **子节点展示区域**: 专门展示RMC和FTM的状态
2. **阻断提示框**: 当RMC失败时显示红色阻断提示
3. **操作指引消息**: 在子节点中显示具体的错误信息和操作建议
4. **状态徽章**: 为子节点添加独立的状态徽章

#### 颜色方案
- **绿色**: 成功状态（复核通过、RMC成功、FTM成功、匹配成功）
- **蓝色**: 进行中状态（复核中、处理中、匹配中）
- **灰色**: 待处理状态
- **红色**: 失败/终结状态（交易已删除、RMC失败、流程阻断）
- **黄色**: 警告/待人工处理状态（FTM失败、手工处理）

### 4. Props变更

**移除的Props**:
- `tradeDate`
- `valueDate`
- `accountingDate`
- `confirmationType`
- `confirmationStatus`
- `settlementMethod`
- `cashFlowCount`
- `voucherCount`
- `currentStage`

**新增的Props**:
- `rmcStatus`: RMC子节点状态
- `ftmStatus`: FTM子节点状态

**修改的Props**:
- `stageStatuses`: 从5个阶段改为3个主要阶段
  ```javascript
  // 修改前
  {
    trade: 'completed',
    confirmation: 'completed',
    settlement: 'current',
    accounting: 'pending',
    completed: 'pending'
  }
  
  // 修改后
  {
    review: 'approved',
    swift: 'processing',
    matching: 'pending'
  }
  ```

- `timestamps`: 从5个时间戳改为4个
  ```javascript
  // 修改前
  {
    trade: null,
    confirmation: null,
    settlement: null,
    accounting: null,
    completed: null
  }
  
  // 修改后
  {
    review: null,
    rmc: null,
    ftm: null,
    matching: null
  }
  ```

## 状态值定义

### 主要阶段状态

**review (后台复核)**:
- `pending`: 待复核
- `in-review`: 复核中
- `approved`: 复核通过
- `deleted`: 交易已删除（流程终结）

**swift (SWIFT证实回执)**:
- `pending`: 待处理
- `processing`: 处理中
- `success`: 发送成功
- `failed`: 发送失败
- `blocked`: 回执失败（流程阻断）

**matching (证实匹配)**:
- `pending`: 待匹配
- `matching`: 匹配中
- `success`: 匹配成功
- `manual`: 手工处理

### 子节点状态

**rmcStatus / ftmStatus**:
- `pending`: 待处理
- `processing`: 处理中
- `success`: 成功
- `failed`: 失败

## 使用示例

```vue
<TransactionLifecycleProgress 
  transaction-id="FX202602160001"
  product-type="外汇掉期"
  :stage-statuses="{
    review: 'approved',
    swift: 'processing',
    matching: 'pending'
  }"
  rmc-status="success"
  ftm-status="processing"
  :timestamps="{
    review: '2026-02-16T17:13:00',
    rmc: '2026-02-16T18:15:00',
    ftm: null,
    matching: null
  }"
/>
```

## 关键场景展示

### 场景1: RMC失败（流程阻断）
```javascript
stageStatuses: {
  review: 'approved',
  swift: 'blocked',
  matching: 'pending'
}
rmcStatus: 'failed'
ftmStatus: 'pending'  // 不会显示FTM子节点
```
**显示效果**:
- SWIFT证实回执状态卡片显示红色阻断状态
- 只显示RMC子节点，标记为"失败"
- 显示红色阻断提示框："RMC失败，流程已阻断，无FTM回执"
- 不显示FTM子节点

### 场景2: FTM失败（需补发）
```javascript
stageStatuses: {
  review: 'approved',
  swift: 'failed',
  matching: 'pending'
}
rmcStatus: 'success'
ftmStatus: 'failed'
```
**显示效果**:
- SWIFT证实回执状态卡片显示失败状态
- RMC子节点标记为"成功"（绿色）
- FTM子节点标记为"失败"（红色）
- FTM子节点下方显示黄色警告消息："报文传输中断（FTM失败），请在待办中执行'补发处理'"

### 场景3: 正常流转
```javascript
stageStatuses: {
  review: 'approved',
  swift: 'success',
  matching: 'success'
}
rmcStatus: 'success'
ftmStatus: 'success'
```
**显示效果**:
- 所有阶段标记为绿色"已完成"
- RMC和FTM子节点都标记为"成功"
- 证实匹配显示"匹配成功"

## 验收要点

✅ 严格按照后台复核 → SWIFT证实回执 → 证实匹配的顺序展示  
✅ SWIFT证实回执内部遵循RMC → FTM的串行逻辑  
✅ RMC失败时不显示FTM子节点  
✅ RMC失败时显示红色阻断提示  
✅ FTM失败时显示黄色警告和操作指引  
✅ 子节点状态独立显示和更新  
✅ 时间戳正确显示  
✅ 响应式布局在不同设备上正常工作  
✅ 与结算支付进度保持一致的视觉风格  

## 文件清单

**修改的文件**:
1. `frontend/src/components/TransactionLifecycleProgress.vue` - 完全重构
2. `frontend/src/views/TransactionSummaryNew.vue` - 更新props传递
3. `PROGRESS_UI_UPGRADE.md` - 更新文档
4. `TRANSACTION_PROGRESS_UPDATE.md` - 新增本文档

## 后续建议

1. **数据联动**: 根据后端API返回的实际状态自动更新进度
2. **操作入口**: 为"补发处理"、"手工匹配"等操作提供可点击的按钮
3. **详情展开**: 点击子节点可展开查看更多详细信息
4. **历史记录**: 显示每个阶段的历史变更记录
5. **通知提醒**: 当状态变更时发送通知给相关人员

## 测试建议

1. 测试RMC失败场景，确认FTM子节点不显示
2. 测试FTM失败场景，确认显示补发提醒
3. 测试交易删除场景，确认流程终结标记
4. 测试正常流转场景，确认所有状态正确显示
5. 测试响应式布局在不同屏幕尺寸下的表现
6. 测试时间戳显示格式
7. 测试状态颜色和图标的正确性
