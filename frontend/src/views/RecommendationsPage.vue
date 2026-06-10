<!-- Smart Recommendations (智能推荐) — AI/recommendation cards with match scores -->
<template>
  <div class="recommendations-page">
    <AppHeader title="智能推荐" />

    <LoadingSpinner v-if="loading" text="正在分析你的兴趣标签..." />

    <EmptyState
      v-else-if="!loading && recommendations.length === 0"
      text="完善你的兴趣标签和个人简介，AI 可以给你更精准的推荐哦～"
      action-text="完善资料"
      @action="router.push('/profile/edit')"
    />

    <div v-else class="rec-list">
      <RecommendationCard
        v-for="item in recommendations"
        :key="item.user.id"
        :item="item"
        :requested="requestedIds.has(item.user.id)"
        @match="handleMatch"
        @view-profile="router.push(`/users/${$event}`)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useMatchesStore } from '@/stores/matches'
import AppHeader from '@/components/common/AppHeader.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import RecommendationCard from '@/components/match/RecommendationCard.vue'

const router = useRouter()
const matchesStore = useMatchesStore()

const loading = ref(true)
const requestedIds = ref(new Set<number>())

const recommendations = ref(matchesStore.recommendations)

onMounted(async () => {
  try {
    await matchesStore.fetchRecommendations()
    recommendations.value = matchesStore.recommendations
  } finally {
    loading.value = false
  }
})

async function handleMatch(userId: number) {
  try {
    await matchesStore.requestMatch(userId)
    requestedIds.value.add(userId)
    ElMessage.success('匹配请求已发送')
  } catch (err: unknown) {
    ElMessage.error((err as Error)?.message || '请求失败')
  }
}
</script>

<style scoped>
.recommendations-page {
  min-height: 100vh;
  padding-bottom: 56px;
}

.rec-list {
  padding: 12px 16px;
}
</style>
