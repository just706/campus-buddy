/** Chat and Message type definitions — matches backend chat schemas. */

export interface ChatBriefResponse {
  id: number
  match_id: number
  user1_id: number
  user2_id: number
  other_user_nickname: string | null
  other_user_avatar: string | null
  last_message: string | null
  last_message_at: string | null
  unread_count: number
  created_at: string
}

export interface ChatListResponse {
  items: ChatBriefResponse[]
  total: number
  page: number
  page_size: number
}

export interface MessageResponse {
  id: number
  chat_id: number
  sender_id: number
  content: string
  content_type: string // text | image
  is_read: boolean
  created_at: string
}

export interface MessageListResponse {
  items: MessageResponse[]
  total: number
  page: number
  page_size: number
}

export interface SendMessageRequest {
  content: string
  content_type: string // text | image
}

/** WebSocket client → server message. */
export interface WsClientMessage {
  type: 'message' | 'ping'
  content?: string
  content_type?: string
}

/** WebSocket server → client message. */
export interface WsServerMessage {
  type: 'message' | 'system' | 'pong' | 'error'
  message_id?: number
  chat_id?: number
  sender_id?: number
  sender_nickname?: string
  sender_avatar?: string
  content?: string
  content_type?: string
  created_at?: string
  // System message fields
  action?: string
  user_id?: number
  // Error fields
  reason?: string
  detail?: string
}
