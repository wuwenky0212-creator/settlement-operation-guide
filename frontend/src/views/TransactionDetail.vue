<template>
  <div class="transaction-detail-overlay" @click.self="handleClose">
    <div class="transaction-detail-modal">
      <!-- Modal Header -->
      <div class="modal-header">
        <h2>交易生命周期</h2>
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
      <div v-if="!loading && transactionDetail" class="modal-content">
        <!-- Tabs -->
        <TabsComponent
          :tabs="tabs"
          :active-tab="activeTab"
          @tab-change="handleTabChange"
        />

        <!-- Tab Content -->
        <div class="tab-content">
          <!-- 交易信息 Tab -->
          <div v-show="activeTab === 'transaction-info'" class="tab-pane">
            <TransactionInfoTab :transaction="transactionDetail" />
          </div>

          <!-- 事件信息 Tab -->
          <div v-show="activeTab === 'event-info'" class="tab-pane">
            <EventInfoTab :external-id="externalId" />
          </div>

          <!-- 支付信息 Tab -->
          <div v-show="activeTab === 'payment-info'" class="tab-pane">
            <PaymentInfoTab :transaction-id="transactionDetail.transaction_id" />
          </div>

          <!-- 账务信息 Tab -->
          <div v-show="activeTab === 'accounting-info'" class="tab-pane">
            <AccountingInfoTab :transaction-id="transactionDetail.transaction_id" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'
import TabsComponent from '@/components/TabsComponent.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import MessageAlert from '@/components/MessageAlert.vue'
import TransactionInfoTab from '@/components/TransactionInfoTab.vue'
import EventInfoTab from '@/components/EventInfoTab.vue'
import PaymentInfoTab from '@/components/PaymentInfoTab.vue'
import AccountingInfoTab from '@/components/AccountingInfoTab.vue'

const route = useRoute()
const router = useRouter()

// Props from route
const externalId = ref(route.params.externalId)

// State
const loading = ref(false)
const error = ref(null)
const transactionDetail = ref(null)
const activeTab = ref('transaction-info')

// Tabs configuration
const tabs = [
  { id: 'transaction-info', label: '交易信息' },
  { id: 'event-info', label: '事件信息' },
  { id: 'payment-info', label: '支付信息' },
  { id: 'accounting-info', label: '账务信息' }
]

// Methods
const loadTransactionDetail = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await apiClient.get(`/transactions/${externalId.value}`)
    transactionDetail.value = response
  } catch (err) {
    console.error('Load transaction detail error:', err)
    error.value = err.response?.data?.message || '加载交易详情失败'
  } finally {
    loading.value = false
  }
}

const handleTabChange = (tabId) => {
  activeTab.value = tabId
}

const handleClose = () => {
  router.push({ name: 'transaction-summary' })
}

const handleEscKey = (event) => {
  if (event.key === 'Escape') {
    handleClose()
  }
}

// Lifecycle
onMounted(() => {
  loadTransactionDetail()
  window.addEventListener('keydown', handleEscKey)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleEscKey)
})
</script>

<style scoped>
.transaction-detail-overlay {
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

.transaction-detail-modal {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 1400px;
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
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.tab-pane {
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Responsive */
@media (max-width: 1024px) {
  .transaction-detail-overlay {
    padding: 1rem;
  }

  .transaction-detail-modal {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .modal-header {
    padding: 1rem;
  }

  .modal-header h2 {
    font-size: 1.25rem;
  }

  .tab-content {
    padding: 1rem;
  }
}
</style>
