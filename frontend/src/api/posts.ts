/**
 * Posts (邀约) API — CRUD, list, filter.
 */
import http from './client'
import type { PostCreate, PostUpdate, PostResponse, PostListResponse } from '@/types'

export async function createPost(data: PostCreate): Promise<PostResponse> {
  return http.post('/posts', data)
}

export interface ListPostsParams {
  category?: string
  tag?: string
  keyword?: string
  page?: number
  page_size?: number
}

export async function listPosts(params: ListPostsParams = {}): Promise<PostListResponse> {
  return http.get('/posts', { params })
}

export async function getPost(id: number): Promise<PostResponse> {
  return http.get(`/posts/${id}`)
}

export async function updatePost(id: number, data: PostUpdate): Promise<PostResponse> {
  return http.put(`/posts/${id}`, data)
}

export async function closePost(id: number): Promise<PostResponse> {
  return http.delete(`/posts/${id}`)
}
