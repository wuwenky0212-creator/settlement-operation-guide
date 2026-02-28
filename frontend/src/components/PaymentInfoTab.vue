<template>
  <div class="payment-info-tab">
    <!-- Loading State -->
    <LoadingSpinner v-if="loading" />

    <!-- Error State -->
    <MessageAlert
      v-if="error"
      type="error"
      :message="error"
      @close="error = null"
    />

    <!-- Payment Info Content -->
    <div v-if="!loading && paymentInfo">
      <!-- 清算方式 -->
      <div class="info-section">
        <h3 class="section-title">清算方式</h3>
        
        <!-- 我行信息 -->
        <div class="subsection">
          <h4 class="subsection-title">我行</h4>
          <div class="info-grid">
            <div class="info-item">
              <label>开户行</label>
              <span>{{ paymentInfo.our_bank_name || '-' }}</span>
            </div>
            <div class="info-item">
              <label>开户行号</label>
              <span>{{ paymentInfo.our_bank_code || '-' }}</span>
            </div>
            <div class="info-item">
              <label>户名</label>
              <span>{{ paymentInfo.our_account_name || '-' }}</span>
            </div>
            <div class="info-item">
              <label>账号</label>
              <span>{{ paymentInfo.our_account_number || '-' }}</span>
            </div>
          </div>
        </div>

        <!-- 对手方信息 -->
        <div class="subsection">
          <h4 class="subsection-title">对手方</h4>
          <div class="info-grid">
            <div class="info-item">
              <label>开户行</label>
              <span>{{ paymentInfo.counterparty_bank_name || '-' }}</span>
            </div>
            <div class="info-item">
              <label>开户行号</label>
              <span>{{ paymentInfo.counterparty_bank_code || '-' }}</span>
            </div>
            <div class="info-item">
              <label>户名</label>
              <span>{{ paymentInfo.counterparty_account_name || '-' }}</span>
            </div>
            <div class="info-item">
              <label>账号</label>
              <span>{{ paymentInfo.counterparty_account_number || '-' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 支付信息 -->
      <div class="info-section">
        <h3 class="section-title">支付信息</h3>
        
        <!-- 支付记录列表 -->
        <div v-if="paymentInfo.payment_records && paymentInfo.payment_records.length > 0">
          <div
            v-for="(record, index) in paymentInfo.payment_records"
            :key="index"
            class="payment-record"
          >
            <h4 class="record-title">支付记录 {{ index + 1 }}</h4>
            <div class="info-grid">
              <div class="info-item">
                <label>指令ID</label>
                <span>{{ record.instruction_id || '-' }}</span>
              </div>
              <div class="info-item">
                <label>支付日期</label>
                <span>{{ formatDate(record.payment_date) }}</span>
              </div>
              <div class="info-item">
                <label>报文类型</label>
                <span>{{ record.message_type || '-' }}</span>
              </div>
              <div class="info-item">
                <label>币种</label>
                <span>{{ record.currency || '-' }}</span>
              </div>
              <div class="info-item">
                <label>金额</label>
                <span class="amount">{{ formatAmount(record.amount, record.currency) }}</span>
              </div>
              <div class="info-item">
                <label>报文发送人</label>
                <span>{{ record.message_sender || '-' }}</span>
              </div>
              <div class="info-item">
                <label>报文发送时间</label>
                <span>{{ formatDateTime(record.message_sent_time) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 单条支付信息 -->
        <div v-else class="info-grid">
          <div class="info-item">
            <label>指令ID</label>
            <span>{{ paymentInfo.instruction_id || '-' }}</span>
          </div>
          <div class="info-item">
            <label>支付日期</label>
            <span>{{ formatDate(paymentInfo.payment_date) }}</span>
          </div>
          <div class="info-item">
            <label>报文类型</label>
            <span>{{ paymentInfo.message_type || '-' }}</span>
          </div>
          <div class="info-item">
            <label>币种</label>
            <span>{{ paymentInfo.currency || '-' }}</span>
          </div>
          <div class="info-item">
            <label>金额</label>
            <span class="amount">{{ formatAmount(paymentInfo.amount, paymentInfo.currency) }}</span>
          </div>
          <div class="info-item">
            <label>报文发送人</label>
            <span>{{ paymentInfo.message_sender || '-' }}</span>
          </div>
          <div class="info-item">
            <label>报文发送时间</label>
            <span>{{ formatDateTime(paymentInfo.message_sent_time) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- No Payment Info Message -->
    <div v-if="!loading && !paymentInfo" class="no-payment-info">
      <p>该交易暂无账务信息</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps } from 'vue'
import apiClient from '@/api/client'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import MessageAlert from '@/components/MessageAlert.vue'

const props = defineProps({
  transactionId: {
    type: String,
    required: true
  }
})

// State
const loading = ref(false)
const error = ref(null)
const paymentInfo = ref(null)

// Methods
const loadPaymentInfo = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await apiClient.get(`/transactions/${props.transactionId}/payment-info`)
    paymentInfo.value = response
  } catch (err) {
    console.error('Load payment info error:', err)
    if (err.response?.status === 404) {
      paymentInfo.value = null
    } else {
      error.value = err.response?.data?.message || '加载支付信息失败'
    }
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return '-'
  const date = new Date(dateTimeStr)
  return date.toLocaleString('zh-CN')
}

const formatAmount = (amount, currency) => {
  if (!amount) return '-'
  const formatted = new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
  return currency ? `${formatted} ${currency}` : formatted
}

// Lifecycle
onMounted(() => {
  loadPaymentInfo()
})
</script>

<style scoped>
.payment-info-tab {
  min-height: 300px;
}

.info-section {
  background: #f9f9f9;
  border-radius: 4px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.section-title {
  color: #D32F2F;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #D32F2F;
}

.subsection {
  margin-bottom: 1.5rem;
}

.subsection:last-child {
  margin-bottom: 0;
}

.subsection-title {
  color: #666;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
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
  color: #4CAF50;
}

.payment-record {
  background: white;
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid #e0e0e0;
}

.payment-record:last-child {
  margin-bottom: 0;
}

.record-title {
  color: #333;
  font-size: 0.9375rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
}

.no-payment-info {
  text-align: center;
  padding: 3rem;
  color: #666;
  background: #f9f9f9;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
