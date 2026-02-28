<template>
  <div class="pagination-container">
    <div class="pagination-left">
      <span class="pagination-label">每页显示：</span>
      <select v-model="currentPageSize" @change="handlePageSizeChange" class="page-size-select">
        <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
      </select>
    </div>
    
    <div class="pagination-center">
      <button 
        class="pagination-btn" 
        :disabled="currentPage === 1"
        @click="goToPage(1)"
      >
        首页
      </button>
      <button 
        class="pagination-btn" 
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
      >
        上一页
      </button>
      
      <span class="page-info">
        <input 
          type="number" 
          v-model.number="pageInput" 
          @keyup.enter="goToInputPage"
          class="page-input"
          min="1"
          :max="totalPages"
        />
        <span class="page-separator">/</span>
        <span class="total-pages">{{ totalPages }}</span>
      </span>
      
      <button 
        class="pagination-btn" 
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
      >
        下一页
      </button>
      <button 
        class="pagination-btn" 
        :disabled="currentPage === totalPages"
        @click="goToPage(totalPages)"
      >
        末页
      </button>
    </div>
    
    <div class="pagination-right">
      <span class="record-info">
        显示 {{ startRecord }} 到 {{ endRecord }}，共 {{ totalRecords }} 记录
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    required: true,
    default: 1
  },
  pageSize: {
    type: Number,
    required: true,
    default: 20
  },
  totalRecords: {
    type: Number,
    required: true,
    default: 0
  },
  pageSizeOptions: {
    type: Array,
    default: () => [15, 20, 50, 100]
  }
})

const emit = defineEmits(['page-change', 'page-size-change'])

const currentPageSize = ref(props.pageSize)
const pageInput = ref(props.currentPage)

watch(() => props.currentPage, (newVal) => {
  pageInput.value = newVal
})

const totalPages = computed(() => {
  return Math.ceil(props.totalRecords / props.pageSize) || 1
})

const startRecord = computed(() => {
  if (props.totalRecords === 0) return 0
  return (props.currentPage - 1) * props.pageSize + 1
})

const endRecord = computed(() => {
  const end = props.currentPage * props.pageSize
  return Math.min(end, props.totalRecords)
})

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value && page !== props.currentPage) {
    emit('page-change', page)
  }
}

const goToInputPage = () => {
  const page = parseInt(pageInput.value)
  if (!isNaN(page) && page >= 1 && page <= totalPages.value) {
    goToPage(page)
  } else {
    pageInput.value = props.currentPage
  }
}

const handlePageSizeChange = () => {
  emit('page-size-change', currentPageSize.value)
}
</script>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f5f5f5;
  border-top: 1px solid #ddd;
}

.pagination-left,
.pagination-center,
.pagination-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-label {
  font-size: 14px;
  color: #333;
}

.page-size-select {
  padding: 4px 8px;
  border: 1px solid #ccc;
  border-radius: 3px;
  font-size: 14px;
  cursor: pointer;
}

.page-size-select:focus {
  outline: none;
  border-color: #D32F2F;
}

.pagination-btn {
  padding: 6px 12px;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 3px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #D32F2F;
  color: #fff;
  border-color: #D32F2F;
}

.pagination-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.page-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

.page-input {
  width: 50px;
  padding: 4px 8px;
  border: 1px solid #ccc;
  border-radius: 3px;
  text-align: center;
  font-size: 14px;
}

.page-input:focus {
  outline: none;
  border-color: #D32F2F;
}

.page-separator {
  color: #666;
}

.total-pages {
  color: #333;
  font-weight: 500;
}

.record-info {
  font-size: 14px;
  color: #666;
}
</style>
