<!-- Chat list item — avatar, nickname, last message preview, time, unread badge -->
<template>
  <div class="chat-list-item" @click="$emit('click')">
    <UserAvatar
      :src="chat.other_user_avatar"
      :name="chat.other_user_nickname || '?'"
      :size="48"
    />
    <div class="chat-info">
      <div class="chat-top">
        <span class="chat-name">{{ chat.other_user_nickname || '未知用户' }}</span>
        <span class="chat-time">{{ timeText }}</span>
      </div>
      <div class="chat-bottom">
        <span class="chat-preview">{{ previewText }}</span>
        <el-badge
          v-if="chat.unread_count > 0"
          :value="chat.unread_count"
          :max="99"
          class="chat-badge"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ChatBriefResponse } from '@/types'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { relativeTime, truncate } from '@/utils/format'

const props = defineProps<{
  chat: ChatBriefResponse
}>()

defineEmits<{
  click: []
}>()

const timeText = computed(() => relativeTime(props.chat.last_message_at))

const previewText = computed(() => {
  if (!props.chat.last_message) return '暂无消息'
  return truncate(props.chat.last_message, 30)
})
</script>

<style scoped>
.chat-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--bg-white);
  cursor: pointer;
  transition: background 0.15s;
}

.chat-list-item:active {
  background: #f0f2f5;
}

.chat-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chat-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.chat-time {
  font-size: 12px;
  color: var(--text-placeholder);
  flex-shrink: 0;
  margin-left: 8px;
}

.chat-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.chat-preview {
  font-size: 13px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.chat-badge {
  flex-shrink: 0;
}
</style>
