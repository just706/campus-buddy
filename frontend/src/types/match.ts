/** Match-related type definitions — matches backend match schemas. */

export interface MatchRequest {
  post_id?: number
}

export interface MatchAction {
  action: 'accept' | 'reject'
}

export interface MatchedUserBrief {
  id: number
  username: string
  nickname: string | null
  avatar: string | null
  university: string
  gender: string | null
  tags: string[] | null
}

export interface RecommendationItem {
  user: MatchedUserBrief
  match_score: number // 0-100
  ai_reason: string
}

export interface RecommendationResponse {
  recommendations: RecommendationItem[]
  total: number
}

export interface MatchDetailResponse {
  id: number
  user_id: number
  target_user_id: number
  post_id: number | null
  match_score: number | null
  ai_reason: string | null
  status: string // pending | accepted | rejected
  created_at: string
  updated_at: string
  user: MatchedUserBrief | null
  target_user: MatchedUserBrief | null
}

export interface MatchListResponse {
  items: MatchDetailResponse[]
  total: number
  page: number
  page_size: number
}
