<template>
  <div class="tabs-container">
    <div class="tabs-header">
      <div 
        v-for="tab in tabs" 
        :key="tab.key"
        class="tab-item"
        :class="{ 'active': activeTab === tab.key }"
        @click="handleTabClick(tab.key)"
      >
        {{ tab.label }}
      </div>
    </div>
    <div class="tabs-content">
      <slot :name="activeTab"></slot>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  tabs: {
    type: Array,
    required: true,
    // tabs: [{ key: 'info', label: '交易信息' }]
  },
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'tab-change'])

const activeTab = ref(props.modelValue || (props.tabs.length > 0 ? props.tabs[0].key : ''))

watch(() => props.modelValue, (newVal) => {
  if (newVal && newVal !== activeTab.value) {
    activeTab.value = newVal
  }
})

const handleTabClick = (key) => {
  if (key !== activeTab.value) {
    activeTab.value = key
    emit('update:modelValue', key)
    emit('tab-change', key)
  }
}
</script>

<style scoped>
.tabs-container {
  width: 100%;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.tabs-header {
  display: flex;
  background-color: #f5f5f5;
  border-bottom: 2px solid #ddd;
}

.tab-item {
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  background-color: #e8e8e8;
  border-right: 1px solid #ddd;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.tab-item:last-child {
  border-right: none;
}

.tab-item:hover:not(.active) {
  background-color: #ddd;
  color: #333;
}

.tab-item.active {
  background-color: #D32F2F;
  color: #fff;
  border-bottom: 2px solid #D32F2F;
  margin-bottom: -2px;
}

.tabs-content {
  padding: 20px;
  min-height: 200px;
}
</style>
