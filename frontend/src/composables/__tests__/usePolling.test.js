import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { usePolling } from '../usePolling'

describe('usePolling', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should start polling and call callback at intervals', async () => {
    const callback = vi.fn().mockResolvedValue(undefined)
    const { startPolling, isPolling } = usePolling(callback, 1000)

    expect(isPolling.value).toBe(false)

    startPolling()
    expect(isPolling.value).toBe(true)

    // Fast-forward time by 1 second
    await vi.advanceTimersByTimeAsync(1000)
    expect(callback).toHaveBeenCalledTimes(1)

    // Fast-forward time by another 2 seconds
    await vi.advanceTimersByTimeAsync(2000)
    expect(callback).toHaveBeenCalledTimes(3)
  })

  it('should stop polling when stopPolling is called', async () => {
    const callback = vi.fn().mockResolvedValue(undefined)
    const { startPolling, stopPolling, isPolling } = usePolling(callback, 1000)

    startPolling()
    expect(isPolling.value).toBe(true)

    await vi.advanceTimersByTimeAsync(1000)
    expect(callback).toHaveBeenCalledTimes(1)

    stopPolling()
    expect(isPolling.value).toBe(false)

    // Advance time further - callback should not be called
    await vi.advanceTimersByTimeAsync(2000)
    expect(callback).toHaveBeenCalledTimes(1)
  })

  it('should update lastUpdate timestamp after successful callback', async () => {
    const callback = vi.fn().mockResolvedValue(undefined)
    const { startPolling, lastUpdate } = usePolling(callback, 1000)

    expect(lastUpdate.value).toBeNull()

    startPolling()
    await vi.advanceTimersByTimeAsync(1000)

    expect(lastUpdate.value).toBeInstanceOf(Date)
  })

  it('should handle callback errors gracefully', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const callback = vi.fn().mockRejectedValue(new Error('Test error'))
    const { startPolling, isPolling } = usePolling(callback, 1000)

    startPolling()
    await vi.advanceTimersByTimeAsync(1000)

    expect(callback).toHaveBeenCalledTimes(1)
    expect(consoleErrorSpy).toHaveBeenCalled()
    expect(isPolling.value).toBe(true) // Should continue polling despite error

    consoleErrorSpy.mockRestore()
  })

  it('should not start polling if already polling', async () => {
    const callback = vi.fn().mockResolvedValue(undefined)
    const { startPolling, isPolling } = usePolling(callback, 1000)

    startPolling()
    expect(isPolling.value).toBe(true)

    // Try to start again
    startPolling()
    
    await vi.advanceTimersByTimeAsync(1000)
    // Should only be called once per interval, not twice
    expect(callback).toHaveBeenCalledTimes(1)
  })

  it('should restart polling correctly', async () => {
    const callback = vi.fn().mockResolvedValue(undefined)
    const { startPolling, restartPolling } = usePolling(callback, 1000)

    startPolling()
    await vi.advanceTimersByTimeAsync(1000)
    expect(callback).toHaveBeenCalledTimes(1)

    restartPolling()
    await vi.advanceTimersByTimeAsync(1000)
    expect(callback).toHaveBeenCalledTimes(2)
  })
})
