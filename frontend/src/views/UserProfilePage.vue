<!-- User Profile (他人资料) — public profile view of another user -->
<template>
  <div class="user-profile-page">
    <AppHeader title="用户资料" :show-back="true" />

    <LoadingSpinner v-if="loading" text="加载中..." />

    <template v-else-if="profile">
      <!-- User Brief Card -->
      <UserBriefCard :user="profile" />

      <!-- Match Action -->
      <div class="profile-actions" v-if="!isMe">
        <el-button
          type="primary"
          size="large"
          :disabled="matchSent"
          :loading="matchLoading"
          @click="handleMatchRequest"
          class="match-btn"
        >
          {{ matchSent ? '请求已发送' : '想和TA成为搭子' }}
        </el-button>
      </div>
    </template>

    <EmptyState
      v-else
      text="用户不存在"
      action-text="返回"
      @action="router.back()"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useMatchesStore } from '@/stores/matches'
import * as usersApi from '@/api/users'
import type { UserResponse } from '@/types'
import AppHeader from '@/components/common/AppHeader.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import UserBriefCard from '@/components/user/UserBriefCard.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const matchesStore = useMatchesStore()

const loading = ref(true)
const matchLoading = ref(false)
const matchSent = ref(false)
const profile = ref<UserResponse | null>(null)

const isMe = computed(() => profile.value?.id === authStore.currentUser?.id)

onMounted(async () => {
  const id = Number(route.params.id)
  try {
    profile.value = await usersApi.getUserById(id)
  } catch {
    profile.value = null
  } finally {
    loading.value = false
  }
})

async function handleMatchRequest() {
  if (!profile.value) return
  matchLoading.value = true
  try {
    await matchesStore.requestMatch(profile.value.id)
    matchSent.value = true
    ElMessage.success('请求已发送')
  } catch (err: unknown) {
    ElMessage.error((err as Error)?.message || '请求失败')
  } finally {
    matchLoading.value = false
  }
}
</script>

<style scoped>
.user-profile-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.profile-actions {
  padding: 16px;
}

.match-btn {
  width: 100%;
}
</style>
