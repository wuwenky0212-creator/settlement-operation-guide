# ProgressStepper Component

简化的进度指示器组件，用于在交易信息和现金流信息标签页底部显示生命周期进度。

## 功能

- 横向步骤条展示
- 支持多种状态：completed（已完成）、current（当前）、pending（待处理）、failed（失败）
- 响应式设计，支持移动端
- 平滑的动画效果

## 使用方法

### 基本用法

```vue
<template>
  <ProgressStepper :steps="progressSteps" />
</template>

<script setup>
import { ref } from 'vue'
import ProgressStepper from '@/components/ProgressStepper.vue'

const progressSteps = ref([
  { label: '交易点', status: 'completed' },
  { label: '已证实', status: 'completed' },
  { label: '已记账', status: 'current' },
  { label: '已发报', status: 'pending' },
  { label: '已完成', status: 'pending' }
])
</script>
```

### Props

| 属性名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| steps | Array | 是 | 步骤数组，每个步骤包含 label 和 status |

### Steps 数据格式

```typescript
interface Step {
  label: string;  // 步骤标签
  status: 'completed' | 'current' | 'pending' | 'failed';  // 步骤状态
}
```

### 状态说明

- **completed**: 已完成的步骤，显示为绿色，带勾号
- **current**: 当前步骤，显示为红色，带脉冲动画
- **pending**: 待处理步骤，显示为灰色
- **failed**: 失败步骤，显示为红色，带叉号

## 集成示例

### 在 TransactionInfoTab 中使用

```vue
<template>
  <div class="transaction-info-tab">
    <!-- 交易信息内容 -->
    
    <!-- 生命周期进度 -->
    <div v-if="progressSteps.length > 0" class="progress-section">
      <h3 class="section-title">生命周期进度</h3>
      <ProgressStepper :steps="progressSteps" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'
import ProgressStepper from '@/components/ProgressStepper.vue'

const progressSteps = ref([])

const loadProgress = async () => {
  const response = await apiClient.get(`/transactions/${transactionId}/progress`)
  
  if (response?.flowVisualization) {
    progressSteps.value = response.flowVisualization.map(node => ({
      label: node.name,
      status: node.status.toLowerCase()
    }))
  }
}

onMounted(() => {
  loadProgress()
})
</script>
```

## 样式定制

组件使用 scoped 样式，主要颜色：
- 已完成：#4CAF50（绿色）
- 当前：#D32F2F（红色）
- 失败：#F44336（红色）
- 待处理：#e0e0e0（灰色）

## 响应式行为

- 桌面端：步骤横向排列，自动分配空间
- 移动端（< 768px）：支持横向滚动，步骤大小固定

## 注意事项

1. 确保 steps 数组中至少有一个步骤
2. status 值必须是预定义的四种状态之一
3. label 文本过长时会自动截断并显示省略号
4. 组件会自动处理步骤之间的连接线颜色
