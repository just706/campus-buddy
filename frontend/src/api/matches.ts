/**
 * Matches API — recommendations, match requests, actions, list.
 */
import http from './client'
import type {
  RecommendationResponse,
  MatchDetailResponse,
  MatchListResponse,
  MatchRequest,
  MatchAction,
} from '@/types'

export async function getRecommendations(limit = 10): Promise<RecommendationResponse> {
  return http.get('/matches/recommendations', { params: { limit } })
}

export async function requestMatch(
  targetUserId: number,
  body: MatchRequest = {},
): Promise<MatchDetailResponse> {
  return http.post(`/matches/request/${targetUserId}`, body)
}

export async function handleMatchAction(
  matchId: number,
  body: MatchAction,
): Promise<MatchDetailResponse> {
  return http.post(`/matches/${matchId}/action`, body)
}

export interface ListMatchesParams {
  page?: number
  page_size?: number
  status?: string
}

export async function listMatches(params: ListMatchesParams = {}): Promise<MatchListResponse> {
  return http.get('/matches', { params })
}
