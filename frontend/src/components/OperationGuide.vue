<template>
  <div class="operation-guide">
    <div class="guide-header">
      <h3 class="guide-title">操作指引</h3>
    </div>

    <div class="guide-content">
      <!-- Next Action -->
      <div class="guide-section">
        <div class="section-label">
          <span class="label-icon">→</span>
          <span class="label-text">下一步操作</span>
        </div>
        <div class="section-content">
          <p class="next-action">{{ guide.nextAction }}</p>
        </div>
      </div>

      <!-- Action Entry -->
      <div v-if="guide.actionEntry" class="guide-section">
        <div class="section-label">
          <span class="label-icon">⚡</span>
          <span class="label-text">操作入口</span>
        </div>
        <div class="section-content">
          <button
            v-if="guide.actionEntry.type === 'BUTTON'"
            class="action-button"
            @click="handleActionClick"
          >
            {{ guide.actionEntry.label }}
          </button>
          <a
            v-else-if="guide.actionEntry.type === 'LINK'"
            :href="guide.actionEntry.url"
            class="action-link"
            target="_blank"
            rel="noopener noreferrer"
          >
            {{ guide.actionEntry.label }}
            <span class="link-icon">↗</span>
          </a>
        </div>
      </div>

      <!-- Notes -->
      <div v-if="guide.notes" class="guide-section">
        <div class="section-label">
          <span class="label-icon">ℹ</span>
          <span class="label-text">注意事项</span>
        </div>
        <div class="section-content">
          <p class="notes">{{ guide.notes }}</p>
        </div>
      </div>

      <!-- Estimated Time -->
      <div v-if="guide.estimatedTime" class="guide-section">
        <div class="section-label">
          <span class="label-icon">⏱</span>
          <span class="label-text">预计时间</span>
        </div>
        <div class="section-content">
          <p class="estimated-time">{{ guide.estimatedTime }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  guide: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['action-click'])

// Methods
const handleActionClick = () => {
  if (props.guide.actionEntry?.action) {
    emit('action-click', props.guide.actionEntry.action)
  }
}
</script>

<style scoped>
.operation-guide {
  background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
  border-radius: 8px;
  border: 2px solid #FF9800;
  overflow: hidden;
}

.guide-header {
  background: #FF9800;
  padding: 1rem 1.5rem;
}

.guide-title {
  color: white;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.guide-title::before {
  content: '📋';
  font-size: 1.25rem;
}

.guide-content {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.guide-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #E65100;
}

.label-icon {
  font-size: 1.25rem;
}

.label-text {
  font-size: 0.9375rem;
}

.section-content {
  padding-left: 2rem;
}

.next-action {
  font-size: 1rem;
  color: #333;
  margin: 0;
  line-height: 1.6;
  font-weight: 500;
}

.action-button {
  background: #D32F2F;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(211, 47, 47, 0.3);
}

.action-button:hover {
  background: #B71C1C;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(211, 47, 47, 0.4);
}

.action-button:active {
  transform: translateY(0);
}

.action-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #1976D2;
  text-decoration: none;
  font-size: 0.9375rem;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  background: white;
  border: 2px solid #1976D2;
  transition: all 0.2s;
}

.action-link:hover {
  background: #1976D2;
  color: white;
}

.link-icon {
  font-size: 1rem;
}

.notes {
  font-size: 0.875rem;
  color: #666;
  margin: 0;
  line-height: 1.6;
  background: white;
  padding: 0.75rem;
  border-radius: 4px;
  border-left: 4px solid #FF9800;
}

.estimated-time {
  font-size: 0.875rem;
  color: #666;
  margin: 0;
  background: white;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  display: inline-block;
}

@media (max-width: 768px) {
  .guide-content {
    padding: 1rem;
  }

  .section-content {
    padding-left: 1rem;
  }
}
</style>
