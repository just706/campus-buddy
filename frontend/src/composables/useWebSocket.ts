/**
 * WebSocket composable — manages WebSocket lifecycle with heartbeat
 * and exponential backoff reconnect.
 *
 * Full implementation in Stage 3 (Chat module).
 */

import { ref, onUnmounted } from 'vue'

export function useWebSocket(_url: string) {
  const isConnected = ref(false)
  const lastMessage = ref<unknown>(null)

  function connect() {
    isConnected.value = true
    // Full WebSocket implementation in Stage 3
  }

  function disconnect() {
    isConnected.value = false
  }

  function send(_data: unknown) {
    // Implementation in Stage 3
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    lastMessage,
    connect,
    disconnect,
    send,
  }
}
