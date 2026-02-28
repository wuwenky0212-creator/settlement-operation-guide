<template>
  <transition name="fade">
    <div 
      v-if="visible" 
      class="message-alert"
      :class="[`message-${type}`]"
    >
      <div class="message-icon">
        <span v-if="type === 'success'">✓</span>
        <span v-else-if="type === 'error'">✕</span>
        <span v-else-if="type === 'warning'">!</span>
        <span v-else>ℹ</span>
      </div>
      <div class="message-content">
        <div class="message-title" v-if="title">{{ title }}</div>
        <div class="message-text">{{ message }}</div>
      </div>
      <button class="message-close" @click="handleClose">✕</button>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  title: {
    type: String,
    default: ''
  },
  message: {
    type: String,
    required: true
  },
  duration: {
    type: Number,
    default: 3000
  },
  closable: {
    type: Boolean,
    default: true
  },
  modelValue: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

const visible = ref(props.modelValue)
let timer = null

watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
  if (newVal && props.duration > 0) {
    startTimer()
  }
})

onMounted(() => {
  if (visible.value && props.duration > 0) {
    startTimer()
  }
})

const startTimer = () => {
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => {
    handleClose()
  }, props.duration)
}

const handleClose = () => {
  visible.value = false
  emit('update:modelValue', false)
  emit('close')
  if (timer) clearTimeout(timer)
}
</script>

<style scoped>
.message-alert {
  display: flex;
  align-items: flex-start;
  padding: 12px 16px;
  margin-bottom: 12px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  border-left: 4px solid;
}

.message-success {
  border-left-color: #52c41a;
}

.message-error {
  border-left-color: #D32F2F;
}

.message-warning {
  border-left-color: #faad14;
}

.message-info {
  border-left-color: #1890ff;
}

.message-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  margin-right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
}

.message-success .message-icon {
  color: #52c41a;
}

.message-error .message-icon {
  color: #D32F2F;
}

.message-warning .message-icon {
  color: #faad14;
}

.message-info .message-icon {
  color: #1890ff;
}

.message-content {
  flex: 1;
}

.message-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.message-text {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.message-close {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  margin-left: 12px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #999;
  transition: color 0.2s;
}

.message-close:hover {
  color: #333;
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
