<template>
  <div class="cash-flow-detail-overlay" @click.self="handleClose">
    <div class="cash-flow-detail-modal">
      <!-- Modal Header -->
      <div class="modal-header">
        <h2>现金流收付进度</h2>
        <button class="close-btn" @click="handleClose" title="关闭 (Esc)">
          <span>&times;</span>
        </button>
      </div>

      <!-- Loading State -->
      <LoadingSpinner v-if="loading" />

      <!-- Error State -->
      <MessageAlert
        v-if="error"
        type="error"
        :message="error"
        @close="error = null"
      />

      <!-- Content -->
      <div v-if="!loading && cashFlowDetail" class="modal-content">
        <!-- Basic Information -->
        <div class="basic-info">
          <h3>基本信息</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">现金流内部ID:</span>
              <span class="info-value">{{ cashFlowDetail.cash_flow_id }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">交易流水号:</span>
              <span class="info-value">{{ cashFlowDetail.transaction_id }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">方向:</span>
              <span class="info-value">{{ formatDirection(cashFlowDetail.direction) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">币种:</span>
              <span class="info-value">{{ cashFlowDetail.currency }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">金额:</span>
              <span class="info-value">{{ formatAmount(cashFlowDetail.amount) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">收付日期:</span>
              <span class="info-value">{{ formatDate(cashFlowDetail.payment_date) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">结算方式:</span>
              <span class="info-value">{{ cashFlowDetail.settlement_method }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">当前状态:</span>
              <span class="info-value status-badge" :class="getStatusClass(cashFlowDetail.current_status)">
                {{ formatStatus(cashFlowDetail.current_status) }}
              </span>
            </div>
          </div>

          <!-- Account Information -->
          <div class="account-info">
            <h4>账号信息</h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">账号:</span>
                <span class="info-value">{{ cashFlowDetail.account_number }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">户名:</span>
                <span class="info-value">{{ cashFlowDetail.account_name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">开户行:</span>
                <span class="info-value">{{ cashFlowDetail.bank_name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">开户行号:</span>
                <span class="info-value">{{ cashFlowDetail.bank_code }}</span>
              </div>
            </div>
          </div>

          <!-- 收付进度指示器 -->
          <div v-if="progressSteps.length > 0" class="progress-indicator">
            <h4>收付进度</h4>
            <ProgressStepper :steps="progressSteps" />
          </div>
        </div>

        <!-- Operation Guide -->
        <div class="guide-section">
          <h3>操作指引</h3>
          <CashFlowOperationGuide :cash-flow-id="cashFlowId" />
        </div>

        <!-- Settlement Payment Progress -->
        <div class="settlement-progress-section">
          <SettlementPaymentProgress 
            :current-stage="currentStage"
            :stage-statuses="stageStatuses"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import MessageAlert from '@/components/MessageAlert.vue'
import CashFlowOperationGuide from '@/components/CashFlowOperationGuide.vue'
import ProgressStepper from '@/components/ProgressStepper.vue'
import SettlementPaymentProgress from '@/components/SettlementPaymentProgress.vue'

const route = useRoute()
const router = useRouter()

// Props from route
const cashFlowId = ref(route.params.cashFlowId)

// State
const loading = ref(false)
const error = ref(null)
const cashFlowDetail = ref(null)
const progressSteps = ref([])
const currentStage = ref('netting')
const stageStatuses = ref({
  netting: 'pending',
  compliance: 'pending',
  routing: 'pending',
  swift: 'pending',
  accounting: 'pending',
  completed: 'pending'
})

// Methods
const loadCashFlowDetail = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await apiClient.get(`/cash-flows/${cashFlowId.value}`)
    cashFlowDetail.value = response
    
    // Load progress steps
    await loadProgressSteps()
  } catch (err) {
    console.error('Load cash flow detail error:', err)
    error.value = err.response?.data?.message || '加载现金流详情失败'
  } finally {
    loading.value = false
  }
}

const loadProgressSteps = async () => {
  try {
    const response = await apiClient.get(`/cash-flows/${cashFlowId.value}/progress`)
    
    // Convert progress data to stepper format
    // Support both camelCase and snake_case from API
    const flowData = response?.flowVisualization || response?.flow_visualization
    if (flowData) {
      progressSteps.value = flowData.map(node => ({
        label: node.name,
        status: node.status.toLowerCase() // 'COMPLETED' -> 'completed'
      }))
    }

    // Map current status to settlement stages
    mapStatusToStages(response)
  } catch (err) {
    console.error('Load progress steps error:', err)
    // Silently fail - progress is optional
  }
}

const mapStatusToStages = (progressData) => {
  // Map the current status to settlement payment stages
  const status = cashFlowDetail.value?.current_status
  
  // Initialize all stages as pending
  const newStatuses = {
    netting: 'pending',
    compliance: 'pending',
    routing: 'pending',
    swift: 'pending',
    accounting: 'pending',
    completed: 'pending'
  }

  // Map based on current status
  if (status) {
    if (status.includes('PENDING_AML') || status === 'AML_APPROVED' || status === 'AML_REJECTED') {
      newStatuses.netting = 'completed'
      newStatuses.compliance = status === 'AML_REJECTED' ? 'failed' : 
                               status === 'AML_APPROVED' ? 'completed' : 'current'
      currentStage.value = 'compliance'
    } else if (status.includes('PENDING_SWIFT') || status.includes('SWIFT')) {
      newStatuses.netting = 'completed'
      newStatuses.compliance = 'completed'
      newStatuses.routing = 'completed'
      newStatuses.swift = status === 'SWIFT_FAILED' ? 'failed' : 
                          status === 'SWIFT_SENT' ? 'completed' : 'current'
      currentStage.value = 'swift'
    } else if (status.includes('CORE')) {
      newStatuses.netting = 'completed'
      newStatuses.compliance = 'completed'
      newStatuses.routing = 'completed'
      newStatuses.swift = 'completed'
      newStatuses.accounting = status === 'CORE_FAILED' ? 'failed' : 
                               status === 'CORE_SUCCESS' ? 'completed' : 'current'
      if (status === 'CORE_SUCCESS') {
        newStatuses.completed = 'completed'
        currentStage.value = 'completed'
      } else {
        currentStage.value = 'accounting'
      }
    }
  }

  stageStatuses.value = newStatuses
}

const formatDirection = (direction) => {
  return direction === 'RECEIVE' ? '收' : '付'
}

const formatAmount = (amount) => {
  return new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const formatStatus = (status) => {
  const statusMap = {
    'PENDING_AML': '待反洗钱检查',
    'AML_APPROVED': '反洗钱通过',
    'AML_REJECTED': '反洗钱拒绝',
    'PENDING_SWIFT': '待SWIFT发报',
    'SWIFT_SENT': 'SWIFT已发送',
    'SWIFT_FAILED': 'SWIFT发送失败',
    'PENDING_CORE': '待核心入账',
    'CORE_SUCCESS': '核心入账成功',
    'CORE_FAILED': '核心入账失败',
    'CORE_UNKNOWN': '核心入账状态不明'
  }
  return statusMap[status] || status
}

const getStatusClass = (status) => {
  if (status === 'CORE_SUCCESS' || status === 'AML_APPROVED' || status === 'SWIFT_SENT') {
    return 'status-success'
  } else if (status === 'CORE_FAILED' || status === 'AML_REJECTED' || status === 'SWIFT_FAILED') {
    return 'status-failed'
  } else if (status === 'CORE_UNKNOWN') {
    return 'status-unknown'
  } else {
    return 'status-pending'
  }
}

const handleClose = () => {
  router.push({ name: 'cash-flow-summary' })
}

const handleEscKey = (event) => {
  if (event.key === 'Escape') {
    handleClose()
  }
}

// Lifecycle
onMounted(() => {
  loadCashFlowDetail()
  window.addEventListener('keydown', handleEscKey)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleEscKey)
})
</script>

<style scoped>
.cash-flow-detail-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.cash-flow-detail-modal {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 1200px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 2px solid #D32F2F;
  background: #f5f5f5;
  border-radius: 8px 8px 0 0;
}

.modal-header h2 {
  color: #D32F2F;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e0e0e0;
  color: #333;
}

.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.basic-info,
.progress-section,
.guide-section {
  margin-bottom: 2rem;
}

.basic-info h3,
.progress-section h3,
.guide-section h3 {
  color: #D32F2F;
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #D32F2F;
}

.account-info {
  margin-top: 1.5rem;
}

.account-info h4 {
  color: #666;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.info-item {
  display: flex;
  padding: 0.75rem;
  background: #f9f9f9;
  border-radius: 4px;
}

.info-label {
  font-weight: 500;
  color: #666;
  min-width: 120px;
}

.info-value {
  color: #333;
  font-weight: 500;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.status-success {
  background: #4CAF50;
  color: white;
}

.status-failed {
  background: #f44336;
  color: white;
}

.status-unknown {
  background: #FF9800;
  color: white;
}

.status-pending {
  background: #2196F3;
  color: white;
}

.progress-indicator {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e0e0e0;
}

.progress-indicator h4 {
  color: #666;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.settlement-progress-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #e0e0e0;
}

/* Responsive */
@media (max-width: 1024px) {
  .cash-flow-detail-overlay {
    padding: 1rem;
  }

  .cash-flow-detail-modal {
    max-width: 100%;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .modal-header {
    padding: 1rem;
  }

  .modal-header h2 {
    font-size: 1.25rem;
  }

  .modal-content {
    padding: 1rem;
  }
}
</style>
