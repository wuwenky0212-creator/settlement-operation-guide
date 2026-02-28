<template>
  <div class="transaction-lifecycle-progress">
    <h4 class="progress-title">交易生命周期进度跟踪</h4>
    
    <div class="progress-flow">
      <!-- Stage 1: 后台复核 -->
      <div class="stage-card">
        <div class="stage-icon" :class="getStageIconClass('review')">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V7C19 5.89543 18.1046 5 17 5H15M9 5C9 6.10457 9.89543 7 11 7H13C14.1046 7 15 6.10457 15 5M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5M12 12H15M12 16H15M9 12H9.01M9 16H9.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stage-content">
          <div class="stage-header">
            <span class="stage-badge">复核流程</span>
          </div>
          <h5 class="stage-title">后台复核</h5>
          <p class="stage-subtitle">Back-office Validation</p>
          <p class="stage-subtitle">结算员核对交易要素与清算路径</p>
          
          <div class="stage-actions">
            <div class="action-item">
              <span class="action-icon">✓</span>
              <span class="action-text">复核通过</span>
            </div>
            <div class="action-item terminated">
              <span class="action-icon">✗</span>
              <span class="action-text">流程终结（交易已删除）</span>
            </div>
          </div>
          
          <div class="stage-status" :class="getStageStatusClass('review')">
            <span class="status-icon">{{ getStatusIcon('review') }}</span>
            <span class="status-text">{{ getStatusText('review') }}</span>
            <span v-if="timestamps.review" class="status-time">{{ formatDateTime(timestamps.review) }}</span>
          </div>
        </div>
      </div>

      <!-- Arrow -->
      <div class="flow-arrow">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <!-- Stage 2: SWIFT证实回执状态 -->
      <div class="stage-card stage-card-wide">
        <div class="stage-icon" :class="getStageIconClass('swift')">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 8L10.89 13.26C11.2187 13.4793 11.6049 13.5963 12 13.5963C12.3951 13.5963 12.7813 13.4793 13.11 13.26L21 8M5 19H19C19.5304 19 20.0391 18.7893 20.4142 18.4142C20.7893 18.0391 21 17.5304 21 17V7C21 6.46957 20.7893 5.96086 20.4142 5.58579C20.0391 5.21071 19.5304 5 19 5H5C4.46957 5 3.96086 5.21071 3.58579 5.58579C3.21071 5.96086 3 6.46957 3 7V17C3 17.5304 3.21071 18.0391 3.58579 18.4142C3.96086 18.7893 4.46957 19 5 19Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stage-content">
          <div class="stage-header">
            <span class="stage-badge">RMC → FTM</span>
          </div>
          <h5 class="stage-title">SWIFT 证实回执状态</h5>
          <p class="stage-subtitle">SWIFT Confirmation Status</p>
          <p class="stage-subtitle">仅适用于外汇掉期和拆借交易</p>
          
          <!-- 子节点：RMC -->
          <div class="sub-stage-group">
            <div class="sub-stage-title">子节点1: RMC 发送</div>
            <div class="sub-stage">
              <div class="sub-stage-header">
                <span class="sub-stage-name">RMC 回执</span>
                <span class="status-badge" :class="getSubStageStatusClass('rmc')">
                  {{ getSubStageStatusText('rmc') }}
                </span>
              </div>
              <div v-if="rmcStatus === 'failed'" class="sub-stage-message error">
                <span class="message-icon">⚠️</span>
                <span>报文出口受阻（RMC失败），请检查报文规范</span>
              </div>
              <div v-if="timestamps.rmc" class="sub-stage-time">
                {{ formatDateTime(timestamps.rmc) }}
              </div>
            </div>
          </div>

          <!-- 子节点：FTM（仅当RMC成功时显示） -->
          <div v-if="rmcStatus === 'success'" class="sub-stage-group">
            <div class="sub-stage-title">子节点2: FTM 处理</div>
            <div class="sub-stage">
              <div class="sub-stage-header">
                <span class="sub-stage-name">FTM 回执</span>
                <span class="status-badge" :class="getSubStageStatusClass('ftm')">
                  {{ getSubStageStatusText('ftm') }}
                </span>
              </div>
              <div v-if="ftmStatus === 'failed'" class="sub-stage-message warning">
                <span class="message-icon">⚠️</span>
                <span>报文传输中断（FTM失败），请在待办中执行"补发处理"</span>
              </div>
              <div v-if="timestamps.ftm" class="sub-stage-time">
                {{ formatDateTime(timestamps.ftm) }}
              </div>
            </div>
          </div>

          <!-- RMC失败时的提示 -->
          <div v-if="rmcStatus === 'failed'" class="stage-blocked">
            <span class="blocked-icon">🚫</span>
            <span class="blocked-text">RMC失败，流程已阻断，无FTM回执</span>
          </div>
          
          <div class="stage-status" :class="getStageStatusClass('swift')">
            <span class="status-icon">{{ getStatusIcon('swift') }}</span>
            <span class="status-text">{{ getStatusText('swift') }}</span>
          </div>
        </div>
      </div>

      <!-- Arrow -->
      <div class="flow-arrow">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <!-- Stage 3: 证实匹配 -->
      <div class="stage-card">
        <div class="stage-icon" :class="getStageIconClass('matching')">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stage-content">
          <div class="stage-header">
            <span class="stage-badge">自动匹配 / 手动处理</span>
          </div>
          <h5 class="stage-title">证实匹配</h5>
          <p class="stage-subtitle">Confirmation Matching</p>
          <p class="stage-subtitle">系统或人工进行匹配处理</p>
          
          <div class="stage-actions">
            <div class="action-item">
              <span class="action-icon">✓</span>
              <span class="action-text">匹配成功</span>
            </div>
            <div class="action-item warning">
              <span class="action-icon">✋</span>
              <span class="action-text">手工处理（人工匹配/撤销）</span>
            </div>
          </div>
          
          <div class="stage-status" :class="getStageStatusClass('matching')">
            <span class="status-icon">{{ getStatusIcon('matching') }}</span>
            <span class="status-text">{{ getStatusText('matching') }}</span>
            <span v-if="timestamps.matching" class="status-time">{{ formatDateTime(timestamps.matching) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  transactionId: {
    type: String,
    default: ''
  },
  productType: {
    type: String,
    default: ''
  },
  // 主要阶段状态
  stageStatuses: {
    type: Object,
    default: () => ({
      review: 'pending',      // 后台复核: pending/in-review/approved/deleted
      swift: 'pending',        // SWIFT证实: pending/processing/success/failed/blocked
      matching: 'pending'      // 证实匹配: pending/matching/success/manual
    })
  },
  // SWIFT子节点状态
  rmcStatus: {
    type: String,
    default: 'pending'  // pending/processing/success/failed
  },
  ftmStatus: {
    type: String,
    default: 'pending'  // pending/processing/success/failed
  },
  // 时间戳
  timestamps: {
    type: Object,
    default: () => ({
      review: null,
      rmc: null,
      ftm: null,
      matching: null
    })
  }
})

const getStageIconClass = (stage) => {
  const status = props.stageStatuses[stage] || 'pending'
  return {
    'icon-completed': status === 'approved' || status === 'success',
    'icon-current': status === 'in-review' || status === 'processing' || status === 'matching',
    'icon-pending': status === 'pending',
    'icon-failed': status === 'failed' || status === 'blocked',
    'icon-terminated': status === 'deleted'
  }
}

const getStageStatusClass = (stage) => {
  const status = props.stageStatuses[stage] || 'pending'
  return {
    'status-completed': status === 'approved' || status === 'success',
    'status-current': status === 'in-review' || status === 'processing' || status === 'matching',
    'status-pending': status === 'pending',
    'status-failed': status === 'failed' || status === 'blocked',
    'status-terminated': status === 'deleted',
    'status-warning': status === 'manual'
  }
}

const getSubStageStatusClass = (subStage) => {
  const status = subStage === 'rmc' ? props.rmcStatus : props.ftmStatus
  return {
    'badge-success': status === 'success',
    'badge-processing': status === 'processing',
    'badge-pending': status === 'pending',
    'badge-failed': status === 'failed'
  }
}

const getSubStageStatusText = (subStage) => {
  const status = subStage === 'rmc' ? props.rmcStatus : props.ftmStatus
  const texts = {
    pending: '待处理',
    processing: '处理中',
    success: '成功',
    failed: '失败'
  }
  return texts[status] || '待处理'
}

const getStatusIcon = (stage) => {
  const status = props.stageStatuses[stage] || 'pending'
  const icons = {
    'approved': '✓',
    'success': '✓',
    'in-review': '⏳',
    'processing': '⏳',
    'matching': '⏳',
    'pending': '○',
    'failed': '✗',
    'blocked': '🚫',
    'deleted': '✗',
    'manual': '✋'
  }
  return icons[status] || '○'
}

const getStatusText = (stage) => {
  const status = props.stageStatuses[stage] || 'pending'
  
  if (stage === 'review') {
    const texts = {
      'pending': '待复核',
      'in-review': '复核中',
      'approved': '复核通过',
      'deleted': '交易已删除'
    }
    return texts[status] || '待复核'
  }
  
  if (stage === 'swift') {
    const texts = {
      'pending': '待处理',
      'processing': '处理中',
      'success': '发送成功',
      'failed': '发送失败',
      'blocked': '回执失败'
    }
    return texts[status] || '待处理'
  }
  
  if (stage === 'matching') {
    const texts = {
      'pending': '待匹配',
      'matching': '匹配中',
      'success': '匹配成功',
      'manual': '手工处理'
    }
    return texts[status] || '待匹配'
  }
  
  return '待处理'
}

const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return ''
  const date = new Date(dateTimeStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.transaction-lifecycle-progress {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.progress-title {
  color: #D32F2F;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #D32F2F;
}

.progress-flow {
  display: flex;
  align-items: stretch;
  gap: 1rem;
  overflow-x: auto;
  padding: 1rem 0;
}

.stage-card {
  flex: 0 0 280px;
  background: white;
  border-radius: 8px;
  border: 2px solid #e0e0e0;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stage-card-wide {
  flex: 0 0 360px;
}

.stage-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.stage-icon {
  width: 100%;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  transition: all 0.3s ease;
}

.stage-icon svg {
  width: 40px;
  height: 40px;
  color: #999;
}

.stage-icon.icon-completed {
  background: #E8F5E9;
}

.stage-icon.icon-completed svg {
  color: #4CAF50;
}

.stage-icon.icon-current {
  background: #E3F2FD;
}

.stage-icon.icon-current svg {
  color: #2196F3;
}

.stage-icon.icon-failed {
  background: #FFEBEE;
}

.stage-icon.icon-failed svg {
  color: #F44336;
}

.stage-icon.icon-terminated {
  background: #FFEBEE;
}

.stage-icon.icon-terminated svg {
  color: #D32F2F;
}

.stage-content {
  padding: 1rem;
}

.stage-header {
  margin-bottom: 0.75rem;
}

.stage-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #E3F2FD;
  color: #1976D2;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.stage-title {
  color: #333;
  font-size: 1rem;
  font-weight: 600;
  margin: 0.5rem 0 0.25rem 0;
}

.stage-subtitle {
  color: #666;
  font-size: 0.875rem;
  margin: 0.25rem 0;
  line-height: 1.4;
}

.stage-actions {
  margin: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f9f9f9;
  border-radius: 4px;
  border-left: 3px solid #4CAF50;
  font-size: 0.8125rem;
}

.action-item.warning {
  border-left-color: #FF9800;
  background: #FFF3E0;
}

.action-item.terminated {
  border-left-color: #F44336;
  background: #FFEBEE;
}

.action-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.action-text {
  color: #666;
  line-height: 1.3;
}

.sub-stage-group {
  margin: 1rem 0;
  padding: 0.75rem;
  background: #fafafa;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.sub-stage-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #666;
  margin-bottom: 0.75rem;
}

.sub-stage {
  background: white;
  border-radius: 4px;
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
}

.sub-stage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.sub-stage-name {
  font-weight: 600;
  color: #333;
  font-size: 0.875rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge-success {
  background: #E8F5E9;
  color: #2E7D32;
}

.badge-processing {
  background: #E3F2FD;
  color: #1565C0;
}

.badge-pending {
  background: #f5f5f5;
  color: #999;
}

.badge-failed {
  background: #FFEBEE;
  color: #C62828;
}

.sub-stage-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.8125rem;
  margin-top: 0.5rem;
}

.sub-stage-message.error {
  background: #FFEBEE;
  color: #C62828;
  border-left: 3px solid #F44336;
}

.sub-stage-message.warning {
  background: #FFF3E0;
  color: #E65100;
  border-left: 3px solid #FF9800;
}

.message-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.sub-stage-time {
  font-size: 0.75rem;
  color: #999;
  margin-top: 0.5rem;
}

.stage-blocked {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #FFEBEE;
  border-radius: 4px;
  border-left: 4px solid #F44336;
  margin: 1rem 0;
}

.blocked-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.blocked-text {
  color: #C62828;
  font-weight: 600;
  font-size: 0.875rem;
}

.stage-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f5f5f5;
  border-radius: 4px;
  margin-top: 1rem;
}

.status-icon {
  font-size: 1.125rem;
}

.status-text {
  font-weight: 600;
  color: #666;
  flex: 1;
}

.status-time {
  font-size: 0.75rem;
  color: #999;
}

.stage-status.status-completed {
  background: #E8F5E9;
}

.stage-status.status-completed .status-icon,
.stage-status.status-completed .status-text {
  color: #4CAF50;
}

.stage-status.status-current {
  background: #E3F2FD;
}

.stage-status.status-current .status-icon,
.stage-status.status-current .status-text {
  color: #2196F3;
}

.stage-status.status-failed {
  background: #FFEBEE;
}

.stage-status.status-failed .status-icon,
.stage-status.status-failed .status-text {
  color: #F44336;
}

.stage-status.status-terminated {
  background: #FFEBEE;
}

.stage-status.status-terminated .status-icon,
.stage-status.status-terminated .status-text {
  color: #D32F2F;
}

.stage-status.status-warning {
  background: #FFF3E0;
}

.stage-status.status-warning .status-icon,
.stage-status.status-warning .status-text {
  color: #E65100;
}

.flow-arrow {
  flex: 0 0 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.flow-arrow svg {
  width: 32px;
  height: 32px;
  color: #999;
}

/* Responsive */
@media (max-width: 1400px) {
  .progress-flow {
    justify-content: flex-start;
  }
  
  .stage-card {
    flex: 0 0 260px;
  }
  
  .stage-card-wide {
    flex: 0 0 340px;
  }
}

@media (max-width: 768px) {
  .transaction-lifecycle-progress {
    padding: 1rem;
  }
  
  .progress-flow {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stage-card,
  .stage-card-wide {
    flex: 1 1 auto;
  }
  
  .flow-arrow {
    flex: 0 0 40px;
    transform: rotate(90deg);
  }
}
</style>
