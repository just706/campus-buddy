/**
 * Notifications store — list, unread count, read/batch operations.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { NotificationResponse } from '@/types'
import * as notifApi from '@/api/notifications'

export const useNotificationsStore = defineStore('notifications', () => {
  const notifications = ref<NotificationResponse[]>([])
  const unreadCount = ref(0)
  const total = ref(0)
  const isLoading = ref(false)

  async function fetchNotifications(page = 1, pageSize = 20, unreadOnly = false) {
    isLoading.value = true
    try {
      const result = await notifApi.listNotifications({
        page,
        page_size: pageSize,
        unread_only: unreadOnly,
      })
      if (page === 1) {
        notifications.value = result.items
      } else {
        notifications.value.push(...result.items)
      }
      total.value = result.total
      unreadCount.value = result.unread_count
    } finally {
      isLoading.value = false
    }
  }

  async function markRead(id: number) {
    await notifApi.markNotificationRead(id)
    const n = notifications.value.find((n) => n.id === id)
    if (n && !n.is_read) {
      n.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
  }

  async function markAllRead() {
    const count = await notifApi.markAllRead()
    notifications.value.forEach((n) => (n.is_read = true))
    unreadCount.value = 0
    return count
  }

  async function markBatchRead(ids: number[]) {
    const count = await notifApi.batchRead(ids)
    ids.forEach((id) => {
      const n = notifications.value.find((n) => n.id === id)
      if (n && !n.is_read) {
        n.is_read = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    })
    return count
  }

  function reset() {
    notifications.value = []
    unreadCount.value = 0
    total.value = 0
  }

  return {
    notifications,
    unreadCount,
    total,
    isLoading,
    fetchNotifications,
    markRead,
    markAllRead,
    markBatchRead,
    reset,
  }
})
