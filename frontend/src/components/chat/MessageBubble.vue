<!-- Chat message bubble — right blue (mine) / left gray (other), with time & sender avatar -->
<template>
  <div class="message-row" :class="{ 'message-row--mine': isMine }">
    <!-- Other user's avatar -->
    <div class="message-avatar" v-if="!isMine">
      <UserAvatar
        :src="senderAvatar"
        :name="senderName"
        :size="32"
      />
    </div>

    <div class="message-body">
      <!-- Sender name for group chats (other side only) -->
      <div class="message-sender" v-if="!isMine && showSender">
        {{ senderName }}
      </div>

      <div class="message-bubble" :class="{
        'message-bubble--mine': isMine,
        'message-bubble--other': !isMine,
        'message-bubble--failed': message._failed,
      }">
        <span class="message-text">{{ message.content }}</span>
      </div>

      <!-- Send failed indicator -->
      <div class="message-error" v-if="message._failed && isMine">
        <el-icon :size="14" color="#F56C6C"><WarningFilled /></el-icon>
        <span class="error-text">发送失败</span>
        <el-button text size="small" type="danger" @click="$emit('retry', message)">
          重发
        </el-button>
      </div>

      <!-- Time -->
      <div class="message-time" v-if="showTime" :class="{ 'message-time--mine': isMine }">
        {{ formattedTime }}
      </div>
    </div>

    <!-- Own avatar (optional, hidden on mobile for space) -->
    <div class="message-avatar message-avatar--mine" v-if="isMine">
      <UserAvatar
        :src="senderAvatar"
        :name="senderName"
        :size="32"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { WarningFilled } from '@element-plus/icons-vue'
import type { MessageResponse } from '@/types'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { formatMessageTime } from '@/utils/format'

const props = defineProps<{
  message: MessageResponse & { _failed?: boolean }
  isMine: boolean
  showTime?: boolean
  showSender?: boolean
  senderName?: string
  senderAvatar?: string | null
}>()

defineEmits<{
  retry: [message: MessageResponse & { _failed?: boolean }]
}>()

const formattedTime = computed(() => formatMessageTime(props.message.created_at))
</script>

<style scoped>
.message-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 4px 16px;
}

.message-row--mine {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
  margin-top: 4px;
}

.message-avatar--mine {
  /* Hide own avatar on narrow screens */
  display: none;
}

@media (min-width: 480px) {
  .message-avatar--mine {
    display: block;
  }
}

.message-body {
  max-width: 72%;
  display: flex;
  flex-direction: column;
}

.message-row--mine .message-body {
  align-items: flex-end;
}

.message-sender {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 2px;
  padding: 0 4px;
}

.message-bubble {
  padding: 10px 14px;
  border-radius: var(--border-radius-xl);
  font-size: 15px;
  line-height: 1.5;
  word-break: break-word;
  position: relative;
}

.message-bubble--other {
  background: #fff;
  color: var(--text-primary);
  border-top-left-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.message-bubble--mine {
  background: var(--color-primary);
  color: #fff;
  border-top-right-radius: 4px;
}

.message-bubble--failed {
  opacity: 0.7;
  border: 1px solid var(--color-danger);
}

.message-text {
  white-space: pre-wrap;
}

.message-time {
  font-size: 11px;
  color: var(--text-placeholder);
  margin-top: 2px;
  padding: 0 4px;
}

.message-time--mine {
  text-align: right;
}

.message-error {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 2px;
}

.error-text {
  font-size: 11px;
  color: var(--color-danger);
}
</style>
