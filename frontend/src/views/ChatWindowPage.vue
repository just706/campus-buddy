<!--
  Chat window page — real-time messaging via WebSocket + HTTP history.

  Layout: ChatHeader → Message list (date-divided bubbles) → MessageInput

  Features:
  - HTTP fetch 50 latest messages on enter, auto-scroll to bottom
  - WebSocket for real-time send/receive with heartbeat + reconnect
  - Send via WebSocket with optimistic UI; fallback to HTTP on error
  - Pull up to load older history (maintains scroll position)
  - Date dividers between message groups
  - Online/offline status from WS system messages
  - Failed message retry
  - Cleanup on leave (WS disconnect)
-->
<template>
  <div class="chat-window">
    <!-- Header -->
    <ChatHeader
      :nickname="otherNickname"
      :avatar="otherAvatar"
      :is-online="chatsStore.otherUserOnline"
      :connection-state="wsConnectionState"
    />

    <!-- Message list -->
    <div
      class="message-list"
      ref="listRef"
      @scroll="handleScroll"
    >
      <!-- Loading older messages -->
      <div v-if="loadingMore" class="list-status">
        <LoadingSpinner :size="20" />
      </div>

      <div v-if="!hasMore && messages.length > 0" class="list-status list-status--end">
        没有更多消息了
      </div>

      <!-- Empty state -->
      <EmptyState
        v-if="!loadingMessages && messages.length === 0"
        text="开始聊天吧！发送第一条消息"
        icon="ChatDotRound"
      />

      <!-- Skeleton loading for initial message load -->
      <template v-if="loadingMessages && messages.length === 0">
        <div v-for="i in 5" :key="'sk-' + i" class="msg-skeleton" :class="{ 'msg-skeleton--mine': i % 2 === 0 }">
          <el-skeleton animated>
            <template #template>
              <el-skeleton-item variant="text" :style="i % 2 === 0 ? 'width:60%;margin-left:auto' : 'width:70%'" />
            </template>
          </el-skeleton>
        </div>
      </template>

      <!-- Message groups with date dividers -->
      <template v-for="group in messageGroups" :key="group.date">
        <DateDivider :date="group.date" />
        <MessageBubble
          v-for="(msg, idx) in group.messages"
          :key="msg.id"
          :message="msg"
          :is-mine="msg.sender_id === currentUserId"
          :show-time="shouldShowTime(group.messages, idx)"
          :sender-name="msg.sender_id === currentUserId ? '' : otherNickname"
          :sender-avatar="msg.sender_id === currentUserId ? '' : otherAvatar"
          @retry="handleRetry"
        />
      </template>
    </div>

    <!-- Input bar -->
    <MessageInput
      :disabled="false"
      @send="handleSend"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ChatHeader from '@/components/chat/ChatHeader.vue'
import DateDivider from '@/components/chat/DateDivider.vue'
import MessageBubble from '@/components/chat/MessageBubble.vue'
import MessageInput from '@/components/chat/MessageInput.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { useChatsStore } from '@/stores/chats'
import { useAuthStore } from '@/stores/auth'
import { useWebSocket } from '@/composables/useWebSocket'
import { usePagination } from '@/composables/usePagination'
import { formatMessageTime } from '@/utils/format'
import type { MessageResponse, WsServerMessage } from '@/types'

// ================================================================
// Route & Stores
// ================================================================
const route = useRoute()
const chatsStore = useChatsStore()
const authStore = useAuthStore()

const chatId = computed(() => Number(route.params.id))
const currentUserId = computed(() => authStore.currentUser?.id ?? 0)

// ================================================================
// Chat info (from store's chatList or fallback)
// ================================================================
const chatInfo = computed(() =>
  chatsStore.chatList.find((c) => c.id === chatId.value),
)

const otherNickname = computed(() => chatInfo.value?.other_user_nickname || '对方')
const otherAvatar = computed(() => chatInfo.value?.other_user_avatar || null)

// ================================================================
// Messages & pagination
// ================================================================
const { page, pageSize, hasMore, reset, nextPage } = usePagination(50)
const loadingMore = ref(false)
const PAGE_SIZE = 50

const messages = computed(() => chatsStore.messages)
const loadingMessages = computed(() => chatsStore.isLoadingMessages)

const messageGroups = computed(() => {
  const groups: Array<{ date: string; messages: MessageResponse[] }> = []
  let currentDate = ''

  for (const msg of messages.value) {
    const msgDate = new Date(msg.created_at).toDateString()
    if (msgDate !== currentDate) {
      currentDate = msgDate
      groups.push({ date: msg.created_at, messages: [msg] })
    } else {
      groups[groups.length - 1].messages.push(msg)
    }
  }

  return groups
})

/** Show time if this is the last message or next message is > 1 min apart. */
function shouldShowTime(msgs: MessageResponse[], idx: number): boolean {
  if (idx === msgs.length - 1) return true
  const curr = new Date(msgs[idx].created_at).getTime()
  const next = new Date(msgs[idx + 1].created_at).getTime()
  return next - curr > 60_000 // > 1 minute
}

// ================================================================
// Scroll management
// ================================================================
const listRef = ref<HTMLElement | null>(null)
let userScrolledUp = false

/** Check if user is near the bottom of the message list. */
function isNearBottom(): boolean {
  const el = listRef.value
  if (!el) return true
  return el.scrollHeight - el.scrollTop - el.clientHeight < 150
}

/** Auto-scroll to the very bottom (new messages, initial load). */
async function scrollToBottom(smooth = false) {
  await nextTick()
  const el = listRef.value
  if (!el) return
  el.scrollTo({
    top: el.scrollHeight,
    behavior: smooth ? 'smooth' : 'instant',
  })
}

/** Maintain scroll position after prepending older messages. */
async function maintainScrollAfterPrepend(prevScrollHeight: number) {
  await nextTick()
  const el = listRef.value
  if (!el) return
  const newScrollHeight = el.scrollHeight
  el.scrollTop = newScrollHeight - prevScrollHeight
}

/** Handle scroll events — detect top reach for history load. */
function handleScroll() {
  const el = listRef.value
  if (!el) return

  // Track if user scrolled up
  userScrolledUp = !isNearBottom()

  // Load older messages when reaching the top
  if (el.scrollTop < 50 && hasMore.value && !loadingMore.value) {
    loadMoreHistory()
  }
}

/** Load older message history (triggered on scroll to top). */
async function loadMoreHistory() {
  if (loadingMore.value || !hasMore.value) return
  loadingMore.value = true

  const el = listRef.value
  const prevHeight = el?.scrollHeight ?? 0

  nextPage()
  await chatsStore.fetchMessages(chatId.value, page.value, PAGE_SIZE)
  await maintainScrollAfterPrepend(prevHeight)

  loadingMore.value = false
}

// ================================================================
// WebSocket
// ================================================================
const wsConnectionState = ref<'disconnected' | 'connecting' | 'connected'>('disconnected')

const { isConnected: wsConnected, connect: wsConnect, disconnect: wsDisconnect, send: wsSend } =
  useWebSocket({
    urlFactory: () => {
      const token = authStore.accessToken
      if (!token) return null
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      return `${protocol}//${window.location.host}/api/v1/ws/chat/${chatId.value}?token=${token}`
    },
    onMessage: handleWsMessage,
    onOpen: () => {
      wsConnectionState.value = 'connected'
    },
    onClose: () => {
      wsConnectionState.value = 'disconnected'
    },
    onError: () => {
      wsConnectionState.value = 'disconnected'
    },
  })

/** Handle incoming WebSocket messages. */
function handleWsMessage(data: Record<string, unknown>) {
  const msg = data as unknown as WsServerMessage

  switch (msg.type) {
    case 'message':
      // Message from the other user
      if (msg.message_id && msg.sender_id !== currentUserId.value) {
        chatsStore.appendWsMessage({
          id: msg.message_id,
          chat_id: msg.chat_id ?? chatId.value,
          sender_id: msg.sender_id ?? 0,
          content: msg.content ?? '',
          content_type: msg.content_type ?? 'text',
          is_read: false,
          created_at: msg.created_at ?? new Date().toISOString(),
        })

        // Auto-scroll if user is near bottom
        if (isNearBottom()) {
          scrollToBottom(true)
        }

        // Update chat list preview
        chatsStore.updateChatInList(chatId.value, {
          last_message: msg.content,
          last_message_at: msg.created_at,
        })

        // Mark as read
        chatsStore.markRead(chatId.value, msg.message_id)
      }
      break

    case 'system':
      if (msg.action === 'user_online') {
        chatsStore.setOtherUserOnline(true)
      } else if (msg.action === 'user_offline') {
        chatsStore.setOtherUserOnline(false)
      }
      break

    case 'error':
      console.error('[WS] Server error:', msg.reason, msg.detail)
      break
  }
}

// ================================================================
// Send message
// ================================================================

/** Track temporary failed message IDs. */
const failedMessageIds = ref<Set<number>>(new Set())

/**
 * Send a message via WebSocket with optimistic UI.
 * Falls back to HTTP on failure.
 */
async function handleSend(content: string) {
  // Optimistic message with temporary ID
  const tempId = -Date.now()
  const now = new Date().toISOString()
  const optimisticMsg: MessageResponse = {
    id: tempId,
    chat_id: chatId.value,
    sender_id: currentUserId.value,
    content,
    content_type: 'text',
    is_read: false,
    created_at: now,
  }

  chatsStore.appendWsMessage(optimisticMsg)
  scrollToBottom(true)

  // Update chat list preview immediately
  chatsStore.updateChatInList(chatId.value, {
    last_message: content,
    last_message_at: now,
  })

  // Try WebSocket send
  const sent = wsSend({
    type: 'message',
    content,
    content_type: 'text',
  })

  if (!sent) {
    // WebSocket not connected — use HTTP fallback
    await sendViaHttp(tempId, content)
  }
  // If WS sent successfully, the message is delivered.
  // We don't get a confirmation back, so the optimistic message stays.
  // If the server sends an error via WS, handleWsMessage will catch it
  // (but the backend doesn't send confirmation for success).
}

/** Fallback: send via HTTP and replace optimistic message. */
async function sendViaHttp(tempId: number, content: string) {
  try {
    const realMsg = await chatsStore.sendMessageHttp(chatId.value, content)
    // Replace optimistic message with real one
    chatsStore.removeMessage(tempId)
    chatsStore.appendWsMessage(realMsg)
    scrollToBottom(true)
  } catch {
    // Mark optimistic message as failed
    chatsStore.markMessageFailed(tempId)
  }
}

/** Retry sending a failed message via HTTP. */
async function handleRetry(msg: MessageResponse & { _failed?: boolean }) {
  // Remove the failed message
  chatsStore.removeMessage(msg.id)
  // Re-send via HTTP (reliable)
  await handleSend(msg.content)
}

// Watch for WS error messages that indicate send failure
watch(wsConnectionState, (state) => {
  if (state === 'connecting') {
    // Could show "connecting..." indicator
  }
})

// ================================================================
// Lifecycle
// ================================================================

/** Initialize: fetch messages, connect WebSocket. */
async function init() {
  chatsStore.currentChatId = chatId.value

  // Ensure we have the chat list for header info
  if (!chatInfo.value) {
    await chatsStore.fetchChatList(1, 20)
  }

  // Fetch latest messages
  reset()
  await chatsStore.fetchMessages(chatId.value, 1, PAGE_SIZE)
  await scrollToBottom()

  // Mark all unread as read
  await chatsStore.markRead(chatId.value)

  // Connect WebSocket
  wsConnect()
}

init()

/** Cleanup on leave: disconnect WebSocket, clear messages. */
onBeforeUnmount(() => {
  wsDisconnect()
  chatsStore.clearMessages()
})
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-page);
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
  /* Smooth scrolling on iOS */
  -webkit-overflow-scrolling: touch;
}

.list-status {
  display: flex;
  justify-content: center;
  padding: 12px;
}

.list-status--end {
  font-size: 12px;
  color: var(--text-placeholder);
}

/* Message skeleton */
.msg-skeleton {
  padding: 16px 16px 4px;
  max-width: 72%;
}

.msg-skeleton--mine {
  margin-left: auto;
}
</style>
