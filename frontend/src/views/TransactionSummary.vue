<template>
  <div class="transaction-summary">
    <!-- Query Form -->
    <div class="query-form">
      <h2>交易汇总查询</h2>
      
      <form @submit.prevent="handleQuery">
        <div class="form-grid">
          <!-- Row 1 -->
          <div class="form-group">
            <label for="externalId">外部流水号 <span class="required">*</span></label>
            <input
              id="externalId"
              v-model="queryForm.externalId"
              type="text"
              placeholder="请输入外部流水号"
              required
            />
          </div>

          <div class="form-group">
            <label for="status">交易状态</label>
            <select id="status" v-model="queryForm.status">
              <option value="">全部</option>
              <option value="生效">生效</option>
              <option value="到期">到期</option>
              <option value="失效">失效</option>
            </select>
          </div>

          <div class="form-group">
            <label for="product">产品</label>
            <select id="product" v-model="queryForm.product">
              <option value="">全部</option>
              <option value="外汇即期">外汇即期</option>
              <option value="外汇远期">外汇远期</option>
              <option value="外汇掉期">外汇掉期</option>
              <option value="同业拆借">同业拆借</option>
              <option value="货币市场存款">货币市场存款</option>
              <option value="现券买卖">现券买卖</option>
              <option value="买断式回购">买断式回购</option>
              <option value="质押式回购">质押式回购</option>
              <option value="单边现金流">单边现金流</option>
            </select>
          </div>

          <div class="form-group">
            <label for="counterparty">交易对手</label>
            <input
              id="counterparty"
              v-model="queryForm.counterparty"
              type="text"
              placeholder="请输入交易对手"
            />
          </div>

          <!-- Row 2 -->
          <div class="form-group">
            <label for="tradeDateFrom">交易日起始</label>
            <input
              id="tradeDateFrom"
              v-model="queryForm.tradeDateFrom"
              type="date"
            />
          </div>

          <div class="form-group">
            <label for="tradeDateTo">交易日结束</label>
            <input
              id="tradeDateTo"
              v-model="queryForm.tradeDateTo"
              type="date"
            />
          </div>

          <div class="form-group">
            <label for="valueDateFrom">起息日起始</label>
            <input
              id="valueDateFrom"
              v-model="queryForm.valueDateFrom"
              type="date"
            />
          </div>

          <div class="form-group">
            <label for="valueDateTo">起息日结束</label>
            <input
              id="valueDateTo"
              v-model="queryForm.valueDateTo"
              type="date"
            />
          </div>

          <!-- Row 3 -->
          <div class="form-group">
            <label for="maturityDateFrom">到期日起始</label>
            <input
              id="maturityDateFrom"
              v-model="queryForm.maturityDateFrom"
              type="date"
            />
          </div>

          <div class="form-group">
            <label for="maturityDateTo">到期日结束</label>
            <input
              id="maturityDateTo"
              v-model="queryForm.maturityDateTo"
              type="date"
            />
          </div>

          <div class="form-group">
            <label for="currency">货币</label>
            <input
              id="currency"
              v-model="queryForm.currency"
              type="text"
              placeholder="如 CNY, USD, EUR"
              maxlength="3"
            />
          </div>

          <div class="form-group">
            <label for="operatingInstitution">运营机构</label>
            <select id="operatingInstitution" v-model="queryForm.operatingInstitution">
              <option value="">全部</option>
              <option value="1530H_中国银行(香港)有限公司">1530H_中国银行(香港)有限公司</option>
              <option value="052_中国银行（香港）有限公司文莱分行">052_中国银行（香港）有限公司文莱分行</option>
              <option value="053_中国银行（香港）有限公司仰光分行">053_中国银行（香港）有限公司仰光分行</option>
            </select>
          </div>

          <!-- Row 4 -->
          <div class="form-group">
            <label for="businessInstitution">业务机构</label>
            <input
              id="businessInstitution"
              v-model="queryForm.businessInstitution"
              type="text"
              placeholder="请输入业务机构"
            />
          </div>

          <div class="form-group">
            <label for="settlementMethod">清算方式</label>
            <select id="settlementMethod" v-model="queryForm.settlementMethod">
              <option value="">全部</option>
              <option value="全额">全额</option>
              <option value="净额">净额</option>
              <option value="集中">集中</option>
              <option value="无需">无需</option>
              <option value="我行代理">我行代理</option>
              <option value="他行代理">他行代理</option>
            </select>
          </div>

          <div class="form-group">
            <label for="confirmationType">证实方式</label>
            <select id="confirmationType" v-model="queryForm.confirmationType">
              <option value="">全部</option>
              <option value="SWIFT">SWIFT</option>
              <option value="文本">文本</option>
              <option value="无证实">无证实</option>
            </select>
          </div>

          <div class="form-group">
            <label for="source">交易来源</label>
            <select id="source" v-model="queryForm.source">
              <option value="">全部</option>
              <option value="GIT">GIT</option>
              <option value="FXO">FXO</option>
              <option value="FXS">FXS</option>
              <option value="FXY">FXY</option>
              <option value="FXW">FXW</option>
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
          <button
            type="button"
            class="btn-export"
            @click="handleExport"
            :disabled="!hasResults || loading"
          >
            导出
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
      <DataTable
        :columns="tableColumns"
        :data="transactions"
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
      <p>未找到符合条件的交易记录</p>
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
  externalId: '',
  status: '',
  tradeDateFrom: '',
  tradeDateTo: '',
  valueDateFrom: '',
  valueDateTo: '',
  maturityDateFrom: '',
  maturityDateTo: '',
  counterparty: '',
  product: '',
  currency: '',
  operatingInstitution: '',
  businessInstitution: '',
  settlementMethod: '',
  confirmationType: '',
  source: ''
})

// State
const loading = ref(false)
const error = ref(null)
const transactions = ref([])
const searched = ref(false)
const pagination = ref({
  currentPage: 1,
  totalPages: 0,
  totalRecords: 0,
  pageSize: 20
})

// Computed
const hasResults = computed(() => transactions.value.length > 0)

// Table columns configuration
const tableColumns = [
  { key: 'external_id', label: '外部流水号', width: '120px' },
  { key: 'transaction_id', label: '交易流水号', width: '120px' },
  { key: 'entry_date', label: '录入日', width: '100px', format: 'date' },
  { key: 'trade_date', label: '交易日', width: '100px', format: 'date' },
  { key: 'value_date', label: '起息日', width: '100px', format: 'date' },
  { key: 'maturity_date', label: '到期日', width: '100px', format: 'date' },
  { key: 'account', label: '账户', width: '100px' },
  { key: 'product', label: '产品', width: '100px' },
  { key: 'direction', label: '买卖方向', width: '80px' },
  { key: 'underlying', label: '标的物', width: '100px' },
  { key: 'counterparty', label: '交易对手', width: '120px' },
  { key: 'status', label: '交易状态', width: '80px' },
  { key: 'back_office_status', label: '后线处理状态', width: '120px' },
  { key: 'settlement_method', label: '清算方式', width: '80px' },
  { key: 'confirmation_number', label: '证实编号', width: '100px' },
  { key: 'confirmation_type', label: '证实方式', width: '80px' },
  { key: 'confirmation_match_type', label: '证实匹配方式', width: '100px' },
  { key: 'nature', label: '交易性质', width: '100px' },
  { key: 'source', label: '交易来源', width: '80px' },
  { key: 'latest_event_type', label: '事件类型', width: '100px' },
  { key: 'operating_institution', label: '运营机构', width: '150px' },
  { key: 'trader', label: '交易员', width: '80px' }
]

// Methods
const handleQuery = async () => {
  if (!queryForm.value.externalId) {
    error.value = '请输入外部流水号'
    return
  }

  loading.value = true
  error.value = null
  searched.value = true

  try {
    const params = {
      external_id: queryForm.value.externalId,
      page: pagination.value.currentPage,
      page_size: pagination.value.pageSize,
      sort_by: 'trade_date',
      sort_order: 'DESC'
    }

    // Add optional parameters
    if (queryForm.value.status) params.status = queryForm.value.status
    if (queryForm.value.tradeDateFrom) params.trade_date_from = queryForm.value.tradeDateFrom
    if (queryForm.value.tradeDateTo) params.trade_date_to = queryForm.value.tradeDateTo
    if (queryForm.value.valueDateFrom) params.value_date_from = queryForm.value.valueDateFrom
    if (queryForm.value.valueDateTo) params.value_date_to = queryForm.value.valueDateTo
    if (queryForm.value.maturityDateFrom) params.maturity_date_from = queryForm.value.maturityDateFrom
    if (queryForm.value.maturityDateTo) params.maturity_date_to = queryForm.value.maturityDateTo
    if (queryForm.value.counterparty) params.counterparty = queryForm.value.counterparty
    if (queryForm.value.product) params.product = queryForm.value.product
    if (queryForm.value.currency) params.currency = queryForm.value.currency.toUpperCase()
    if (queryForm.value.operatingInstitution) params.operating_institution = queryForm.value.operatingInstitution
    if (queryForm.value.businessInstitution) params.business_institution = queryForm.value.businessInstitution
    if (queryForm.value.settlementMethod) params.settlement_method = queryForm.value.settlementMethod
    if (queryForm.value.confirmationType) params.confirmation_type = queryForm.value.confirmationType
    if (queryForm.value.source) params.source = queryForm.value.source

    const response = await apiClient.get('/transactions', { params })

    transactions.value = response.data
    pagination.value = {
      currentPage: response.pagination.current_page,
      totalPages: response.pagination.total_pages,
      totalRecords: response.pagination.total_records,
      pageSize: response.pagination.page_size
    }
  } catch (err) {
    console.error('Query error:', err)
    error.value = err.response?.data?.message || '查询失败，请稍后重试'
    transactions.value = []
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
    externalId: '',
    status: '',
    tradeDateFrom: '',
    tradeDateTo: '',
    valueDateFrom: '',
    valueDateTo: '',
    maturityDateFrom: '',
    maturityDateTo: '',
    counterparty: '',
    product: '',
    currency: '',
    operatingInstitution: '',
    businessInstitution: '',
    settlementMethod: '',
    confirmationType: '',
    source: ''
  }
  transactions.value = []
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
  // Navigate to transaction detail page
  router.push({
    name: 'transaction-detail',
    params: { externalId: row.external_id }
  })
}

const handleExport = async () => {
  if (!hasResults.value) return

  loading.value = true
  error.value = null

  try {
    const params = {
      external_id: queryForm.value.externalId,
      format: 'excel'
    }

    // Add optional parameters
    if (queryForm.value.status) params.status = queryForm.value.status
    if (queryForm.value.tradeDateFrom) params.trade_date_from = queryForm.value.tradeDateFrom
    if (queryForm.value.tradeDateTo) params.trade_date_to = queryForm.value.tradeDateTo
    if (queryForm.value.valueDateFrom) params.value_date_from = queryForm.value.valueDateFrom
    if (queryForm.value.valueDateTo) params.value_date_to = queryForm.value.valueDateTo
    if (queryForm.value.maturityDateFrom) params.maturity_date_from = queryForm.value.maturityDateFrom
    if (queryForm.value.maturityDateTo) params.maturity_date_to = queryForm.value.maturityDateTo
    if (queryForm.value.counterparty) params.counterparty = queryForm.value.counterparty
    if (queryForm.value.product) params.product = queryForm.value.product
    if (queryForm.value.currency) params.currency = queryForm.value.currency.toUpperCase()
    if (queryForm.value.operatingInstitution) params.operating_institution = queryForm.value.operatingInstitution
    if (queryForm.value.businessInstitution) params.business_institution = queryForm.value.businessInstitution
    if (queryForm.value.settlementMethod) params.settlement_method = queryForm.value.settlementMethod
    if (queryForm.value.confirmationType) params.confirmation_type = queryForm.value.confirmationType
    if (queryForm.value.source) params.source = queryForm.value.source

    const response = await apiClient.get('/export/transactions', {
      params,
      responseType: 'blob'
    })

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `交易汇总_${new Date().toISOString().slice(0, 10)}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Export error:', err)
    error.value = err.response?.data?.message || '导出失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.transaction-summary {
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

.form-group label .required {
  color: #D32F2F;
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
.btn-secondary,
.btn-export {
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

.btn-export {
  background: #4CAF50;
  color: white;
}

.btn-export:hover:not(:disabled) {
  background: #45a049;
}

.btn-export:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.results-section {
  background: white;
  padding: 1.5rem;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
