<template>
  <div class="event-info-tab">
    <!-- Loading State -->
    <LoadingSpinner v-if="loading" />

    <!-- Error State -->
    <MessageAlert
      v-if="error"
      type="error"
      :message="error"
      @close="error = null"
    />

    <!-- Events Table -->
    <div v-if="!loading && events.length > 0">
      <DataTable
        :columns="eventColumns"
        :data="events"
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

    <!-- No Events Message -->
    <div v-if="!loading && events.length === 0" class="no-events">
      <p>该交易暂无事件记录</p>
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
  externalId: {
    type: String,
    required: true
  }
})

// State
const loading = ref(false)
const error = ref(null)
const events = ref([])
const pagination = ref({
  currentPage: 1,
  totalPages: 0,
  totalRecords: 0,
  pageSize: 15
})

// Event columns configuration
const eventColumns = [
  { key: 'external_id', label: '外部流水号', width: '120px' },
  { key: 'transaction_id', label: '交易流水号', width: '120px' },
  { key: 'parent_transaction_id', label: '父交易流水号', width: '120px' },
  { key: 'product', label: '产品', width: '100px' },
  { key: 'account', label: '账户', width: '100px' },
  { key: 'event_type', label: '事件类型', width: '120px' },
  { key: 'transaction_status', label: '交易状态', width: '80px' },
  { key: 'entry_date', label: '录入日', width: '100px', format: 'date' },
  { key: 'trade_date', label: '交易日', width: '100px', format: 'date' },
  { key: 'modified_date', label: '修改日', width: '100px', format: 'datetime' },
  { key: 'back_office_status', label: '后线处理状态', width: '120px' },
  { key: 'confirmation_status', label: '证实状态', width: '100px' },
  { key: 'confirmation_match_status', label: '证实匹配状态', width: '120px' },
  { key: 'operator', label: '操作用户', width: '100px' }
]

// Methods
const loadEvents = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await apiClient.get(`/transactions/${props.externalId}/events`, {
      params: {
        page: pagination.value.currentPage,
        page_size: pagination.value.pageSize
      }
    })

    events.value = response.data
    pagination.value = {
      currentPage: response.pagination.current_page,
      totalPages: response.pagination.total_pages,
      totalRecords: response.pagination.total_records,
      pageSize: response.pagination.page_size
    }
  } catch (err) {
    console.error('Load events error:', err)
    error.value = err.response?.data?.message || '加载事件信息失败'
    events.value = []
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  pagination.value.currentPage = page
  loadEvents()
}

const handlePageSizeChange = (pageSize) => {
  pagination.value.pageSize = pageSize
  pagination.value.currentPage = 1
  loadEvents()
}

// Lifecycle
onMounted(() => {
  loadEvents()
})
</script>

<style scoped>
.event-info-tab {
  min-height: 300px;
}

.no-events {
  text-align: center;
  padding: 3rem;
  color: #666;
  background: #f9f9f9;
  border-radius: 4px;
}
</style>
