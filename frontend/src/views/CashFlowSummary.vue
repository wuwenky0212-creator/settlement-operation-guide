<template>
  <div class="cash-flow-summary">
    <!-- Query Form -->
    <div class="query-form">
      <h2>现金流查询</h2>
      
      <form @submit.prevent="handleQuery">
        <div class="form-grid">
          <!-- Row 1 -->
          <div class="form-group">
            <label for="transactionId">交易流水号</label>
            <input
              id="transactionId"
              v-model="queryForm.transactionId"
              type="text"
              placeholder="请输入交易流水号"
            />
          </div>

          <div class="form-group">
            <label for="cashFlowId">现金流内部ID</label>
            <input
              id="cashFlowId"
              v-model="queryForm.cashFlowId"
              type="text"
              placeholder="请输入现金流ID"
            />
          </div>

          <div class="form-group">
            <label for="paymentInfoId">收付信息ID</label>
            <input
              id="paymentInfoId"
              v-model="queryForm.paymentInfoId"
              type="text"
              placeholder="请输入收付信息ID"
            />
          </div>

          <div class="form-group">
            <label for="settlementId">结算内部ID</label>
            <input
              id="settlementId"
              v-model="queryForm.settlementId"
              type="text"
              placeholder="请输入结算ID"
            />
          </div>

          <!-- Row 2 -->
          <div class="form-group">
            <label for="direction">方向</label>
            <select id="direction" v-model="queryForm.direction">
              <option value="">全部</option>
              <option value="RECEIVE">收</option>
              <option value="PAY">付</option>
            </select>
          </div>

          <div class="form-group">
            <label for="currency">币种</label>
            <input
              id="currency"
              v-model="queryForm.currency"
              type="text"
              placeholder="如 CNY, USD, EUR"
              maxlength="3"
            />
          </div>

          <div class="form-group">
            <label for="amountMin">最小金额</label>
            <input
              id="amountMin"
              v-model.number="queryForm.amountMin"
              type="number"
              step="0.01"
              placeholder="请输入最小金额"
            />
          </div>

          <div class="form-group">
            <label for="amountMax">最大金额</label>
            <input
              id="amountMax"
              v-model.number="queryForm.amountMax"
              type="number"
              step="0.01"
              placeholder="请输入最大金额"
            />
          </div>

          <!-- Row 3 -->
          <div class="form-group">
            <label for="paymentDateFrom">收付日期起始</label>
            <input
              id="paymentDateFrom"
              v-model="queryForm.paymentDateFrom"
              type="date"
            />
          </div>

          <div class="form-group">
            <label for="paymentDateTo">收付日期结束</label>
            <input
              id="paymentDateTo"
              v-model="queryForm.paymentDateTo"
              type="date"
            />
          </div>

          <div class="form-group">
            <label for="status">状态</label>
            <select id="status" v-model="queryForm.status">
              <option value="">全部</option>
              <option value="PENDING_AML">待反洗钱检查</option>
              <option value="AML_APPROVED">反洗钱通过</option>
              <option value="AML_REJECTED">反洗钱拒绝</option>
              <option value="PENDING_SWIFT">待SWIFT发报</option>
              <option value="SWIFT_SENT">SWIFT已发送</option>
              <option value="SWIFT_FAILED">SWIFT发送失败</option>
              <option value="PENDING_CORE">待核心入账</option>
              <option value="CORE_SUCCESS">核心入账成功</option>
              <option value="CORE_FAILED">核心入账失败</option>
              <option value="CORE_UNKNOWN">核心入账状态不明</option>
            </select>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn-primary" :disabled="loading">
            <span v-if="loading">查询中...</span>
            <span v-else>查询</span>
          </button>
          <button type="button" class="btn-secondary" @click="handleReset">
            重置
          </button>
        </div>
      </form>
    </div>

    <!-- Loading Spinner -->
    <LoadingSpinner v-if="loading" />

    <!-- Error Message -->
    <MessageAlert
      v-if="error"
      type="error"
      :message="error"
      @close="error = null"
    />

    <!-- Results Table -->
    <div v-if="!loading && hasResults" class="results-section">
      <!-- Amount Summary -->
      <div v-if="amountSummary.length > 0" class="amount-summary">
        <h3>金额汇总</h3>
        <div class="summary-grid">
          <div
            v-for="summary in amountSummary"
            :key="`${summary.currency}-${summary.direction}`"
            class="summary-item"
          >
            <span class="summary-label">
              {{ summary.currency }} - {{ summary.direction === 'RECEIVE' ? '收' : '付' }}:
            </span>
            <span class="summary-value">{{ formatAmount(summary.total) }}</span>
          </div>
        </div>
      </div>

      <DataTable
        :columns="tableColumns"
        :data="cashFlows"
        :loading="loading"
        @row-click="handleRowClick"
      />

      <!-- Pagination -->
      <PaginationComponent
        :current-page="pagination.currentPage"
        :total-pages="pagination.totalPages"
        :total-records="pagination.totalRecords"
        :page-size="pagination.pageSize"
        :page-size-options="[15, 20, 50, 100]"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
      />
    </div>

    <!-- No Results Message -->
    <div v-if="!loading && !hasResults && searched" class="no-results">
      <p>未找到符合条件的现金流记录</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/client'
import DataTable from '@/components/DataTable.vue'
import PaginationComponent from '@/components/PaginationComponent.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import MessageAlert from '@/components/MessageAlert.vue'

const router = useRouter()

// Query form data
const queryForm = ref({
  transactionId: '',
  cashFlowId: '',
  paymentInfoId: '',
  settlementId: '',
  direction: '',
  currency: '',
  amountMin: null,
  amountMax: null,
  paymentDateFrom: '',
  paymentDateTo: '',
  status: ''
})

// State
const loading = ref(false)
const error = ref(null)
const cashFlows = ref([])
const searched = ref(false)
const pagination = ref({
  currentPage: 1,
  totalPages: 0,
  totalRecords: 0,
  pageSize: 20
})

// Computed
const hasResults = computed(() => cashFlows.value.length > 0)

// Calculate amount summary by currency and direction
const amountSummary = computed(() => {
  if (!hasResults.value) return []
  
  const summary = {}
  cashFlows.value.forEach(cf => {
    const key = `${cf.currency}-${cf.direction}`
    if (!summary[key]) {
      summary[key] = {
        currency: cf.currency,
        direction: cf.direction,
        total: 0
      }
    }
    summary[key].total += cf.amount
  })
  
  return Object.values(summary)
})

// Table columns configuration
const tableColumns = [
  { key: 'cash_flow_id', label: '现金流内部ID', width: '150px' },
  { key: 'transaction_id', label: '交易流水号', width: '150px' },
  { 
    key: 'direction', 
    label: '方向', 
    width: '80px',
    format: (value) => value === 'RECEIVE' ? '收' : '付'
  },
  { key: 'currency', label: '币种', width: '80px' },
  { 
    key: 'amount', 
    label: '金额', 
    width: '120px',
    format: (value) => formatAmount(value)
  },
  { key: 'payment_date', label: '收付日期', width: '100px', format: 'date' },
  { key: 'account_number', label: '账号', width: '150px' },
  { 
    key: 'current_status', 
    label: '当前状态', 
    width: '120px',
    format: formatStatus
  },
  { 
    key: 'progress_percentage', 
    label: '进度', 
    width: '80px',
    format: (value) => `${value}%`
  }
]

// Methods
const formatAmount = (amount) => {
  return new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
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

const handleQuery = async () => {
  // Validate at least one search criteria
  const hasAnyCriteria = Object.values(queryForm.value).some(v => v !== '' && v !== null)
  if (!hasAnyCriteria) {
    error.value = '请至少输入一个查询条件'
    return
  }

  loading.value = true
  error.value = null
  searched.value = true

  try {
    const params = {
      page: pagination.value.currentPage,
      page_size: pagination.value.pageSize
    }

    // Add optional parameters
    if (queryForm.value.transactionId) params.transaction_id = queryForm.value.transactionId
    if (queryForm.value.cashFlowId) params.cash_flow_id = queryForm.value.cashFlowId
    if (queryForm.value.paymentInfoId) params.payment_info_id = queryForm.value.paymentInfoId
    if (queryForm.value.settlementId) params.settlement_id = queryForm.value.settlementId
    if (queryForm.value.direction) params.direction = queryForm.value.direction
    if (queryForm.value.currency) params.currency = queryForm.value.currency.toUpperCase()
    if (queryForm.value.amountMin !== null) params.amount_min = queryForm.value.amountMin
    if (queryForm.value.amountMax !== null) params.amount_max = queryForm.value.amountMax
    if (queryForm.value.paymentDateFrom) params.payment_date_from = queryForm.value.paymentDateFrom
    if (queryForm.value.paymentDateTo) params.payment_date_to = queryForm.value.paymentDateTo
    if (queryForm.value.status) params.status = queryForm.value.status

    const response = await apiClient.get('/cash-flows', { params })

    cashFlows.value = response.data
    pagination.value = {
      currentPage: response.pagination.current_page,
      totalPages: response.pagination.total_pages,
      totalRecords: response.pagination.total_records,
      pageSize: response.pagination.page_size
    }
  } catch (err) {
    console.error('Query error:', err)
    error.value = err.response?.data?.message || '查询失败，请稍后重试'
    cashFlows.value = []
    pagination.value = {
      currentPage: 1,
      totalPages: 0,
      totalRecords: 0,
      pageSize: 20
    }
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  queryForm.value = {
    transactionId: '',
    cashFlowId: '',
    paymentInfoId: '',
    settlementId: '',
    direction: '',
    currency: '',
    amountMin: null,
    amountMax: null,
    paymentDateFrom: '',
    paymentDateTo: '',
    status: ''
  }
  cashFlows.value = []
  searched.value = false
  error.value = null
  pagination.value = {
    currentPage: 1,
    totalPages: 0,
    totalRecords: 0,
    pageSize: 20
  }
}

const handlePageChange = (page) => {
  pagination.value.currentPage = page
  handleQuery()
}

const handlePageSizeChange = (pageSize) => {
  pagination.value.pageSize = pageSize
  pagination.value.currentPage = 1
  handleQuery()
}

const handleRowClick = (row) => {
  // Navigate to cash flow detail page
  router.push({
    name: 'cash-flow-detail',
    params: { cashFlowId: row.cash_flow_id }
  })
}
</script>

<style scoped>
.cash-flow-summary {
  padding: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
}

.query-form {
  background: white;
  padding: 1.5rem;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.query-form h2 {
  color: #D32F2F;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #333;
}

.form-group input,
.form-group select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.875rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #D32F2F;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-start;
}

.btn-primary,
.btn-secondary {
  padding: 0.625rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #D32F2F;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #B71C1C;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.results-section {
  background: white;
  padding: 1.5rem;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.amount-summary {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 4px;
}

.amount-summary h3 {
  color: #D32F2F;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  background: white;
  border-radius: 4px;
}

.summary-label {
  font-weight: 500;
  color: #666;
}

.summary-value {
  font-weight: 600;
  color: #333;
}

.no-results {
  background: white;
  padding: 3rem;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
  color: #666;
}

@media (max-width: 1366px) {
  .form-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1024px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
