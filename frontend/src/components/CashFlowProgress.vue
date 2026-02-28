<template>
  <div class="cash-flow-progress">
    <!-- Polling Status Indicator -->
    <div v-if="isPolling" class="polling-indicator">
      <span class="polling-dot"></span>
      <span class="polling-text">实时更新中</span>
      <span v-if="lastUpdate" class="last-update">
        最后更新: {{ formatLastUpdate(lastUpdate) }}
      </span>
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

    <!-- Update Notification -->
    <transition name="fade">
      <div v-if="showUpdateNotification" class="update-notification">
        <span>✓ 状态已更新</span>
      </div>
    </transition>

    <!-- Progress Content -->
    <div v-if="!loading && progress" class="progress-content">
      <!-- Current Progress Summary -->
      <div class="progress-summary">
        <div class="summary-item">
          <span class="summary-label">当前阶段:</span>
          <span class="summary-value">{{ progress.current_stage }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">当前状态:</span>
          <span class="summary-value status-badge" :class="getStatusClass(progress.current_status)">
            {{ progress.current_status }}
          </span>
        </div>
        <div class="summary-item">
          <span class="summary-label">发送路径:</span>
          <span class="summary-value">{{ progress.sending_route }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">进度:</span>
          <span class="summary-value">{{ progress.progress_percentage }}%</span>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="progress-bar-container">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: progress.progress_percentage + '%' }"
          ></div>
        </div>
        <span class="progress-text">{{ progress.progress_percentage }}%</span>
      </div>

      <!-- 4-Stage Flow Visualization -->
      <div class="stages-container">
        <!-- Stage 1: 清算轧差 -->
        <div v-if="progress.netting_stage" class="stage-section">
          <h4 class="stage-title">阶段1: 清算轧差</h4>
          <div class="stage-content">
            <!-- Prerequisite Check -->
            <div v-if="progress.netting_stage.prerequisite_check" class="prerequisite-check">
              <div class="check-item">
                <span class="check-label">产品类型:</span>
                <span class="check-value">{{ progress.netting_stage.prerequisite_check.product_type }}</span>
              </div>
              <div class="check-item">
                <span class="check-label">前置条件:</span>
                <span class="check-value">{{ progress.netting_stage.prerequisite_check.required_condition }}</span>
              </div>
              <div class="check-item">
                <span class="check-label">条件满足:</span>
                <span class="check-value" :class="progress.netting_stage.prerequisite_check.condition_met ? 'text-success' : 'text-error'">
                  {{ progress.netting_stage.prerequisite_check.condition_met ? '是' : '否' }}
                </span>
              </div>
            </div>
            
            <div class="stage-status">
              <span class="status-label">轧差类型:</span>
              <span class="status-value">{{ progress.netting_stage.netting_type === 'AUTO' ? '自动轧差' : '手工轧差' }}</span>
            </div>
            <div class="stage-status">
              <span class="status-label">状态:</span>
              <span class="status-badge" :class="getStatusClass(progress.netting_stage.status)">
                {{ progress.netting_stage.status }}
              </span>
            </div>
            <div v-if="progress.netting_stage.timestamp" class="stage-time">
              完成时间: {{ formatDateTime(progress.netting_stage.timestamp) }}
            </div>
          </div>
        </div>

        <!-- Stage 2: 合规准入 -->
        <div v-if="progress.compliance_stage" class="stage-section">
          <h4 class="stage-title">阶段2: 合规准入</h4>
          <div class="stage-content">
            <!-- AML Check -->
            <div v-if="progress.compliance_stage.aml_check" class="sub-stage">
              <div class="sub-stage-header">
                <span class="sub-stage-name">反洗钱检查</span>
                <span class="status-badge" :class="getStatusClass(progress.compliance_stage.aml_check.status)">
                  {{ formatComplianceStatus(progress.compliance_stage.aml_check.status) }}
                </span>
              </div>
              <div v-if="progress.compliance_stage.aml_check.message" class="sub-stage-message">
                {{ progress.compliance_stage.aml_check.message }}
              </div>
              <div v-if="progress.compliance_stage.aml_check.timestamp" class="sub-stage-time">
                {{ formatDateTime(progress.compliance_stage.aml_check.timestamp) }}
              </div>
            </div>

            <!-- Route Decision -->
            <div v-if="progress.compliance_stage.route_decision" class="sub-stage">
              <div class="sub-stage-header">
                <span class="sub-stage-name">路径决策</span>
                <span class="route-badge">{{ progress.compliance_stage.route_decision.route }}</span>
              </div>
              <div v-if="progress.compliance_stage.route_decision.timestamp" class="sub-stage-time">
                {{ formatDateTime(progress.compliance_stage.route_decision.timestamp) }}
              </div>
            </div>

            <!-- Manual Approval -->
            <div v-if="progress.compliance_stage.manual_approval" class="sub-stage">
              <div class="sub-stage-header">
                <span class="sub-stage-name">人工审批</span>
                <span class="status-badge" :class="getStatusClass(progress.compliance_stage.manual_approval.status)">
                  {{ formatApprovalStatus(progress.compliance_stage.manual_approval.status) }}
                </span>
              </div>
              <div v-if="progress.compliance_stage.manual_approval.approver" class="sub-stage-info">
                审批人: {{ progress.compliance_stage.manual_approval.approver }}
              </div>
              <div v-if="progress.compliance_stage.manual_approval.timestamp" class="sub-stage-time">
                {{ formatDateTime(progress.compliance_stage.manual_approval.timestamp) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Stage 3: 结算执行与回执 -->
        <div v-if="progress.settlement_stage" class="stage-section">
          <h4 class="stage-title">阶段3: 结算执行与回执</h4>
          <div class="stage-content">
            <!-- SWIFT Path: Transmission Layer -->
            <div v-if="progress.settlement_stage.transmission_layer" class="sub-stage-group">
              <div class="sub-stage-group-title">传输层回执 (SWIFT路径)</div>
              
              <!-- RMC -->
              <div class="sub-stage">
                <div class="sub-stage-header">
                  <span class="sub-stage-name">RMC 发送</span>
                  <span class="status-badge" :class="getStatusClass(progress.settlement_stage.transmission_layer.rmc.status)">
                    {{ formatTransmissionStatus(progress.settlement_stage.transmission_layer.rmc.status) }}
                  </span>
                </div>
                <div v-if="progress.settlement_stage.transmission_layer.rmc.message" class="sub-stage-message">
                  {{ progress.settlement_stage.transmission_layer.rmc.message }}
                </div>
                <div v-if="progress.settlement_stage.transmission_layer.rmc.timestamp" class="sub-stage-time">
                  {{ formatDateTime(progress.settlement_stage.transmission_layer.rmc.timestamp) }}
                </div>
              </div>

              <!-- FTM (only if RMC succeeded) -->
              <div v-if="progress.settlement_stage.transmission_layer.ftm" class="sub-stage">
                <div class="sub-stage-header">
                  <span class="sub-stage-name">FTM 处理</span>
                  <span class="status-badge" :class="getStatusClass(progress.settlement_stage.transmission_layer.ftm.status)">
                    {{ formatTransmissionStatus(progress.settlement_stage.transmission_layer.ftm.status) }}
                  </span>
                </div>
                <div v-if="progress.settlement_stage.transmission_layer.ftm.message" class="sub-stage-message">
                  {{ progress.settlement_stage.transmission_layer.ftm.message }}
                </div>
                <div v-if="progress.settlement_stage.transmission_layer.ftm.timestamp" class="sub-stage-time">
                  {{ formatDateTime(progress.settlement_stage.transmission_layer.ftm.timestamp) }}
                </div>
              </div>
            </div>

            <!-- CBMNet Path: Manual Confirm -->
            <div v-if="progress.settlement_stage.manual_confirm" class="sub-stage-group">
              <div class="sub-stage-group-title">人工确认 (CBMNet路径)</div>
              <div class="sub-stage">
                <div class="sub-stage-header">
                  <span class="sub-stage-name">人工确认</span>
                  <span class="status-badge" :class="getStatusClass(progress.settlement_stage.manual_confirm.status)">
                    {{ formatApprovalStatus(progress.settlement_stage.manual_confirm.status) }}
                  </span>
                </div>
                <div v-if="progress.settlement_stage.manual_confirm.operator" class="sub-stage-info">
                  操作员: {{ progress.settlement_stage.manual_confirm.operator }}
                </div>
                <div v-if="progress.settlement_stage.manual_confirm.timestamp" class="sub-stage-time">
                  {{ formatDateTime(progress.settlement_stage.manual_confirm.timestamp) }}
                </div>
              </div>
            </div>

            <!-- Accounting Layer -->
            <div class="sub-stage-group">
              <div class="sub-stage-group-title">账务层回执</div>
              <div class="sub-stage">
                <div class="sub-stage-header">
                  <span class="sub-stage-name">核心入账 ({{ progress.settlement_stage.accounting_layer.mode === 'AUTO' ? '自动' : '手动' }})</span>
                  <span class="status-badge" :class="getStatusClass(progress.settlement_stage.accounting_layer.status)">
                    {{ formatAccountingStatus(progress.settlement_stage.accounting_layer.status) }}
                  </span>
                </div>
                <div v-if="progress.settlement_stage.accounting_layer.message" class="sub-stage-message">
                  {{ progress.settlement_stage.accounting_layer.message }}
                </div>
                <div v-if="progress.settlement_stage.accounting_layer.timestamp" class="sub-stage-time">
                  {{ formatDateTime(progress.settlement_stage.accounting_layer.timestamp) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Stage 4: 结算撤销 -->
        <div v-if="progress.cancellation_stage" class="stage-section">
          <h4 class="stage-title">阶段4: 结算撤销</h4>
          <div class="stage-content">
            <!-- SWIFT Path: Transmission Layer -->
            <div v-if="progress.cancellation_stage.transmission_layer" class="sub-stage-group">
              <div class="sub-stage-group-title">传输层 (SWIFT路径)</div>
              
              <!-- RMC -->
              <div class="sub-stage">
                <div class="sub-stage-header">
                  <span class="sub-stage-name">撤销 RMC</span>
                  <span class="status-badge" :class="getStatusClass(progress.cancellation_stage.transmission_layer.rmc.status)">
                    {{ formatTransmissionStatus(progress.cancellation_stage.transmission_layer.rmc.status) }}
                  </span>
                </div>
                <div v-if="progress.cancellation_stage.transmission_layer.rmc.timestamp" class="sub-stage-time">
                  {{ formatDateTime(progress.cancellation_stage.transmission_layer.rmc.timestamp) }}
                </div>
              </div>

              <!-- FTM -->
              <div v-if="progress.cancellation_stage.transmission_layer.ftm" class="sub-stage">
                <div class="sub-stage-header">
                  <span class="sub-stage-name">撤销 FTM</span>
                  <span class="status-badge" :class="getStatusClass(progress.cancellation_stage.transmission_layer.ftm.status)">
                    {{ formatTransmissionStatus(progress.cancellation_stage.transmission_layer.ftm.status) }}
                  </span>
                </div>
                <div v-if="progress.cancellation_stage.transmission_layer.ftm.timestamp" class="sub-stage-time">
                  {{ formatDateTime(progress.cancellation_stage.transmission_layer.ftm.timestamp) }}
                </div>
              </div>
            </div>

            <!-- Reversal Processing -->
            <div class="sub-stage-group">
              <div class="sub-stage-group-title">资金冲正</div>
              <div class="sub-stage">
                <div class="sub-stage-header">
                  <span class="sub-stage-name">冲正处理</span>
                  <span class="status-badge" :class="getStatusClass(progress.cancellation_stage.reversal_processing.status)">
                    {{ formatAccountingStatus(progress.cancellation_stage.reversal_processing.status) }}
                  </span>
                </div>
                <div v-if="progress.cancellation_stage.reversal_processing.message" class="sub-stage-message">
                  {{ progress.cancellation_stage.reversal_processing.message }}
                </div>
                <div v-if="progress.cancellation_stage.reversal_processing.timestamp" class="sub-stage-time">
                  {{ formatDateTime(progress.cancellation_stage.reversal_processing.timestamp) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Operation Guide -->
      <div v-if="progress.operation_guide" class="operation-guide">
        <h4>操作指引</h4>
        <div class="guide-content">
          <div class="guide-action">
            <span class="guide-label">下一步操作:</span>
            <span class="guide-value">{{ progress.operation_guide.next_action }}</span>
          </div>
          <div v-if="progress.operation_guide.notes" class="guide-notes">
            <span class="guide-label">注意事项:</span>
            <span class="guide-value">{{ progress.operation_guide.notes }}</span>
          </div>
          <div v-if="progress.operation_guide.estimated_time" class="guide-time">
            <span class="guide-label">预计时间:</span>
            <span class="guide-value">{{ progress.operation_guide.estimated_time }}</span>
          </div>
          <div v-if="progress.operation_guide.action_entry" class="guide-entry">
            <button 
              v-if="progress.operation_guide.action_entry.type === 'BUTTON'"
              class="btn btn-primary"
              @click="handleActionEntry(progress.operation_guide.action_entry)"
            >
              {{ progress.operation_guide.action_entry.label }}
            </button>
            <a 
              v-else-if="progress.operation_guide.action_entry.type === 'LINK'"
              :href="progress.operation_guide.action_entry.url"
              class="guide-link"
              target="_blank"
            >
              {{ progress.operation_guide.action_entry.label }} →
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'
import { usePolling } from '@/composables/usePolling'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import MessageAlert from '@/components/MessageAlert.vue'

const props = defineProps({
  cashFlowId: {
    type: String,
    required: true
  }
})

// State
const loading = ref(false)
const error = ref(null)
const progress = ref(null)
const showUpdateNotification = ref(false)

// Polling setup (10 second interval)
const { isPolling, lastUpdate, startPolling, stopPolling } = usePolling(
  async () => {
    await refreshProgress()
  },
  10000
)

// Methods
const loadProgress = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await apiClient.get(`/cash-flows/${props.cashFlowId}/progress`)
    progress.value = response
  } catch (err) {
    console.error('Load progress error:', err)
    error.value = err.response?.data?.message || '加载进度信息失败'
  } finally {
    loading.value = false
  }
}

const refreshProgress = async () => {
  try {
    const response = await apiClient.get(`/cash-flows/${props.cashFlowId}/progress`)
    const hasChanged = JSON.stringify(progress.value) !== JSON.stringify(response)
    
    if (hasChanged) {
      progress.value = response
      showUpdateNotification.value = true
      setTimeout(() => {
        showUpdateNotification.value = false
      }, 3000)
    }
  } catch (err) {
    console.error('Refresh progress error:', err)
  }
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const formatLastUpdate = (date) => {
  if (!date) return ''
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)
  
  if (diff < 60) return `${diff}秒前`
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const getStatusClass = (status) => {
  const statusUpper = String(status).toUpperCase()
  if (statusUpper === 'SUCCESS' || statusUpper === 'APPROVED' || status === '成功' || status === '通过') {
    return 'status-success'
  } else if (statusUpper === 'FAILED' || statusUpper === 'REJECTED' || statusUpper === 'BLOCKED' || status === '失败' || status === '拒绝' || status === '阻断') {
    return 'status-failed'
  } else if (statusUpper === 'PENDING' || statusUpper === 'WAITING' || status === '待处理' || status === '等待') {
    return 'status-waiting'
  } else if (statusUpper === 'PROCESSING' || statusUpper === 'SENDING' || statusUpper === 'CHECKING' || status === '处理中' || status === '发送中' || status === '校验中') {
    return 'status-processing'
  }
  return ''
}

const formatComplianceStatus = (status) => {
  const statusMap = {
    'CHECKING': '校验中',
    'APPROVED': '通过',
    'BLOCKED': '拦截'
  }
  return statusMap[status] || status
}

const formatApprovalStatus = (status) => {
  const statusMap = {
    'PENDING': '待审批',
    'APPROVED': '审批通过',
    'REJECTED': '审批拒绝'
  }
  return statusMap[status] || status
}

const formatTransmissionStatus = (status) => {
  const statusMap = {
    'SENDING': '发送中',
    'SUCCESS': '发送成功',
    'FAILED': '发送失败'
  }
  return statusMap[status] || status
}

const formatAccountingStatus = (status) => {
  const statusMap = {
    'PROCESSING': '处理中',
    'SUCCESS': '成功',
    'FAILED': '失败',
    'UNKNOWN': '状态不明'
  }
  return statusMap[status] || status
}

const handleActionEntry = (actionEntry) => {
  if (actionEntry.action) {
    console.log('Action:', actionEntry.action)
  } else if (actionEntry.url) {
    window.open(actionEntry.url, '_blank')
  }
}

onMounted(async () => {
  await loadProgress()
  startPolling()
})
</script>

<style scoped>
.cash-flow-progress {
  padding: 1rem;
  background: #fff;
}

.polling-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #E3F2FD;
  border-left: 4px solid #2196F3;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.polling-dot {
  width: 8px;
  height: 8px;
  background: #2196F3;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.polling-text {
  color: #1565C0;
  font-weight: 500;
}

.last-update {
  color: #666;
  margin-left: auto;
}

.update-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #4CAF50;
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.progress-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.progress-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-label {
  font-size: 0.875rem;
  color: #666;
}

.summary-value {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.875rem;
  width: fit-content;
}

.status-success { background: #4CAF50; color: white; }
.status-failed { background: #f44336; color: white; }
.status-waiting { background: #FF9800; color: white; }
.status-processing { background: #2196F3; color: white; }

.progress-bar-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.progress-bar {
  flex: 1;
  height: 24px;
  background: #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  transition: width 0.3s ease;
}

.progress-text {
  font-weight: 600;
  color: #333;
  min-width: 50px;
  text-align: right;
}

.stages-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.stage-section {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.stage-title {
  background: #f5f5f5;
  color: #333;
  font-size: 1rem;
  font-weight: 600;
  padding: 1rem;
  margin: 0;
  border-bottom: 1px solid #e0e0e0;
}

.stage-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.prerequisite-check {
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.check-item {
  display: flex;
  gap: 0.5rem;
}

.check-label {
  font-weight: 600;
  color: #666;
  min-width: 80px;
}

.check-value {
  color: #333;
}

.text-success { color: #4CAF50; font-weight: 600; }
.text-error { color: #f44336; font-weight: 600; }

.stage-status {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.status-label {
  font-weight: 600;
  color: #666;
}

.status-value {
  color: #333;
}

.stage-time {
  font-size: 0.875rem;
  color: #999;
}

.sub-stage-group {
  background: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.sub-stage-group-title {
  font-weight: 600;
  color: #666;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.sub-stage {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sub-stage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sub-stage-name {
  font-weight: 600;
  color: #333;
}

.sub-stage-message, .sub-stage-info {
  color: #666;
  font-size: 0.875rem;
}

.sub-stage-time {
  font-size: 0.875rem;
  color: #999;
}

.route-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.875rem;
  background: #2196F3;
  color: white;
  font-weight: 500;
}

.operation-guide {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 1rem;
}

.operation-guide h4 {
  color: #333;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.guide-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.guide-action, .guide-notes, .guide-time {
  display: flex;
  gap: 0.5rem;
}

.guide-label {
  font-weight: 600;
  color: #666;
  min-width: 100px;
}

.guide-value {
  color: #333;
  flex: 1;
}

.guide-entry {
  margin-top: 0.5rem;
}

.guide-link {
  color: #2196F3;
  text-decoration: none;
  font-weight: 500;
}

.guide-link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .progress-summary {
    grid-template-columns: 1fr;
  }
}
</style>
