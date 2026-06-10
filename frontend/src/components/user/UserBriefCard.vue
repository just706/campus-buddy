<!-- User brief card — avatar, name, school info, bio, tags -->
<template>
  <div class="user-brief-card" @click="$emit('click')">
    <div class="ubc-main">
      <UserAvatar :src="user.avatar" :name="user.nickname || user.username" :size="48" />
      <div class="ubc-info">
        <span class="ubc-name">{{ user.nickname || user.username }}</span>
        <span class="ubc-school">{{ user.university }}<span v-if="user.major"> · {{ user.major }}</span></span>
        <span v-if="user.grade" class="ubc-grade">{{ user.grade }}</span>
      </div>
    </div>
    <p v-if="user.bio" class="ubc-bio">{{ user.bio }}</p>
    <div class="ubc-tags" v-if="user.tags && user.tags.length">
      <el-tag v-for="tag in user.tags" :key="tag" size="small" class="ubc-tag">#{{ tag }}</el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { UserResponse } from '@/types'
import UserAvatar from '@/components/common/UserAvatar.vue'

defineProps<{
  user: UserResponse
}>()

defineEmits<{
  click: []
}>()
</script>

<style scoped>
.user-brief-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.user-brief-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.ubc-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ubc-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ubc-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.ubc-school {
  font-size: 13px;
  color: #606266;
}

.ubc-grade {
  font-size: 12px;
  color: #909399;
}

.ubc-bio {
  margin: 10px 0 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.ubc-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.ubc-tag {
  margin: 0;
}
</style>
