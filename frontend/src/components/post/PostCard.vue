<!-- Post card — summary card for the post square / list view -->
<template>
  <div class="post-card" @click="$emit('click', post.id)">
    <!-- Category + Status -->
    <div class="card-top">
      <CategoryBadge :category="post.category" size="small" />
      <PostStatusBadge v-if="post.status !== 'active'" :status="post.status" />
    </div>

    <!-- Title -->
    <h3 class="card-title">{{ post.title }}</h3>

    <!-- Description (2-line truncate) -->
    <p v-if="post.description" class="card-desc">{{ post.description }}</p>

    <!-- Location + Time -->
    <div class="card-meta" v-if="post.location || post.time_range">
      <span v-if="post.location" class="meta-item">
        <el-icon :size="14"><Location /></el-icon>
        {{ post.location }}
      </span>
      <span v-if="post.time_range" class="meta-item">
        <el-icon :size="14"><Clock /></el-icon>
        {{ post.time_range }}
      </span>
    </div>

    <!-- Tags -->
    <div class="card-tags" v-if="post.tags && post.tags.length">
      <el-tag
        v-for="tag in post.tags"
        :key="tag"
        size="small"
        class="tag-item"
        @click.stop="$emit('tag-click', tag)"
      >
        #{{ tag }}
      </el-tag>
    </div>

    <!-- Author + Time -->
    <div class="card-footer">
      <div class="author-info" v-if="post.user" @click.stop="$emit('user-click', post.user_id)">
        <UserAvatar :src="post.user.avatar" :name="post.user.nickname || post.user.username" :size="28" />
        <span class="author-name">{{ post.user.nickname || post.user.username }}</span>
        <span class="author-school">{{ post.user.university }}</span>
      </div>
      <span class="post-time">{{ relativeTime(post.created_at) }}</span>
    </div>

    <!-- Participant count -->
    <div class="card-count">
      <el-icon :size="14"><User /></el-icon>
      <span>{{ post.current_count }}/{{ post.target_count }} 人</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Location, Clock, User } from '@element-plus/icons-vue'
import type { PostResponse } from '@/types'
import { relativeTime } from '@/utils/format'
import CategoryBadge from '@/components/common/CategoryBadge.vue'
import PostStatusBadge from '@/components/post/PostStatusBadge.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'

defineProps<{
  post: PostResponse
}>()

defineEmits<{
  click: [id: number]
  'tag-click': [tag: string]
  'user-click': [userId: number]
}>()
</script>

<style scoped>
.post-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.2s;
  cursor: pointer;
  margin-bottom: 12px;
  position: relative;
}

.post-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 6px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-desc {
  font-size: 14px;
  color: #606266;
  margin: 0 0 8px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.tag-item {
  cursor: pointer;
  margin: 0;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.author-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

.author-school {
  font-size: 12px;
  color: #909399;
}

.post-time {
  font-size: 12px;
  color: #c0c4cc;
}

.card-count {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}
</style>
