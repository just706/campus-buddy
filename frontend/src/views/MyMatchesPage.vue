<!-- My Matches (我的匹配) — match list with status filtering and actions -->
<template>
  <div class="my-matches-page">
    <AppHeader title="我的匹配" />

    <!-- Status Filter Tabs -->
    <div class="filter-tabs">
      <div
        v-for="tab in filterTabs"
        :key="tab.value"
        class="filter-tab"
        :class="{ 'filter-tab--active': activeStatus === tab.value }"
        @click="switchFilter(tab.value)"
      >
        {{ tab.label }}
      </div>
    </div>

    <!-- Match List -->
    <LoadingSpinner v-if="loading" text="加载中..." />

    <EmptyState
      v-else-if="!loading && matches.length === 0"
      text="还没有匹配记录，去发现页找搭子吧！"
      :icon="Connection"
      action-text="去发现"
      @action="router.push('/posts')"
    />

    <div v-else class="match-list">
      <MatchCard
        v-for="match in matches"
        :key="match.id"
        :match="match"
        @accept="handleAction($event, 'accept')"
        @reject="handleAction($event, 'reject')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Connection } from '@element-plus/icons-vue'
import { useMatchesStore } from '@/stores/matches'
import AppHeader from '@/components/common/AppHeader.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import MatchCard from '@/components/match/MatchCard.vue'

const router = useRouter()
const matchesStore = useMatchesStore()

const loading = ref(true)
const activeStatus = ref<string | undefined>(undefined)

const filterTabs = [
  { value: undefined, label: '全部' },
  { value: 'pending', label: '待确认' },
  { value: 'accepted', label: '已匹配' },
  { value: 'rejected', label: '已拒绝' },
]

const matches = ref(matchesStore.matches)

onMounted(async () => {
  await loadMatches()
})

async function loadMatches() {
  loading.value = true
  try {
    await matchesStore.fetchMyMatches(1, 20, activeStatus.value)
    matches.value = matchesStore.matches
  } finally {
    loading.value = false
  }
}

function switchFilter(status: string | undefined) {
  activeStatus.value = status
  loadMatches()
}

async function handleAction(matchId: number, action: 'accept' | 'reject') {
  const actionLabel = action === 'accept' ? '接受' : '拒绝'
  try {
    await ElMessageBox.confirm(
      `确认${actionLabel}这个匹配请求吗？`,
      `${actionLabel}匹配`,
      { confirmButtonText: actionLabel, cancelButtonText: '取消', type: action === 'accept' ? 'info' : 'warning' },
    )
  } catch {
    return
  }
  try {
    const result = await matchesStore.handleMatchAction(matchId, action)
    // Update the local list
    const idx = matches.value.findIndex(m => m.id === matchId)
    if (idx >= 0) {
      matches.value[idx] = result
    }
    ElMessage.success(action === 'accept' ? '匹配成功！开始聊天吧' : '已拒绝')
    if (action === 'accept') {
      router.push(`/chats/${matchId}`)
    }
  } catch (err: unknown) {
    ElMessage.error((err as Error)?.message || '操作失败')
  }
}
</script>

<style scoped>
.my-matches-page {
  min-height: 100vh;
}

.filter-tabs {
  display: flex;
  padding: 8px 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  gap: 0;
}

.filter-tab {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  font-size: 14px;
  color: #909399;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tab--active {
  color: #409eff;
  border-bottom-color: #409eff;
  font-weight: 600;
}

.match-list {
  padding: 12px 16px;
}
</style>
