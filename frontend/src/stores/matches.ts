/**
 * Matches store — recommendations, match list, request/accept/reject.
 * Placeholder: full implementation in Stage 2.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { RecommendationItem, MatchDetailResponse } from '@/types'
import * as matchesApi from '@/api/matches'

export const useMatchesStore = defineStore('matches', () => {
  const recommendations = ref<RecommendationItem[]>([])
  const matches = ref<MatchDetailResponse[]>([])
  const isLoading = ref(false)

  async function fetchRecommendations(limit = 10) {
    isLoading.value = true
    try {
      const result = await matchesApi.getRecommendations(limit)
      recommendations.value = result.recommendations
    } finally {
      isLoading.value = false
    }
  }

  async function requestMatch(targetUserId: number, postId?: number) {
    await matchesApi.requestMatch(targetUserId, { post_id: postId })
  }

  async function handleMatchAction(matchId: number, action: 'accept' | 'reject') {
    const result = await matchesApi.handleMatchAction(matchId, { action })
    // Update local state
    const idx = matches.value.findIndex((m) => m.id === matchId)
    if (idx >= 0) matches.value[idx] = result
    return result
  }

  async function fetchMyMatches(page = 1, pageSize = 20, status?: string) {
    isLoading.value = true
    try {
      const result = await matchesApi.listMatches({ page, page_size: pageSize, status })
      matches.value = result.items
    } finally {
      isLoading.value = false
    }
  }

  function reset() {
    recommendations.value = []
    matches.value = []
  }

  return {
    recommendations,
    matches,
    isLoading,
    fetchRecommendations,
    requestMatch,
    handleMatchAction,
    fetchMyMatches,
    reset,
  }
})
