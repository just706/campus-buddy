/** Post (邀约) related type definitions — matches backend post schemas. */

export interface PostCreate {
  title: string
  description?: string
  category: string // study | sports | dining | travel | other
  tags?: string[]
  target_count: number
  location?: string
  time_range?: string
  expires_at?: string
}

export interface PostUpdate {
  title?: string
  description?: string
  category?: string
  tags?: string[]
  target_count?: number
  location?: string
  time_range?: string
  expires_at?: string
}

export interface PostFilter {
  category?: string
  tag?: string
  keyword?: string
  page: number
  page_size: number
}

export interface PostResponse {
  id: number
  user_id: number
  title: string
  description: string
  category: string
  tags: string[] | null
  target_count: number
  current_count: number
  location: string | null
  time_range: string | null
  status: string
  expires_at: string | null
  created_at: string
  updated_at: string
}

export interface PostListResponse {
  items: PostResponse[]
  total: number
  page: number
  page_size: number
}
