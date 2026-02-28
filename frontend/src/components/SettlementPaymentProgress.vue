<template>
  <div class="settlement-payment-progress">
    <h4 class="progress-title">结算支付进度跟踪</h4>
    
    <div class="progress-flow">
      <!-- Stage 1: 清算轧差 -->
      <div class="stage-card">
        <div class="stage-icon" :class="getStageIconClass('netting')">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 11H15M9 15H15M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543 3 7 3H12.5858C12.851 3 13.1054 3.10536 13.2929 3.29289L18.7071 8.70711C18.8946 8.89464 19 9.149 19 9.41421V19C19 20.1046 18.1046 21 17 21Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stage-content">
          <div class="stage-header">
            <span class="stage-badge">检查前置条件</span>
          </div>
          <h5 class="stage-title">清算轧差</h5>
          <p class="stage-subtitle">轧差类型：自动/手工</p>
          <p class="stage-subtitle">自动轧差头寸可用性检查</p>
          
          <div class="stage-actions">
            <div class="action-item">
              <span class="action-icon">🔧</span>
              <span class="action-text">手工轧差 / 查询</span>
            </div>
          </div>
          
          <div class="stage-status" :class="getStageStatusClass('netting')">
            <span class="status-icon">{{ getStatusIcon('netting') }}</span>
            <span class="status-text">{{ getStatusText('netting') }}</span>
          </div>
        </div>
      </div>

      <!-- Arrow -->
      <div class="flow-arrow">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <!-- Stage 2: 合规准入 -->
      <div class="stage-card">
        <div class="stage-icon" :class="getStageIconClass('compliance')">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stage-content">
          <div class="stage-header">
            <span class="stage-badge">合规检查通过</span>
          </div>
          <h5 class="stage-title">合规准入</h5>
          <p class="stage-subtitle">风险检查</p>
          <p class="stage-subtitle">反洗钱检查 / 审批</p>
          
          <div class="stage-actions">
            <div class="action-item warning">
              <span class="action-icon">⚠️</span>
              <span class="action-text">系统拦截，禁止发报</span>
            </div>
            <div class="action-item">
              <span class="action-icon">👤</span>
              <span class="action-text">规避收付审批</span>
            </div>
          </div>
          
          <div class="stage-status" :class="getStageStatusClass('compliance')">
            <span class="status-icon">{{ getStatusIcon('compliance') }}</span>
            <span class="status-text">{{ getStatusText('compliance') }}</span>
          </div>
        </div>
      </div>

      <!-- Arrow -->
      <div class="flow-arrow">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <!-- Stage 3: 报文发送分流 -->
      <div class="stage-card">
        <div class="stage-icon" :class="getStageIconClass('routing')">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 7V3M16 7V3M7 11H17M5 21H19C20.1046 21 21 20.1046 21 19V7C21 5.89543 20.1046 5 19 5H5C3.89543 5 3 5.89543 3 7V19C3 20.1046 3.89543 21 5 21Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stage-content">
          <div class="stage-header">
            <span class="stage-badge">SWIFT</span>
          </div>
          <h5 class="stage-title">报文发送分流</h5>
          <p class="stage-subtitle">维护送报审批</p>
          <p class="stage-subtitle">报文类型：自动/手工审批</p>
          
          <div class="stage-branches">
            <div class="branch-item">
              <span class="branch-label">人工发报审批</span>
            </div>
            <div class="branch-item">
              <span class="branch-label">规避收付审批</span>
            </div>
            <div class="branch-item highlight">
              <span class="branch-label">转至系统</span>
            </div>
            <div class="branch-item">
              <span class="branch-label">CBMNet (人工确认)</span>
            </div>
          </div>
          
          <div class="stage-status" :class="getStageStatusClass('routing')">
            <span class="status-icon">{{ getStatusIcon('routing') }}</span>
            <span class="status-text">{{ getStatusText('routing') }}</span>
          </div>
        </div>
      </div>

      <!-- Arrow -->
      <div class="flow-arrow">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <!-- Stage 4: SWIFT 传输层 -->
      <div class="stage-card">
        <div class="stage-icon" :class="getStageIconClass('swift')">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stage-content">
          <div class="stage-header">
            <span class="stage-badge">报文正式出库</span>
          </div>
          <h5 class="stage-title">SWIFT 传输层</h5>
          <p class="stage-subtitle">RMC → FTM 链路监控</p>
          <p class="stage-subtitle">报文发送状态监控</p>
          
          <div class="stage-actions">
            <div class="action-item">
              <span class="action-icon">📡</span>
              <span class="action-text">RMC 发送失败，人工排查</span>
            </div>
            <div class="action-item">
              <span class="action-icon">📡</span>
              <span class="action-text">FTM 发送失败，人工排查</span>
            </div>
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

      <!-- Stage 5: 核心入账 -->
      <div class="stage-card">
        <div class="stage-icon" :class="getStageIconClass('accounting')">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 10H21M7 15H8M12 15H13M6 19H18C19.1046 19 20 18.1046 20 17V7C20 5.89543 19.1046 5 18 5H6C4.89543 5 4 5.89543 4 7V17C4 18.1046 4.89543 19 6 19Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stage-content">
          <div class="stage-header">
            <span class="stage-badge">入账成功</span>
          </div>
          <h5 class="stage-title">核心入账</h5>
          <p class="stage-subtitle">内部账务扣款</p>
          <p class="stage-subtitle">建立账务至系统</p>
          
          <div class="stage-actions">
            <div class="action-item warning">
              <span class="action-icon">⚠️</span>
              <span class="action-text">强制账务失败，人工排查</span>
            </div>
            <div class="action-item warning">
              <span class="action-icon">⚠️</span>
              <span class="action-text">记账失败日志，人工排查</span>
            </div>
          </div>
          
          <div class="stage-status" :class="getStageStatusClass('accounting')">
            <span class="status-icon">{{ getStatusIcon('accounting') }}</span>
            <span class="status-text">{{ getStatusText('accounting') }}</span>
          </div>
        </div>
      </div>

      <!-- Arrow -->
      <div class="flow-arrow">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <!-- Stage 6: 结算完成 -->
      <div class="stage-card">
        <div class="stage-icon" :class="getStageIconClass('completed')">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stage-content">
          <div class="stage-header">
            <span class="stage-badge success">入账成功</span>
          </div>
          <h5 class="stage-title">结算完成</h5>
          <p class="stage-subtitle">Settled</p>
          <p class="stage-subtitle">资金如期到账</p>
          
          <div class="stage-status success">
            <span class="status-icon">✓</span>
            <span class="status-text">完成</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentStage: {
    type: String,
    default: 'netting' // netting, compliance, routing, swift, accounting, completed
  },
  stageStatuses: {
    type: Object,
    default: () => ({
      netting: 'pending',
      compliance: 'pending',
      routing: 'pending',
      swift: 'pending',
      accounting: 'pending',
      completed: 'pending'
    })
  }
})

const getStageIconClass = (stage) => {
  const status = props.stageStatuses[stage] || 'pending'
  return {
    'icon-completed': status === 'completed',
    'icon-current': status === 'current',
    'icon-pending': status === 'pending',
    'icon-failed': status === 'failed'
  }
}

const getStageStatusClass = (stage) => {
  const status = props.stageStatuses[stage] || 'pending'
  return {
    'status-completed': status === 'completed',
    'status-current': status === 'current',
    'status-pending': status === 'pending',
    'status-failed': status === 'failed'
  }
}

const getStatusIcon = (stage) => {
  const status = props.stageStatuses[stage] || 'pending'
  const icons = {
    completed: '✓',
    current: '⏳',
    pending: '○',
    failed: '✗'
  }
  return icons[status] || '○'
}

const getStatusText = (stage) => {
  const status = props.stageStatuses[stage] || 'pending'
  const texts = {
    completed: '已完成',
    current: '进行中',
    pending: '待处理',
    failed: '失败'
  }
  return texts[status] || '待处理'
}
</script>

<style scoped>
.settlement-payment-progress {
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

.stage-badge.success {
  background: #E8F5E9;
  color: #2E7D32;
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
  border-left: 3px solid #2196F3;
  font-size: 0.8125rem;
}

.action-item.warning {
  border-left-color: #FF9800;
  background: #FFF3E0;
}

.action-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.action-text {
  color: #666;
  line-height: 1.3;
}

.stage-branches {
  margin: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.branch-item {
  padding: 0.5rem;
  background: #f9f9f9;
  border-radius: 4px;
  border-left: 3px solid #e0e0e0;
  font-size: 0.8125rem;
}

.branch-item.highlight {
  border-left-color: #4CAF50;
  background: #E8F5E9;
}

.branch-label {
  color: #666;
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

.stage-status.success {
  background: #E8F5E9;
}

.stage-status.success .status-icon,
.stage-status.success .status-text {
  color: #4CAF50;
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
}

@media (max-width: 768px) {
  .settlement-payment-progress {
    padding: 1rem;
  }
  
  .progress-flow {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stage-card {
    flex: 1 1 auto;
  }
  
  .flow-arrow {
    flex: 0 0 40px;
    transform: rotate(90deg);
  }
}
</style>
