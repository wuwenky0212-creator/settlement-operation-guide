<template>
  <div class="progress-stepper">
    <div class="stepper-container">
      <div
        v-for="(step, index) in steps"
        :key="index"
        class="step-wrapper"
      >
        <!-- Step Node -->
        <div class="step-node" :class="getStepClass(step.status)">
          <div class="step-icon">
            <span v-if="step.status === 'completed'">✓</span>
            <span v-else-if="step.status === 'failed'">✗</span>
            <span v-else-if="step.status === 'current'">{{ index + 1 }}</span>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <div class="step-label">{{ step.label }}</div>
        </div>

        <!-- Connector Line -->
        <div
          v-if="index < steps.length - 1"
          class="step-connector"
          :class="getConnectorClass(step.status, steps[index + 1].status)"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  steps: {
    type: Array,
    required: true,
    // Expected format: [{ label: '交易点', status: 'completed' | 'current' | 'pending' | 'failed' }]
  }
})

// Methods
const getStepClass = (status) => {
  return {
    'step-completed': status === 'completed',
    'step-current': status === 'current',
    'step-pending': status === 'pending',
    'step-failed': status === 'failed'
  }
}

const getConnectorClass = (currentStatus, nextStatus) => {
  if (currentStatus === 'completed' && (nextStatus === 'completed' || nextStatus === 'current')) {
    return 'connector-active'
  }
  if (currentStatus === 'failed') {
    return 'connector-failed'
  }
  return 'connector-inactive'
}
</script>

<style scoped>
.progress-stepper {
  margin-top: 2rem;
  padding: 1.5rem;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.stepper-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.step-wrapper {
  display: flex;
  align-items: center;
  flex: 1;
}

.step-wrapper:last-child {
  flex: 0;
}

.step-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 1;
}

.step-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 2px solid #e0e0e0;
  background: white;
  color: #999;
}

.step-completed .step-icon {
  background: #4CAF50;
  border-color: #4CAF50;
  color: white;
}

.step-current .step-icon {
  background: #D32F2F;
  border-color: #D32F2F;
  color: white;
  box-shadow: 0 0 0 4px rgba(211, 47, 47, 0.1);
  animation: pulse-ring 2s infinite;
}

.step-pending .step-icon {
  background: white;
  border-color: #e0e0e0;
  color: #999;
}

.step-failed .step-icon {
  background: #F44336;
  border-color: #F44336;
  color: white;
}

@keyframes pulse-ring {
  0%, 100% {
    box-shadow: 0 0 0 4px rgba(211, 47, 47, 0.1);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(211, 47, 47, 0.05);
  }
}

.step-label {
  font-size: 0.875rem;
  font-weight: 500;
  text-align: center;
  color: #666;
  white-space: nowrap;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.step-completed .step-label {
  color: #4CAF50;
  font-weight: 600;
}

.step-current .step-label {
  color: #D32F2F;
  font-weight: 600;
}

.step-failed .step-label {
  color: #F44336;
  font-weight: 600;
}

.step-connector {
  flex: 1;
  height: 3px;
  margin: 0 0.5rem;
  position: relative;
  top: -20px;
  transition: all 0.3s ease;
}

.connector-active {
  background: #4CAF50;
}

.connector-inactive {
  background: #e0e0e0;
}

.connector-failed {
  background: #F44336;
}

/* Responsive */
@media (max-width: 768px) {
  .stepper-container {
    overflow-x: auto;
    justify-content: flex-start;
    padding-bottom: 1rem;
  }

  .step-wrapper {
    flex: 0 0 auto;
    min-width: 80px;
  }

  .step-icon {
    width: 32px;
    height: 32px;
    font-size: 0.875rem;
  }

  .step-label {
    font-size: 0.75rem;
    max-width: 80px;
  }

  .step-connector {
    min-width: 40px;
  }
}
</style>
