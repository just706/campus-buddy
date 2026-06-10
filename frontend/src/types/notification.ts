/** Notification type definitions — matches backend notification schemas. */

export interface NotificationResponse {
  id: number
  user_id: number
  type: string // match | message | system
  title: string
  content: string
  is_read: boolean
  created_at: string
}

export interface NotificationListResponse {
  items: NotificationResponse[]
  total: number
  page: number
  page_size: number
  unread_count: number
}

export interface BatchReadRequest {
  ids: number[]
}
