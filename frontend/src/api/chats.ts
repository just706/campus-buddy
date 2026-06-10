/**
 * Chats API — chat list, message history, send message, mark read.
 */
import http from './client'
import type {
  ChatListResponse,
  MessageListResponse,
  MessageResponse,
  SendMessageRequest,
} from '@/types'

export interface ListChatsParams {
  page?: number
  page_size?: number
}

export async function listChats(params: ListChatsParams = {}): Promise<ChatListResponse> {
  return http.get('/chats', { params })
}

export interface GetMessagesParams {
  page?: number
  page_size?: number
  since_id?: number
}

export async function getMessages(
  chatId: number,
  params: GetMessagesParams = {},
): Promise<MessageListResponse> {
  return http.get(`/chats/${chatId}/messages`, { params })
}

export async function sendMessage(
  chatId: number,
  data: SendMessageRequest,
): Promise<MessageResponse> {
  return http.post(`/chats/${chatId}/messages`, data)
}

export async function markRead(chatId: number, upToId?: number): Promise<number> {
  return http.post(`/chats/${chatId}/messages/read`, null, {
    params: upToId ? { up_to_id: upToId } : {},
  })
}
