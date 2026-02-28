<template>
  <div class="demo-container">
    <h1 class="mb-3">UI组件演示</h1>
    
    <!-- Loading Spinner Demo -->
    <div class="card mb-3">
      <div class="card-header">加载动画组件</div>
      <div class="flex gap-2">
        <LoadingSpinner :fullscreen="false" text="加载中..." size="40px" />
        <LoadingSpinner :fullscreen="false" text="处理中..." size="30px" />
      </div>
    </div>

    <!-- Message Alert Demo -->
    <div class="card mb-3">
      <div class="card-header">消息提示组件</div>
      <div class="flex flex-column gap-2">
        <MessageAlert 
          type="success" 
          title="成功" 
          message="操作成功完成！" 
          :duration="0"
          v-model="showSuccess"
        />
        <MessageAlert 
          type="error" 
          title="错误" 
          message="操作失败，请重试。" 
          :duration="0"
          v-model="showError"
        />
        <MessageAlert 
          type="warning" 
          message="这是一个警告消息。" 
          :duration="0"
          v-model="showWarning"
        />
        <MessageAlert 
          type="info" 
          message="这是一个信息提示。" 
          :duration="0"
          v-model="showInfo"
        />
      </div>
    </div>

    <!-- Tabs Demo -->
    <div class="card mb-3">
      <div class="card-header">标签页组件</div>
      <TabsComponent :tabs="tabs" v-model="activeTab">
        <template #info>
          <div class="p-2">
            <h3>交易信息</h3>
            <p>这里显示交易的详细信息...</p>
          </div>
        </template>
        <template #events>
          <div class="p-2">
            <h3>事件信息</h3>
            <p>这里显示事件流转记录...</p>
          </div>
        </template>
        <template #payment>
          <div class="p-2">
            <h3>支付信息</h3>
            <p>这里显示支付相关信息...</p>
          </div>
        </template>
      </TabsComponent>
    </div>

    <!-- Data Table Demo -->
    <div class="card mb-3">
      <div class="card-header">数据表格组件</div>
      <DataTable 
        :columns="columns" 
        :data="tableData"
        @row-click="handleRowClick"
        @sort-change="handleSort"
      >
        <template #cell-status="{ value }">
          <span :class="getStatusClass(value)">{{ value }}</span>
        </template>
      </DataTable>
      
      <!-- Pagination Demo -->
      <PaginationComponent
        :current-page="currentPage"
        :page-size="pageSize"
        :total-records="totalRecords"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
      />
    </div>

    <!-- Button Styles Demo -->
    <div class="card mb-3">
      <div class="card-header">按钮样式</div>
      <div class="flex gap-2">
        <button class="btn btn-primary">主要按钮</button>
        <button class="btn btn-secondary">次要按钮</button>
        <button class="btn btn-primary" disabled>禁用按钮</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { 
  PaginationComponent, 
  DataTable, 
  TabsComponent, 
  LoadingSpinner, 
  MessageAlert 
} from '@/components'

// Message alerts visibility
const showSuccess = ref(true)
const showError = ref(true)
const showWarning = ref(true)
const showInfo = ref(true)

// Tabs
const tabs = [
  { key: 'info', label: '交易信息' },
  { key: 'events', label: '事件信息' },
  { key: 'payment', label: '支付信息' }
]
const activeTab = ref('info')

// Table
const columns = [
  { key: 'id', label: 'ID', width: '80px', sortable: true },
  { key: 'externalId', label: '外部流水号', sortable: true },
  { key: 'tradeDate', label: '交易日', sortable: true },
  { key: 'product', label: '产品' },
  { key: 'amount', label: '金额', formatter: (value) => `¥${value.toLocaleString()}` },
  { key: 'status', label: '状态' }
]

const tableData = ref([
  { id: 1, externalId: 'EXT-001', tradeDate: '2026-02-27', product: '外汇即期', amount: 100000, status: '生效' },
  { id: 2, externalId: 'EXT-002', tradeDate: '2026-02-26', product: '外汇远期', amount: 200000, status: '到期' },
  { id: 3, externalId: 'EXT-003', tradeDate: '2026-02-25', product: '外汇掉期', amount: 150000, status: '生效' },
  { id: 4, externalId: 'EXT-004', tradeDate: '2026-02-24', product: '同业拆借', amount: 300000, status: '失效' },
  { id: 5, externalId: 'EXT-005', tradeDate: '2026-02-23', product: '现券买卖', amount: 250000, status: '生效' }
])

// Pagination
const currentPage = ref(1)
const pageSize = ref(20)
const totalRecords = ref(82)

const handleRowClick = (row) => {
  console.log('Row clicked:', row)
}

const handleSort = ({ key, order }) => {
  console.log('Sort:', key, order)
}

const handlePageChange = (page) => {
  currentPage.value = page
  console.log('Page changed to:', page)
}

const handlePageSizeChange = (size) => {
  pageSize.value = size
  console.log('Page size changed to:', size)
}

const getStatusClass = (status) => {
  const statusMap = {
    '生效': 'text-success',
    '到期': 'text-warning',
    '失效': 'text-error'
  }
  return statusMap[status] || ''
}
</script>

<style scoped>
.demo-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
</style>
