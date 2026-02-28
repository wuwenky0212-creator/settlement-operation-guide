<template>
  <div class="data-table-container">
    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th 
              v-for="column in columns" 
              :key="column.key"
              :style="{ width: column.width || 'auto' }"
              :class="{ 'sortable': column.sortable }"
              @click="column.sortable && handleSort(column.key)"
            >
              {{ column.label }}
              <span v-if="column.sortable" class="sort-icon">
                <span v-if="sortKey === column.key">
                  {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
                <span v-else class="sort-placeholder">⇅</span>
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="(row, index) in data" 
            :key="getRowKey(row, index)"
            :class="{ 'even-row': index % 2 === 0, 'odd-row': index % 2 !== 0 }"
            @click="handleRowClick(row)"
          >
            <td 
              v-for="column in columns" 
              :key="column.key"
            >
              <slot 
                :name="`cell-${column.key}`" 
                :row="row" 
                :value="getNestedValue(row, column.key)"
              >
                {{ formatValue(row, column) }}
              </slot>
            </td>
          </tr>
          <tr v-if="data.length === 0" class="empty-row">
            <td :colspan="columns.length" class="empty-cell">
              {{ emptyText }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  columns: {
    type: Array,
    required: true,
    // columns: [{ key: 'id', label: 'ID', width: '100px', sortable: true, formatter: (value, row) => value }]
  },
  data: {
    type: Array,
    required: true,
    default: () => []
  },
  rowKey: {
    type: [String, Function],
    default: 'id'
  },
  emptyText: {
    type: String,
    default: '暂无数据'
  }
})

const emit = defineEmits(['row-click', 'sort-change'])

const sortKey = ref('')
const sortOrder = ref('asc')

const getRowKey = (row, index) => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(row, index)
  }
  return row[props.rowKey] || index
}

const getNestedValue = (obj, path) => {
  return path.split('.').reduce((acc, part) => acc && acc[part], obj)
}

const formatValue = (row, column) => {
  const value = getNestedValue(row, column.key)
  
  // Handle date formatting
  if (column.format === 'date' && value) {
    try {
      const date = new Date(value)
      return date.toISOString().split('T')[0]
    } catch (e) {
      return value
    }
  }
  
  if (column.formatter && typeof column.formatter === 'function') {
    return column.formatter(value, row)
  }
  return value ?? '-'
}

const handleRowClick = (row) => {
  emit('row-click', row)
}

const handleSort = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
  emit('sort-change', { key: sortKey.value, order: sortOrder.value })
}
</script>

<style scoped>
.data-table-container {
  width: 100%;
  overflow-x: auto;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.table-wrapper {
  min-width: 100%;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table thead {
  background-color: #f5f5f5;
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #ddd;
  white-space: nowrap;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.data-table th.sortable:hover {
  background-color: #e8e8e8;
}

.sort-icon {
  margin-left: 4px;
  font-size: 12px;
  color: #D32F2F;
}

.sort-placeholder {
  color: #ccc;
}

.data-table td {
  padding: 10px 16px;
  border-bottom: 1px solid #eee;
  color: #555;
}

.data-table tbody tr {
  transition: background-color 0.2s;
  cursor: pointer;
}

.data-table tbody tr.even-row {
  background-color: #fff;
}

.data-table tbody tr.odd-row {
  background-color: #fafafa;
}

.data-table tbody tr:hover {
  background-color: #f0f0f0;
}

.empty-row {
  background-color: #fff !important;
}

.empty-cell {
  text-align: center;
  padding: 40px 16px;
  color: #999;
  font-size: 14px;
}
</style>
