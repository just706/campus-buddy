<!-- Post Detail (邀约详情) — full post info, author card, match actions -->
<template>
  <div class="post-detail-page">
    <AppHeader title="邀约详情" :show-back="true" />

    <LoadingSpinner v-if="loading" text="加载中..." />

    <template v-else-if="post">
      <!-- Category + Status -->
      <div class="detail-header">
        <CategoryBadge :category="post.category" />
        <PostStatusBadge v-if="post.status !== 'active'" :status="post.status" />
      </div>

      <!-- Title -->
      <h1 class="detail-title">{{ post.title }}</h1>

      <!-- Meta -->
      <div class="detail-meta">
        <span class="detail-time">
          <el-icon :size="14"><Clock /></el-icon>
          发布于 {{ relativeTime(post.created_at) }}
        </span>
        <span class="detail-count">
          <el-icon :size="14"><User /></el-icon>
          {{ post.current_count }}/{{ post.target_count }} 人
        </span>
      </div>

      <!-- Description -->
      <div class="detail-section" v-if="post.description">
        <p class="detail-desc">{{ post.description }}</p>
      </div>

      <!-- Location + Time Range -->
      <div class="detail-info" v-if="post.location || post.time_range">
        <div class="info-item" v-if="post.location">
          <el-icon :size="16" color="#409EFF"><Location /></el-icon>
          <span>{{ post.location }}</span>
        </div>
        <div class="info-item" v-if="post.time_range">
          <el-icon :size="16" color="#67C23A"><Clock /></el-icon>
          <span>{{ post.time_range }}</span>
        </div>
      </div>

      <!-- Tags -->
      <div class="detail-tags" v-if="post.tags && post.tags.length">
        <el-tag v-for="tag in post.tags" :key="tag" size="default">#{{ tag }}</el-tag>
      </div>

      <!-- Divider -->
      <div class="divider" />

      <!-- Author Card -->
      <div class="author-card" v-if="post.user">
        <div class="author-header" @click="router.push(`/users/${post.user_id}`)">
          <UserAvatar :src="post.user.avatar" :name="post.user.nickname || post.user.username" :size="48" />
          <div class="author-info">
            <span class="author-name">{{ post.user.nickname || post.user.username }}</span>
            <span class="author-school">{{ post.user.university }}<span v-if="post.user.major"> · {{ post.user.major }}</span></span>
            <span v-if="post.user.grade" class="author-grade">{{ post.user.grade }}</span>
          </div>
          <el-icon :size="16"><ArrowRight /></el-icon>
        </div>
      </div>

      <!-- Actions -->
      <div class="detail-actions" v-if="post.status === 'active'">
        <!-- My own post -->
        <template v-if="isMyPost">
          <el-button type="primary" size="large" @click="router.push(`/posts/${post.id}/edit`)">
            编辑邀约
          </el-button>
          <el-button type="danger" size="large" plain @click="handleClose">
            关闭邀约
          </el-button>
        </template>
        <!-- Other user's post -->
        <template v-else>
          <el-button
            type="primary"
            size="large"
            :disabled="matchRequested"
            :loading="matchLoading"
            @click="handleMatchRequest"
            class="match-btn"
          >
            {{ matchRequested ? '请求已发送' : '我想和TA成为搭子' }}
          </el-button>
        </template>
      </div>
    </template>

    <!-- Error -->
    <EmptyState
      v-else
      text="邀约不存在或已删除"
      action-text="返回广场"
      @action="router.push('/posts')"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Clock, User, Location, ArrowRight } from '@element-plus/icons-vue'
import { usePostsStore } from '@/stores/posts'
import { useAuthStore } from '@/stores/auth'
import { useMatchesStore } from '@/stores/matches'
import { relativeTime } from '@/utils/format'
import AppHeader from '@/components/common/AppHeader.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import CategoryBadge from '@/components/common/CategoryBadge.vue'
import PostStatusBadge from '@/components/post/PostStatusBadge.vue'

const route = useRoute()
const router = useRouter()
const postsStore = usePostsStore()
const authStore = useAuthStore()
const matchesStore = useMatchesStore()

const loading = ref(true)
const matchLoading = ref(false)
const matchRequested = ref(false)

const post = computed(() => postsStore.currentPost)
const isMyPost = computed(() => post.value?.user_id === authStore.currentUser?.id)

onMounted(async () => {
  const id = Number(route.params.id)
  try {
    await postsStore.fetchPostById(id)
  } catch {
    // post will be null → handled in template
  } finally {
    loading.value = false
  }
})

async function handleMatchRequest() {
  if (!post.value) return
  try {
    await ElMessageBox.confirm(
      `确认要与 ${post.value.user?.nickname || post.value.user?.username || '该用户'} 成为搭子吗？`,
      '确认发起匹配',
      { confirmButtonText: '确认', cancelButtonText: '取消', type: 'info' },
    )
  } catch {
    return
  }

  matchLoading.value = true
  try {
    await matchesStore.requestMatch(post.value.user_id, post.value.id)
    matchRequested.value = true
    ElMessage.success('请求已发送')
  } catch (err: unknown) {
    const msg = (err as Error)?.message || '请求发送失败'
    ElMessage.error(msg)
  } finally {
    matchLoading.value = false
  }
}

async function handleClose() {
  if (!post.value) return
  try {
    await ElMessageBox.confirm(
      '确认关闭这个邀约吗？关闭后不可恢复。',
      '关闭邀约',
      { confirmButtonText: '确认关闭', cancelButtonText: '取消', type: 'warning' },
    )
  } catch {
    return
  }
  try {
    await postsStore.closePost(post.value.id)
    ElMessage.success('邀约已关闭')
  } catch (err: unknown) {
    ElMessage.error((err as Error)?.message || '关闭失败')
  }
}
</script>

<style scoped>
.post-detail-page {
  min-height: 100vh;
  background: #fff;
  padding-bottom: 40px;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px 0;
}

.detail-title {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
  margin: 12px 16px 8px;
  line-height: 1.4;
}

.detail-meta {
  display: flex;
  gap: 16px;
  padding: 0 16px;
  font-size: 13px;
  color: #909399;
}

.detail-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.detail-section {
  padding: 16px;
}

.detail-desc {
  font-size: 15px;
  color: #303133;
  line-height: 1.8;
  white-space: pre-wrap;
  margin: 0;
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 16px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
  background: #f5f7fa;
  padding: 10px 12px;
  border-radius: 8px;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 0 16px;
  margin-bottom: 16px;
}

.divider {
  height: 8px;
  background: #f5f7fa;
  margin: 0;
}

.author-card {
  padding: 16px;
}

.author-header {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.author-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.author-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.author-school {
  font-size: 13px;
  color: #606266;
}

.author-grade {
  font-size: 12px;
  color: #909399;
}

.detail-actions {
  padding: 16px;
  display: flex;
  gap: 12px;
}

.match-btn {
  flex: 1;
}
</style>
