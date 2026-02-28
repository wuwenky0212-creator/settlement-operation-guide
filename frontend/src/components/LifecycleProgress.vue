<template>
  <div class="lifecycle-progress">
    <!-- Progress Header -->
    <div class="progress-header">
      <div class="progress-info">
        <h3 class="current-stage">{{ progress.currentStage }}</h3>
        <span class="current-status" :class="statusClass">{{ progress.currentStatus }}</span>
      </div>
      <div class="progress-percentage">
        <span class="percentage-value">{{ progress.progressPercentage }}%</span>
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: `${progress.progressPercentage}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Flow Visualization -->
    <div class="flow-visualization">
      <div class="flow-nodes">
        <div
          v-for="(node, index) in progress.flowVisualization"
          :key="node.id"
          class="flow-node-wrapper"
        >
          <!-- Node -->
          <div
            class="flow-node"
            :class="getNodeClass(node.status)"
            @click="handleNodeClick(node)"
          >
            <div class="node-icon">
              <span v-if="node.status === 'COMPLETED'">✓</span>
              <span v-else-if="node.status === 'FAILED'">✗</span>
              <span v-else-if="node.status === 'CURRENT'">●</span>
              <span v-else>○</span>
            </div>
            <div class="node-label">{{ node.name }}</div>
            <div v-if="node.timestamp" class="node-time">
              {{ formatDateTime(node.timestamp) }}
            </div>
          </div>

          <!-- Connector -->
          <div
            v-if="index < progress.flowVisualization.length - 1"
            class="flow-connector"
            :class="getConnectorClass(node.status, progress.flowVisualization[index + 1].status)"
          ></div>
        </div>
      </div>
    </div>

    <!-- Status Receipts Details -->
    <div class="status-receipts">
      <h4 class="receipts-title">状态回执详情</h4>
      <div class="receipts-list">
        <div
          v-for="(receipt, index) in progress.statusReceipts"
          :key="index"
          class="receipt-item"
          :class="getReceiptClass(receipt.status)"
        >
          <div class="receipt-header">
            <span class="receipt-stage">{{ receipt.stage }}</span>
            <span class="receipt-status" :class="getStatusBadgeClass(receipt.status)">
              {{ getStatusLabel(receipt.status) }}
            </span>
          </div>
          <div v-if="receipt.message" class="receipt-message">
            {{ receipt.message }}
          </div>
          <div v-if="receipt.timestamp" class="receipt-time">
            {{ formatDateTime(receipt.timestamp) }}
          </div>
          <div v-if="!receipt.canProceed" class="receipt-warning">
            ⚠ 无法继续后续流程
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue'

const props = defineProps({
  progress: {
    type: Object,
    required: true
  }
})

// Computed
const statusClass = computed(() => {
  const status = props.progress.currentStatus
  if (status.includes('成功') || status.includes('完成')) return 'status-success'
  if (status.includes('失败') || status.includes('错误')) return 'status-failed'
  if (status.includes('等待') || status.includes('待')) return 'status-waiting'
  if (status.includes('处理中')) return 'status-processing'
  return ''
})

// Methods
const getNodeClass = (status) => {
  return {
    'node-completed': status === 'COMPLETED',
    'node-current': status === 'CURRENT',
    'node-pending': status === 'PENDING',
    'node-failed': status === 'FAILED'
  }
}

const getConnectorClass = (currentStatus, nextStatus) => {
  if (currentStatus === 'COMPLETED' && (nextStatus === 'COMPLETED' || nextStatus === 'CURRENT')) {
    return 'connector-active'
  }
  if (currentStatus === 'FAILED') {
    return 'connector-failed'
  }
  return 'connector-inactive'
}

const getReceiptClass = (status) => {
  return {
    'receipt-success': status === 'SUCCESS',
    'receipt-failed': status === 'FAILED',
    'receipt-waiting': status === 'WAITING',
    'receipt-processing': status === 'PROCESSING'
  }
}

const getStatusBadgeClass = (status) => {
  return {
    'badge-success': status === 'SUCCESS',
    'badge-failed': status === 'FAILED',
    'badge-waiting': status === 'WAITING',
    'badge-processing': status === 'PROCESSING'
  }
}

const getStatusLabel = (status) => {
  const labels = {
    'SUCCESS': '成功',
    'FAILED': '失败',
    'WAITING': '等待中',
    'PROCESSING': '处理中'
  }
  return labels[status] || status
}

const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return ''
  const date = new Date(dateTimeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleNodeClick = (node) => {
  // Could expand to show more details
  console.log('Node clicked:', node)
}
</script>

<style scoped>
.lifecycle-progress {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Progress Header */
.progress-header {
  background: #f9f9f9;
  border-radius: 4px;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.progress-info {
  flex: 1;
}

.current-stage {
  color: #333;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.current-status {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-success {
  background: #E8F5E9;
  color: #2E7D32;
}

.status-failed {
  background: #FFEBEE;
  color: #C62828;
}

.status-waiting {
  background: #FFF3E0;
  color: #E65100;
}

.status-processing {
  background: #E3F2FD;
  color: #1565C0;
}

.progress-percentage {
  flex: 0 0 300px;
}

.percentage-value {
  display: block;
  text-align: right;
  font-size: 1.5rem;
  font-weight: 600;
  color: #D32F2F;
  margin-bottom: 0.5rem;
}

.progress-bar {
  height: 12px;
  background: #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #D32F2F, #F44336);
  transition: width 0.3s ease;
}

/* Flow Visualization */
.flow-visualization {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 2rem;
  overflow-x: auto;
}

.flow-nodes {
  display: flex;
  align-items: center;
  min-width: max-content;
}

.flow-node-wrapper {
  display: flex;
  align-items: center;
}

.flow-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  min-width: 120px;
  cursor: pointer;
  transition: all 0.2s;
}

.flow-node:hover {
  transform: translateY(-2px);
}

.node-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  transition: all 0.2s;
}

.node-completed .node-icon {
  background: #4CAF50;
  color: white;
}

.node-current .node-icon {
  background: #2196F3;
  color: white;
  animation: pulse 2s infinite;
}

.node-pending .node-icon {
  background: #e0e0e0;
  color: #999;
}

.node-failed .node-icon {
  background: #F44336;
  color: white;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.node-label {
  font-size: 0.875rem;
  font-weight: 500;
  text-align: center;
  color: #333;
}

.node-time {
  font-size: 0.75rem;
  color: #666;
  text-align: center;
}

.flow-connector {
  width: 60px;
  height: 4px;
  margin: 0 -1rem;
  position: relative;
  top: -20px;
}

.connector-active {
  background: #4CAF50;
}

.connector-inactive {
  background: #e0e0e0;
}

.connector-failed {
  background: #F44336;
}

/* Status Receipts */
.status-receipts {
  background: #f9f9f9;
  border-radius: 4px;
  padding: 1.5rem;
}

.receipts-title {
  color: #D32F2F;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #D32F2F;
}

.receipts-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.receipt-item {
  background: white;
  border-radius: 4px;
  padding: 1rem;
  border-left: 4px solid #e0e0e0;
}

.receipt-success {
  border-left-color: #4CAF50;
}

.receipt-failed {
  border-left-color: #F44336;
}

.receipt-waiting {
  border-left-color: #FF9800;
}

.receipt-processing {
  border-left-color: #2196F3;
}

.receipt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.receipt-stage {
  font-weight: 600;
  color: #333;
}

.receipt-status {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge-success {
  background: #E8F5E9;
  color: #2E7D32;
}

.badge-failed {
  background: #FFEBEE;
  color: #C62828;
}

.badge-waiting {
  background: #FFF3E0;
  color: #E65100;
}

.badge-processing {
  background: #E3F2FD;
  color: #1565C0;
}

.receipt-message {
  font-size: 0.875rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.receipt-time {
  font-size: 0.75rem;
  color: #999;
}

.receipt-warning {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #FFF3E0;
  color: #E65100;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Responsive */
@media (max-width: 1024px) {
  .progress-header {
    flex-direction: column;
    align-items: stretch;
  }

  .progress-percentage {
    flex: 1;
  }

  .percentage-value {
    text-align: left;
  }
}

@media (max-width: 768px) {
  .flow-node {
    min-width: 100px;
    padding: 0.75rem;
  }

  .node-icon {
    width: 40px;
    height: 40px;
    font-size: 1.25rem;
  }

  .flow-connector {
    width: 40px;
  }
}
</style>
