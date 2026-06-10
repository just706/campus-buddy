<!-- Notification list item — type icon, title, content, time, unread indicator -->
<template>
  <div
    class="notification-item"
    :class="{ 'notification-item--unread': !notification.is_read }"
    @click="$emit('click', notification)"
  >
    <div class="notif-icon" :style="{ background: iconColor + '15' }">
      <el-icon :size="20" :color="iconColor">
        <component :is="iconComponent" />
      </el-icon>
    </div>
    <div class="notif-body">
      <div class="notif-header">
        <span class="notif-title">{{ notification.title }}</span>
        <span v-if="!notification.is_read" class="unread-dot" />
      </div>
      <p class="notif-content">{{ notification.content }}</p>
      <span class="notif-time">{{ relativeTime(notification.created_at) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Connection, ChatDotRound, Notification } from '@element-plus/icons-vue'
import type { NotificationResponse } from '@/types'
import { relativeTime } from '@/utils/format'

const props = defineProps<{
  notification: NotificationResponse
}>()

defineEmits<{
  click: [notification: NotificationResponse]
}>()

const iconComponent = computed(() => {
  switch (props.notification.type) {
    case 'match': return Connection
    case 'message': return ChatDotRound
    default: return Notification
  }
})

const iconColor = computed(() => {
  switch (props.notification.type) {
    case 'match': return '#409EFF'
    case 'message': return '#67C23A'
    default: return '#909399'
  }
})
</script>

<style scoped>
.notification-item {
  display: flex;
  gap: 12px;
  padding: 14px 16px;
  background: #fff;
  cursor: pointer;
  transition: background 0.15s;
}

.notification-item--unread {
  background: #f0f7ff;
}

.notification-item:active {
  background: #f5f7fa;
}

.notif-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notif-body {
  flex: 1;
  min-width: 0;
}

.notif-header {
  display: flex;
  align-items: center;
  gap: 6px;
}

.notif-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409EFF;
  flex-shrink: 0;
}

.notif-content {
  margin: 4px 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notif-time {
  font-size: 11px;
  color: #c0c4cc;
}
</style>
