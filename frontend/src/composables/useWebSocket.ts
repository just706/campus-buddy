/**
 * WebSocket composable — manages WebSocket lifecycle with heartbeat
 * and exponential backoff reconnect.
 *
 * ## Features
 * - Heartbeat: client sends `{"type":"ping"}` every 30s,
 *   expects pong within 60s or considers connection dead
 * - Reconnect: exponential backoff (1→2→4→8→… max 30s)
 * - Connection state tracking (disconnected / connecting / connected)
 * - Automatic cleanup on component unmount
 * - URL factory pattern for token refresh support
 *
 * ## Usage
 * ```ts
 * const { isConnected, connect, disconnect, send } = useWebSocket({
 *   urlFactory: () => `ws://host/ws/chat/${chatId}?token=${getToken()}`,
 *   onMessage: (data) => { ... },
 * })
 * connect()
 * ```
 */

import { ref, onUnmounted } from 'vue'

// ================================================================
// Types
// ================================================================

export interface WebSocketOptions {
  /**
   * Returns the WebSocket URL to connect to, or null if not ready.
   * Called on each connection attempt, so token can be refreshed between retries.
   */
  urlFactory: () => string | null

  /** Called with parsed JSON for each server message. */
  onMessage?: (data: Record<string, unknown>) => void

  /** Called when the connection opens. */
  onOpen?: () => void

  /** Called when the connection closes (before reconnect). */
  onClose?: () => void

  /** Called on WebSocket error. */
  onError?: (event: Event) => void

  /** Ping interval in ms (default 30000). */
  heartbeatInterval?: number

  /** Timeout for waiting for a pong in ms (default 60000). */
  heartbeatTimeout?: number

  /** Base reconnect delay in ms (default 1000). */
  reconnectBaseDelay?: number

  /** Maximum reconnect delay in ms (default 30000). */
  reconnectMaxDelay?: number
}

export type WsConnectionState = 'disconnected' | 'connecting' | 'connected'

// ================================================================
// Composable
// ================================================================

export function useWebSocket(options: WebSocketOptions) {
  const isConnected = ref(false)
  const connectionState = ref<WsConnectionState>('disconnected')

  const {
    urlFactory,
    onMessage,
    onOpen,
    onClose,
    onError,
    heartbeatInterval = 30_000,
    heartbeatTimeout = 60_000,
    reconnectBaseDelay = 1_000,
    reconnectMaxDelay = 30_000,
  } = options

  // Internal state
  let ws: WebSocket | null = null
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null
  let heartbeatTimeoutTimer: ReturnType<typeof setTimeout> | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let reconnectAttempts = 0
  let intentionalClose = false

  // ================================================================
  // Heartbeat
  // ================================================================

  function clearHeartbeat() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
    if (heartbeatTimeoutTimer) {
      clearTimeout(heartbeatTimeoutTimer)
      heartbeatTimeoutTimer = null
    }
  }

  function startHeartbeat() {
    clearHeartbeat()
    heartbeatTimer = setInterval(() => {
      send({ type: 'ping' })
      // Set a timeout — if no pong arrives, connection is dead
      heartbeatTimeoutTimer = setTimeout(() => {
        console.warn('[WS] Heartbeat timeout — closing connection')
        ws?.close()
      }, heartbeatTimeout)
    }, heartbeatInterval)
  }

  function handlePong() {
    if (heartbeatTimeoutTimer) {
      clearTimeout(heartbeatTimeoutTimer)
      heartbeatTimeoutTimer = null
    }
  }

  // ================================================================
  // Reconnect
  // ================================================================

  function clearReconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  function scheduleReconnect() {
    if (intentionalClose) return
    clearReconnect()
    const delay = Math.min(
      reconnectBaseDelay * Math.pow(2, reconnectAttempts),
      reconnectMaxDelay,
    )
    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${reconnectAttempts + 1})`)
    reconnectTimer = setTimeout(() => {
      reconnectAttempts++
      connect()
    }, delay)
  }

  // ================================================================
  // Connect / Disconnect
  // ================================================================

  function connect() {
    const url = urlFactory()
    if (!url) {
      console.warn('[WS] URL factory returned null — skipping connect')
      return
    }

    // Avoid duplicate connections
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      return
    }

    connectionState.value = 'connecting'

    try {
      ws = new WebSocket(url)
    } catch {
      console.error('[WS] Failed to create WebSocket')
      connectionState.value = 'disconnected'
      scheduleReconnect()
      return
    }

    ws.onopen = () => {
      isConnected.value = true
      connectionState.value = 'connected'
      reconnectAttempts = 0
      startHeartbeat()
      onOpen?.()
    }

    ws.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as Record<string, unknown>
        // Swallow pong — just resets the heartbeat timeout
        if (data.type === 'pong') {
          handlePong()
          return
        }
        onMessage?.(data)
      } catch {
        // Ignore non-JSON messages
      }
    }

    ws.onclose = () => {
      isConnected.value = false
      connectionState.value = 'disconnected'
      clearHeartbeat()
      onClose?.()
      ws = null
      scheduleReconnect()
    }

    ws.onerror = (event: Event) => {
      onError?.(event)
    }
  }

  function disconnect() {
    intentionalClose = true
    clearReconnect()
    clearHeartbeat()
    if (ws) {
      // Remove handler to prevent reconnect after intentional close
      ws.onclose = null
      ws.close()
      ws = null
    }
    isConnected.value = false
    connectionState.value = 'disconnected'
  }

  function send(data: unknown) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data))
      return true
    }
    return false
  }

  // ================================================================
  // Lifecycle
  // ================================================================

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    connectionState,
    connect,
    disconnect,
    send,
  }
}
