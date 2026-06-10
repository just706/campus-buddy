/**
 * Chats store — chat list, messages, online status, unread count.
 *
 * Manages HTTP-based chat operations. WebSocket connection lifecycle
 * is handled by the `useWebSocket` composable in ChatWindowPage.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChatBriefResponse, MessageResponse } from '@/types'
import * as chatsApi from '@/api/chats'

export const useChatsStore = defineStore('chats', () => {
  // ===== State =====
  const chatList = ref<ChatBriefResponse[]>([])
  const chatListTotal = ref(0)
  const currentChatId = ref<number | null>(null)
  const messages = ref<MessageResponse[]>([])
  const messagesTotal = ref(0)
  const isLoading = ref(false)
  const isLoadingMessages = ref(false)
  const loadingMoreMessages = ref(false)

  /** Track largest message ID received via WebSocket for incremental pull. */
  const lastKnownMessageId = ref<number>(0)

  /** Online status of the other user in the current chat. */
  const otherUserOnline = ref(false)

  // ===== Getters =====

  /** Total unread messages across all chats — used by TabBar badge. */
  const unreadTotal = computed(() =>
    chatList.value.reduce((sum, c) => sum + (c.unread_count || 0), 0),
  )

  // ===== Chat List =====

  /** Fetch paginated chat list. Appends on page > 1. */
  async function fetchChatList(page = 1, pageSize = 20) {
    isLoading.value = true
    try {
      const result = await chatsApi.listChats({ page, page_size: pageSize })
      if (page === 1) {
        chatList.value = result.items
      } else {
        // Append, deduplicating by id
        const existingIds = new Set(chatList.value.map((c) => c.id))
        for (const chat of result.items) {
          if (!existingIds.has(chat.id)) {
            chatList.value.push(chat)
          }
        }
      }
      chatListTotal.value = result.total
    } finally {
      isLoading.value = false
    }
  }

  /** Update a single chat in the list (e.g., new last message). */
  function updateChatInList(chatId: number, updates: Partial<ChatBriefResponse>) {
    const idx = chatList.value.findIndex((c) => c.id === chatId)
    if (idx !== -1) {
      chatList.value[idx] = { ...chatList.value[idx], ...updates }
    }
  }

  // ===== Messages =====

  /** Fetch message history for a chat. */
  async function fetchMessages(
    chatId: number,
    page = 1,
    pageSize = 50,
    sinceId?: number,
  ) {
    if (page === 1) {
      isLoadingMessages.value = true
    } else {
      loadingMoreMessages.value = true
    }

    try {
      const result = await chatsApi.getMessages(chatId, {
        page,
        page_size: pageSize,
        since_id: sinceId,
      })

      if (page === 1 && !sinceId) {
        // Initial load — replace all
        messages.value = result.items
      } else if (sinceId) {
        // Incremental pull after reconnect — prepend
        const existingIds = new Set(messages.value.map((m) => m.id))
        const newMsgs = result.items.filter((m) => !existingIds.has(m.id))
        messages.value = [...newMsgs, ...messages.value]
      } else if (page > 1) {
        // Older history — prepend
        const existingIds = new Set(messages.value.map((m) => m.id))
        const olderMsgs = result.items.filter((m) => !existingIds.has(m.id))
        messages.value = [...olderMsgs, ...messages.value]
      }

      messagesTotal.value = result.total

      // Track max message ID
      for (const msg of result.items) {
        if (msg.id > lastKnownMessageId.value) {
          lastKnownMessageId.value = msg.id
        }
      }

      return result
    } finally {
      isLoadingMessages.value = false
      loadingMoreMessages.value = false
    }
  }

  /** Append a real-time message from WebSocket. */
  function appendWsMessage(msg: MessageResponse) {
    // Avoid duplicates
    if (messages.value.some((m) => m.id === msg.id)) return
    messages.value.push(msg)
    if (msg.id > lastKnownMessageId.value) {
      lastKnownMessageId.value = msg.id
    }
  }

  /** Mark a locally-failed message for retry UI. Internal; not persisted. */
  function markMessageFailed(tempId: number) {
    const msg = messages.value.find((m) => m.id === tempId)
    if (msg) {
      ;(msg as MessageResponse & { _failed: boolean })._failed = true
    }
  }

  /** Remove a local (failed) message from the list. */
  function removeMessage(msgId: number) {
    messages.value = messages.value.filter((m) => m.id !== msgId)
  }

  // ===== Send =====

  /**
   * Send a message via HTTP (fallback when WebSocket is not available).
   * Returns the created message from the server.
   */
  async function sendMessageHttp(chatId: number, content: string, contentType = 'text') {
    const msg = await chatsApi.sendMessage(chatId, { content, content_type: contentType })
    messages.value.push(msg)
    if (msg.id > lastKnownMessageId.value) {
      lastKnownMessageId.value = msg.id
    }
    // Update chat list preview
    updateChatInList(chatId, {
      last_message: content,
      last_message_at: msg.created_at,
    })
    return msg
  }

  // ===== Read Status =====

  /** Mark all unread messages in a chat as read on the server. */
  async function markRead(chatId: number, upToId?: number) {
    const count = await chatsApi.markRead(chatId, upToId)
    // Update local unread count
    const chat = chatList.value.find((c) => c.id === chatId)
    if (chat) {
      chat.unread_count = 0
    }
    return count
  }

  // ===== Online Status =====

  function setOtherUserOnline(online: boolean) {
    otherUserOnline.value = online
  }

  // ===== Reset =====

  /** Reset messages when navigating away from a chat window. */
  function clearMessages() {
    messages.value = []
    messagesTotal.value = 0
    currentChatId.value = null
    lastKnownMessageId.value = 0
    otherUserOnline.value = false
  }

  /** Full store reset (e.g., on logout). */
  function reset() {
    chatList.value = []
    chatListTotal.value = 0
    currentChatId.value = null
    messages.value = []
    messagesTotal.value = 0
    lastKnownMessageId.value = 0
    otherUserOnline.value = false
    isLoading.value = false
    isLoadingMessages.value = false
    loadingMoreMessages.value = false
  }

  return {
    // State
    chatList,
    chatListTotal,
    currentChatId,
    messages,
    messagesTotal,
    isLoading,
    isLoadingMessages,
    loadingMoreMessages,
    lastKnownMessageId,
    otherUserOnline,
    // Getters
    unreadTotal,
    // Chat list
    fetchChatList,
    updateChatInList,
    // Messages
    fetchMessages,
    appendWsMessage,
    markMessageFailed,
    removeMessage,
    // Send
    sendMessageHttp,
    // Read
    markRead,
    // Online
    setOtherUserOnline,
    // Lifecycle
    clearMessages,
    reset,
  }
})
