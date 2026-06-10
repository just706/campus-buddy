/**
 * Chats store — chat list, messages, WebSocket state.
 * Placeholder: full implementation in Stage 3.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChatBriefResponse, MessageResponse } from '@/types'
import * as chatsApi from '@/api/chats'

export const useChatsStore = defineStore('chats', () => {
  const chatList = ref<ChatBriefResponse[]>([])
  const currentChatId = ref<number | null>(null)
  const messages = ref<MessageResponse[]>([])
  const wsConnected = ref(false)
  const isLoading = ref(false)

  const unreadTotal = computed(() =>
    chatList.value.reduce((sum, c) => sum + (c.unread_count || 0), 0),
  )

  async function fetchChatList(page = 1, pageSize = 20) {
    isLoading.value = true
    try {
      const result = await chatsApi.listChats({ page, page_size: pageSize })
      chatList.value = result.items
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMessages(chatId: number, page = 1, pageSize = 50, sinceId?: number) {
    const result = await chatsApi.getMessages(chatId, { page, page_size: pageSize, since_id: sinceId })
    if (page === 1 && !sinceId) {
      messages.value = result.items
    } else if (sinceId) {
      // Prepend older messages for incremental pull
      messages.value = [...result.items, ...messages.value]
    } else {
      messages.value = [...messages.value, ...result.items]
    }
    return result
  }

  async function sendMessage(chatId: number, content: string, contentType = 'text') {
    const msg = await chatsApi.sendMessage(chatId, { content, content_type: contentType })
    messages.value.push(msg)
    return msg
  }

  async function markRead(chatId: number) {
    await chatsApi.markRead(chatId)
    // Update local unread count
    const chat = chatList.value.find((c) => c.id === chatId)
    if (chat) chat.unread_count = 0
  }

  function connectWS(_chatId: number, _token: string) {
    wsConnected.value = true
    // Full WebSocket implementation in Stage 3
  }

  function disconnectWS() {
    wsConnected.value = false
  }

  function reset() {
    chatList.value = []
    currentChatId.value = null
    messages.value = []
    wsConnected.value = false
  }

  return {
    chatList,
    currentChatId,
    messages,
    wsConnected,
    isLoading,
    unreadTotal,
    fetchChatList,
    fetchMessages,
    sendMessage,
    markRead,
    connectWS,
    disconnectWS,
    reset,
  }
})
