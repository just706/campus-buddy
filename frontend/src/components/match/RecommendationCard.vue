<!-- Recommendation card — match score + user info + reason -->
<template>
  <div class="recommendation-card">
    <div class="rec-left">
      <MatchScoreBadge :score="item.match_score" size="large" />
    </div>
    <div class="rec-body">
      <div class="rec-user" @click="$emit('view-profile', item.user.id)">
        <UserAvatar :src="item.user.avatar" :name="item.user.nickname || item.user.username" :size="40" />
        <div class="rec-user-info">
          <span class="rec-name">{{ item.user.nickname || item.user.username }}</span>
          <span class="rec-school">{{ item.user.university }}<span v-if="item.user.grade"> · {{ item.user.grade }}</span></span>
        </div>
      </div>
      <div class="rec-tags" v-if="item.user.tags && item.user.tags.length">
        <el-tag v-for="tag in item.user.tags" :key="tag" size="small" class="rec-tag">#{{ tag }}</el-tag>
      </div>
      <p class="rec-reason">
        <el-icon :size="14"><MagicStick /></el-icon>
        {{ item.ai_reason }}
      </p>
    </div>
    <div class="rec-actions">
      <el-button
        v-if="!requested"
        type="primary"
        size="small"
        :icon="Connection"
        @click.stop="$emit('match', item.user.id)"
      >
        想搭
      </el-button>
      <el-tag v-else type="info" size="small">请求已发送</el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Connection, MagicStick } from '@element-plus/icons-vue'
import type { RecommendationItem } from '@/types'
import MatchScoreBadge from '@/components/match/MatchScoreBadge.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'

withDefaults(defineProps<{
  item: RecommendationItem
  requested?: boolean
}>(), {
  requested: false,
})

defineEmits<{
  match: [userId: number]
  'view-profile': [userId: number]
}>()
</script>

<style scoped>
.recommendation-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 12px;
}

.rec-left {
  flex-shrink: 0;
}

.rec-body {
  flex: 1;
  min-width: 0;
}

.rec-user {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.rec-user-info {
  display: flex;
  flex-direction: column;
}

.rec-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.rec-school {
  font-size: 12px;
  color: #909399;
}

.rec-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
}

.rec-tag {
  margin: 0;
}

.rec-reason {
  margin: 8px 0 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  display: flex;
  align-items: flex-start;
  gap: 4px;
  background: #f5f7fa;
  padding: 8px 10px;
  border-radius: 8px;
}

.rec-actions {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
</style>
