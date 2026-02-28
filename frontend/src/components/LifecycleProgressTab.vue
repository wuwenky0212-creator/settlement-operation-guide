<template>
  <div class="lifecycle-progress-tab">
    <!-- Polling Status Indicator -->
    <div v-if="isPolling" class="polling-indicator">
      <span class="polling-dot"></span>
      <span class="polling-text">实时更新中</span>
      <span v-if="lastUpdate" class="last-update">
        最后更新: {{ formatLastUpdate(lastUpdate) }}
      </span>
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

    <!-- Update Notification -->
    <transition name="fade">
      <div v-if="showUpdateNotification" class="update-notification">
        <span>✓ 状态已更新</span>
      </div>
    </transition>

    <!-- Lifecycle Progress -->
    <div v-if="!loading && lifecycleProgress">
      <LifecycleProgress :progress="lifecycleProgress" />
      
      <!-- Operation Guide -->
      <div v-if="operationGuide" class="operation-guide-section">
        <OperationGuide
          :guide="operationGuide"
          @action-click="handleActionClick"
        />
      </div>
    </div>

    <!-- No Progress Data -->
    <div v-if="!loading && !lifecycleProgress" class="no-progress">
      <p>暂无生命周期进度信息</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps } from 'vue'
import apiClient from '@/api/client'
import { usePolling } from '@/composables/usePolling'
import LifecycleProgress from '@/components/LifecycleProgress.vue'
import OperationGuide from '@/components/OperationGuide.vue'
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
const lifecycleProgress = ref(null)
const operationGuide = ref(null)
const showUpdateNotification = ref(false)

// Polling setup (10 second interval)
const { isPolling, lastUpdate, startPolling, stopPolling } = usePolling(
  async () => {
    await refreshProgress()
  },
  10000
)

// Methods
const loadLifecycleProgress = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await apiClient.get(`/transactions/${props.transactionId}/progress`)
    lifecycleProgress.value = response
    
    // Load operation guide
    await loadOperationGuide()
  } catch (err) {
    console.error('Load lifecycle progress error:', err)
    if (err.response?.status === 404) {
      lifecycleProgress.value = null
    } else {
      error.value = err.response?.data?.message || '加载生命周期进度失败'
    }
  } finally {
    loading.value = false
  }
}

const refreshProgress = async () => {
  // Silent refresh without showing loading spinner
  try {
    const response = await apiClient.get(`/transactions/${props.transactionId}/progress`)
    
    // Check if progress has changed
    const hasChanged = JSON.stringify(lifecycleProgress.value) !== JSON.stringify(response)
    
    if (hasChanged) {
      lifecycleProgress.value = response
      await loadOperationGuide()
      
      // Show update notification
      showUpdateNotification.value = true
      setTimeout(() => {
        showUpdateNotification.value = false
      }, 3000)
    }
  } catch (err) {
    console.error('Refresh progress error:', err)
    // Don't show error for background refresh
  }
}

const loadOperationGuide = async () => {
  try {
    const response = await apiClient.get(`/transactions/${props.transactionId}/operation-guide`)
    operationGuide.value = response
  } catch (err) {
    console.error('Load operation guide error:', err)
    // Don't show error for operation guide, it's optional
    operationGuide.value = null
  }
}

const handleActionClick = (action) => {
  console.log('Action clicked:', action)
  // Handle action based on action type
  // This could trigger navigation, open a modal, etc.
}

const formatLastUpdate = (date) => {
  if (!date) return ''
  const now = new Date()
  const diff = Math.floor((now - date) / 1000) // seconds
  
  if (diff < 60) return `${diff}秒前`
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// Lifecycle
onMounted(async () => {
  await loadLifecycleProgress()
  // Start polling after initial load
  startPolling()
})
</script>

<style scoped>
.lifecycle-progress-tab {
  min-height: 300px;
  position: relative;
}

.polling-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #E3F2FD;
  border-left: 4px solid #2196F3;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.polling-dot {
  width: 8px;
  height: 8px;
  background: #2196F3;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

.polling-text {
  color: #1565C0;
  font-weight: 500;
}

.last-update {
  color: #666;
  margin-left: auto;
}

.update-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #4CAF50;
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.operation-guide-section {
  margin-top: 2rem;
}

.no-progress {
  text-align: center;
  padding: 3rem;
  color: #666;
  background: #f9f9f9;
  border-radius: 4px;
}
</style>
