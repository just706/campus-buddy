/**
 * Notifications API — list, mark read, batch operations.
 */
import http from './client'
import type { NotificationListResponse, NotificationResponse } from '@/types'

export interface ListNotificationsParams {
  page?: number
  page_size?: number
  unread_only?: boolean
}

export async function listNotifications(
  params: ListNotificationsParams = {},
): Promise<NotificationListResponse> {
  return http.get('/notifications', { params })
}

export async function markNotificationRead(id: number): Promise<NotificationResponse> {
  return http.put(`/notifications/${id}/read`)
}

export async function markAllRead(): Promise<number> {
  return http.put('/notifications/read-all')
}

export async function batchRead(ids: number[]): Promise<number> {
  return http.put('/notifications/batch-read', { ids })
}
