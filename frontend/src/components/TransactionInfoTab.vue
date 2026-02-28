<template>
  <div class="transaction-info-tab">
    <!-- Loading State -->
    <LoadingSpinner v-if="progressLoading" />

    <!-- 交易信息 -->
    <div class="info-section">
      <h3 class="section-title">交易信息</h3>
      <div class="info-grid">
        <div class="info-item">
          <label>货币对</label>
          <span>{{ transaction.currency_pair || '-' }}</span>
        </div>
        <div class="info-item">
          <label>BUY金额</label>
          <span class="amount buy">{{ formatAmount(transaction.buy_amount, transaction.buy_currency) }}</span>
        </div>
        <div class="info-item">
          <label>SELL金额</label>
          <span class="amount sell">{{ formatAmount(transaction.sell_amount, transaction.sell_currency) }}</span>
        </div>
        <div class="info-item">
          <label>即期汇率</label>
          <span>{{ transaction.spot_rate || '-' }}</span>
        </div>
        <div class="info-item">
          <label>点差</label>
          <span>{{ transaction.spread || '-' }}</span>
        </div>
        <div class="info-item">
          <label>成本汇率</label>
          <span>{{ transaction.cost_rate || '-' }}</span>
        </div>
        <div class="info-item">
          <label>分润金额</label>
          <span>{{ formatAmount(transaction.profit_amount, transaction.profit_currency) }}</span>
        </div>
        <div class="info-item">
          <label>交易日</label>
          <span>{{ formatDate(transaction.trade_date) }}</span>
        </div>
        <div class="info-item">
          <label>交易时间</label>
          <span>{{ formatTime(transaction.trade_time) }}</span>
        </div>
        <div class="info-item">
          <label>起息日</label>
          <span>{{ formatDate(transaction.value_date) }}</span>
        </div>
      </div>
    </div>

    <!-- 交易账户 -->
    <div class="info-section">
      <h3 class="section-title">交易账户</h3>
      <div class="info-grid">
        <div class="info-item">
          <label>账户</label>
          <span>{{ transaction.account || '-' }}</span>
        </div>
        <div class="info-item">
          <label>交易对手</label>
          <span>{{ formatCounterparty(transaction.counterparty, transaction.counterparty_code) }}</span>
        </div>
        <div class="info-item">
          <label>经纪商</label>
          <span>{{ transaction.broker || '-' }}</span>
        </div>
        <div class="info-item">
          <label>背对背账户</label>
          <span>{{ transaction.back_to_back_account || '-' }}</span>
        </div>
      </div>
    </div>

    <!-- 备注 -->
    <div class="info-section">
      <h3 class="section-title">备注</h3>
      <div class="info-grid">
        <div class="info-item">
          <label>交易性质</label>
          <span>{{ transaction.nature || '-' }}</span>
        </div>
        <div class="info-item">
          <label>外部流水号</label>
          <span>{{ transaction.external_id || '-' }}</span>
        </div>
        <div class="info-item">
          <label>交易目的</label>
          <span>{{ transaction.purpose || '-' }}</span>
        </div>
        <div class="info-item full-width">
          <label>备注</label>
          <span>{{ transaction.remarks || '-' }}</span>
        </div>
      </div>
    </div>

    <!-- 拆分信息 -->
    <div class="info-section">
      <h3 class="section-title">拆分信息</h3>
      <div class="info-grid">
        <div class="info-item">
          <label>交易拆分</label>
          <span>
            <input
              type="checkbox"
              :checked="transaction.is_split"
              disabled
            />
            拆分货币对
          </span>
        </div>
      </div>
    </div>

    <!-- 扩展字段 -->
    <div class="info-section">
      <h3 class="section-title">扩展字段</h3>
      <div class="info-grid">
        <div class="info-item">
          <label>我方收结算路径(USD)</label>
          <span>{{ transaction.our_receive_path_usd || '-' }}</span>
        </div>
        <div class="info-item">
          <label>对手方付结算路径(USD)</label>
          <span>{{ transaction.counterparty_pay_path_usd || '-' }}</span>
        </div>
        <div class="info-item">
          <label>我方付结算路径(CNY)</label>
          <span>{{ transaction.our_pay_path_cny || '-' }}</span>
        </div>
        <div class="info-item">
          <label>对手方收结算路径(CNY)</label>
          <span>{{ transaction.counterparty_receive_path_cny || '-' }}</span>
        </div>
        <div class="info-item">
          <label>清算方式</label>
          <span>{{ transaction.settlement_method || '-' }}</span>
        </div>
      </div>
    </div>

    <!-- 生命周期进度 -->
    <div v-if="progressSteps.length > 0" class="progress-section">
      <h3 class="section-title">生命周期进度</h3>
      <ProgressStepper :steps="progressSteps" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps } from 'vue'
import apiClient from '@/api/client'
import ProgressStepper from '@/components/ProgressStepper.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const props = defineProps({
  transaction: {
    type: Object,
    required: true
  }
})

// State
const progressLoading = ref(false)
const progressSteps = ref([])

// Methods
const loadProgress = async () => {
  if (!props.transaction?.transaction_id) return

  progressLoading.value = true
  try {
    const response = await apiClient.get(`/transactions/${props.transaction.transaction_id}/progress`)
    
    // Convert progress data to stepper format
    // Support both camelCase and snake_case from API
    const flowData = response?.flowVisualization || response?.flow_visualization
    if (flowData) {
      progressSteps.value = flowData.map(node => ({
        label: node.name,
        status: node.status.toLowerCase() // 'COMPLETED' -> 'completed'
      }))
    }
  } catch (err) {
    console.error('Load progress error:', err)
    // Silently fail - progress is optional
  } finally {
    progressLoading.value = false
  }
}

// Helper functions
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  return timeStr
}

const formatAmount = (amount, currency) => {
  if (!amount) return '-'
  const formatted = new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
  return currency ? `${formatted} ${currency}` : formatted
}

const formatCounterparty = (name, code) => {
  if (!name && !code) return '-'
  if (name && code) return `${name} (${code})`
  return name || code
}

// Lifecycle
onMounted(() => {
  loadProgress()
})
</script>

<style scoped>
.transaction-info-tab {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.info-section {
  background: #f9f9f9;
  border-radius: 4px;
  padding: 1.5rem;
}

.section-title {
  color: #D32F2F;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #D32F2F;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item label {
  font-size: 0.875rem;
  color: #666;
  font-weight: 500;
}

.info-item span {
  font-size: 0.9375rem;
  color: #333;
}

.amount {
  font-weight: 600;
}

.amount.buy {
  color: #4CAF50;
}

.amount.sell {
  color: #D32F2F;
}

input[type="checkbox"] {
  margin-right: 0.5rem;
}

.progress-section {
  background: #f9f9f9;
  border-radius: 4px;
  padding: 1.5rem;
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
