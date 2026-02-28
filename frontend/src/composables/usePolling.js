/**
 * Composable for implementing polling mechanism
 * Polls a callback function at regular intervals
 */
import { ref, onUnmounted, getCurrentInstance } from 'vue'

export function usePolling(callback, interval = 10000) {
  const isPolling = ref(false)
  const lastUpdate = ref(null)
  let pollingTimer = null

  const startPolling = () => {
    if (isPolling.value) return

    isPolling.value = true
    pollingTimer = setInterval(async () => {
      try {
        await callback()
        lastUpdate.value = new Date()
      } catch (error) {
        console.error('Polling error:', error)
      }
    }, interval)
  }

  const stopPolling = () => {
    if (pollingTimer) {
      clearInterval(pollingTimer)
      pollingTimer = null
    }
    isPolling.value = false
  }

  const restartPolling = () => {
    stopPolling()
    startPolling()
  }

  // Cleanup on unmount (only if in component context)
  if (getCurrentInstance()) {
    onUnmounted(() => {
      stopPolling()
    })
  }

  return {
    isPolling,
    lastUpdate,
    startPolling,
    stopPolling,
    restartPolling
  }
}
