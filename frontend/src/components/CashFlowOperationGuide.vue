<template>
  <div class="cash-flow-operation-guide">
    <!-- Loading State -->
    <LoadingSpinner v-if="loading" />

    <!-- Error State -->
    <MessageAlert
      v-if="error"
      type="error"
      :message="error"
      @close="error = null"
    />

    <!-- Guide Content -->
    <div v-if="!loading && guide" class="guide-content">
      <!-- Next Action -->
      <div class="guide-section">
        <h4>下一步操作</h4>
        <div class="guide-box next-action">
          <p>{{ guide.next_action }}</p>
        </div>
      </div>

      <!-- Action Entry -->
      <div v-if="guide.action_entry" class="guide-section">
        <h4>操作入口</h4>
        <div class="guide-box">
          <button
            v-if="guide.action_entry.type === 'BUTTON'"
            class="action-button"
            @click="handleAction(guide.action_entry)"
          >
            {{ guide.action_entry.label }}
          </button>
          <a
            v-else-if="guide.action_entry.type === 'LINK'"
            :href="guide.action_entry.url"
            class="action-link"
            target="_blank"
          >
            {{ guide.action_entry.label }} →
          </a>
        </div>
      </div>

      <!-- Notes -->
      <div v-if="guide.notes" class="guide-section">
        <h4>注意事项</h4>
        <div class="guide-box notes">
          <p>{{ guide.notes }}</p>
        </div>
      </div>

      <!-- Estimated Time -->
      <div v-if="guide.estimated_time" class="guide-section">
        <h4>预计时间</h4>
        <div class="guide-box">
          <p>{{ guide.estimated_time }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import MessageAlert from '@/components/MessageAlert.vue'

const props = defineProps({
  cashFlowId: {
    type: String,
    required: true
  }
})

// State
const loading = ref(false)
const error = ref(null)
const guide = ref(null)

// Methods
const loadGuide = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await apiClient.get(`/cash-flows/${props.cashFlowId}/operation-guide`)
    guide.value = response
  } catch (err) {
    console.error('Load operation guide error:', err)
    error.value = err.response?.data?.message || '加载操作指引失败'
  } finally {
    loading.value = false
  }
}

const handleAction = (actionEntry) => {
  if (actionEntry.url) {
    window.open(actionEntry.url, '_blank')
  } else if (actionEntry.action) {
    // Handle custom actions
    console.log('Execute action:', actionEntry.action)
    // You can implement custom action handlers here
  }
}

// Lifecycle
onMounted(() => {
  loadGuide()
})
</script>

<style scoped>
.cash-flow-operation-guide {
  padding: 1rem;
}

.guide-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.guide-section h4 {
  color: #666;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.guide-box {
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 4px;
  border-left: 4px solid #2196F3;
}

.guide-box.next-action {
  border-left-color: #D32F2F;
  background: #ffebee;
}

.guide-box.notes {
  border-left-color: #FF9800;
  background: #fff3e0;
}

.guide-box p {
  margin: 0;
  color: #333;
  line-height: 1.6;
}

.action-button {
  padding: 0.75rem 1.5rem;
  background: #D32F2F;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-button:hover {
  background: #B71C1C;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(211, 47, 47, 0.3);
}

.action-link {
  display: inline-flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: #2196F3;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
}

.action-link:hover {
  background: #1976D2;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}
</style>
