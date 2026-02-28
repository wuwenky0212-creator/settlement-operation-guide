<template>
  <div class="accounting-info-tab">
    <!-- Loading State -->
    <LoadingSpinner v-if="loading" />

    <!-- Error State -->
    <MessageAlert
      v-if="error"
      type="error"
      :message="error"
      @close="error = null"
    />

    <!-- Accounting Records Table -->
    <div v-if="!loading && accountingRecords.length > 0">
      <!-- Amount Summary -->
      <div v-if="amountSummary" class="amount-summary">
        <h3 class="summary-title">金额汇总</h3>
        <div class="summary-grid">
          <div
            v-for="(summary, currency) in amountSummary"
            :key="currency"
            class="summary-item"
          >
            <span class="currency">{{ currency }}</span>
            <div class="summary-amounts">
              <span class="debit">借方: {{ formatAmount(summary.debit) }}</span>
              <span class="credit">贷方: {{ formatAmount(summary.credit) }}</span>
              <span class="net">净额: {{ formatAmount(summary.net) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Accounting Records Table -->
      <DataTable
        :columns="accountingColumns"
        :data="accountingRecords"
        :loading="loading"
      />

      <!-- Pagination -->
      <PaginationComponent
        :current-page="pagination.currentPage"
        :total-pages="pagination.totalPages"
        :total-records="pagination.totalRecords"
        :page-size="pagination.pageSize"
        :page-size-options="[15, 20, 50]"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
      />
    </div>

    <!-- No Records Message -->
    <div v-if="!loading && accountingRecords.length === 0" class="no-records">
      <p>该交易暂无账务记录</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps } from 'vue'
import apiClient from '@/api/client'
import DataTable from '@/components/DataTable.vue'
import PaginationComponent from '@/components/PaginationComponent.vue'
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
const accountingRecords = ref([])
const amountSummary = ref(null)
const pagination = ref({
  currentPage: 1,
  totalPages: 0,
  totalRecords: 0,
  pageSize: 15
})

// Accounting columns configuration
const accountingColumns = [
  { key: 'voucher_id', label: '传票号', width: '120px' },
  { key: 'actual_accounting_date', label: '实际记账日', width: '120px', format: 'date' },
  { key: 'planned_accounting_date', label: '计划记账日', width: '120px', format: 'date' },
  { key: 'event_number', label: '事件号', width: '100px' },
  { key: 'debit_credit_indicator', label: '借贷方向', width: '80px' },
  { key: 'currency', label: '货币', width: '80px' },
  { key: 'account_subject', label: '科目', width: '150px' },
  { key: 'transaction_amount', label: '交易金额', width: '120px', format: 'amount' }
]

// Methods
const loadAccountingRecords = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await apiClient.get(`/transactions/${props.transactionId}/accounting-records`, {
      params: {
        page: pagination.value.currentPage,
        page_size: pagination.value.pageSize
      }
    })

    accountingRecords.value = response.data
    pagination.value = {
      currentPage: response.pagination.current_page,
      totalPages: response.pagination.total_pages,
      totalRecords: response.pagination.total_records,
      pageSize: response.pagination.page_size
    }

    // Load amount summary
    await loadAmountSummary()
  } catch (err) {
    console.error('Load accounting records error:', err)
    error.value = err.response?.data?.message || '加载账务记录失败'
    accountingRecords.value = []
  } finally {
    loading.value = false
  }
}

const loadAmountSummary = async () => {
  try {
    const response = await apiClient.get(`/transactions/${props.transactionId}/accounting-summary`)
    amountSummary.value = response
  } catch (err) {
    console.error('Load amount summary error:', err)
    // Don't show error for summary, it's optional
  }
}

const handlePageChange = (page) => {
  pagination.value.currentPage = page
  loadAccountingRecords()
}

const handlePageSizeChange = (pageSize) => {
  pagination.value.pageSize = pageSize
  pagination.value.currentPage = 1
  loadAccountingRecords()
}

const formatAmount = (amount) => {
  if (!amount && amount !== 0) return '-'
  return new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

// Lifecycle
onMounted(() => {
  loadAccountingRecords()
})
</script>

<style scoped>
.accounting-info-tab {
  min-height: 300px;
}

.amount-summary {
  background: #f9f9f9;
  border-radius: 4px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.summary-title {
  color: #D32F2F;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #D32F2F;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.summary-item {
  background: white;
  border-radius: 4px;
  padding: 1rem;
  border: 1px solid #e0e0e0;
}

.currency {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 0.5rem;
}

.summary-amounts {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-amounts span {
  font-size: 0.875rem;
}

.debit {
  color: #D32F2F;
}

.credit {
  color: #4CAF50;
}

.net {
  color: #333;
  font-weight: 600;
}

.no-records {
  text-align: center;
  padding: 3rem;
  color: #666;
  background: #f9f9f9;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
