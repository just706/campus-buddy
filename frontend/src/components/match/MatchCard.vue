<!-- Match card — match list item with status, other user info, actions -->
<template>
  <div class="match-card" @click="handleClick">
    <div class="match-main">
      <UserAvatar
        :src="otherUser?.avatar"
        :name="otherUser?.nickname || otherUser?.username || '?'"
        :size="44"
      />
      <div class="match-info">
        <span class="match-name">{{ otherUser?.nickname || otherUser?.username || '未知用户' }}</span>
        <span class="match-school" v-if="otherUser?.university">
          {{ otherUser.university }}<span v-if="otherUser.grade"> · {{ otherUser.grade }}</span>
        </span>
        <div class="match-meta">
          <MatchStatusBadge :status="match.status" />
          <MatchScoreBadge v-if="match.match_score != null" :score="match.match_score" size="small" />
          <span class="match-time">{{ relativeTime(match.updated_at) }}</span>
        </div>
      </div>
    </div>
    <div class="match-actions" v-if="isPending" @click.stop>
      <template v-if="isIncoming">
        <el-button type="primary" size="small" @click="$emit('accept', match.id)">接受</el-button>
        <el-button type="danger" size="small" plain @click="$emit('reject', match.id)">拒绝</el-button>
      </template>
      <span v-else class="waiting-text">等待对方回应</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { MatchDetailResponse, MatchedUserBrief } from '@/types'
import { relativeTime } from '@/utils/format'
import MatchStatusBadge from '@/components/match/MatchStatusBadge.vue'
import MatchScoreBadge from '@/components/match/MatchScoreBadge.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'

const props = defineProps<{
  match: MatchDetailResponse
}>()

defineEmits<{
  accept: [id: number]
  reject: [id: number]
}>()

const router = useRouter()
const authStore = useAuthStore()

const isPending = computed(() => props.match.status === 'pending')
const isIncoming = computed(() => props.match.target_user_id === authStore.currentUser?.id)
const otherUser = computed((): MatchedUserBrief | null => {
  if (isIncoming.value) return props.match.user
  return props.match.target_user
})

function handleClick() {
  if (!isPending.value) {
    // Navigate to chat (chat ID = match ID pattern)
    router.push(`/chats/${props.match.id}`)
  }
}
</script>

<style scoped>
.match-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 10px;
  transition: box-shadow 0.2s;
  cursor: pointer;
}

.match-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.match-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.match-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.match-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.match-school {
  font-size: 12px;
  color: #909399;
}

.match-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
}

.match-time {
  font-size: 11px;
  color: #c0c4cc;
  margin-left: auto;
}

.match-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.waiting-text {
  font-size: 13px;
  color: #909399;
}
</style>
