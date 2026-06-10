<!-- Chat window header — back button, nickname, online status -->
<template>
  <header class="chat-header">
    <div class="header-left">
      <el-button
        :icon="ArrowLeft"
        text
        @click="goBack"
      />
      <UserAvatar
        :src="avatar"
        :name="nickname || '?'"
        :size="36"
      />
    </div>
    <div class="header-center" @click="$emit('titleClick')">
      <span class="header-nickname">{{ nickname || '未知用户' }}</span>
      <span class="header-status" :class="{ 'header-status--online': isOnline }">
        {{ isOnline ? '在线' : connectionText }}
      </span>
    </div>
    <div class="header-right">
      <slot name="right" />
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import UserAvatar from '@/components/common/UserAvatar.vue'
import type { WsConnectionState } from '@/composables/useWebSocket'

const props = defineProps<{
  nickname?: string | null
  avatar?: string | null
  isOnline?: boolean
  connectionState?: WsConnectionState
}>()

defineEmits<{
  titleClick: []
}>()

const router = useRouter()

function goBack() {
  router.back()
}

const connectionText = computed(() => {
  if (props.isOnline) return '在线'
  switch (props.connectionState) {
    case 'connecting':
      return '连接中...'
    case 'connected':
      return '在线'
    default:
      return '离线'
  }
})
</script>

<style scoped>
.chat-header {
  position: sticky;
  top: 0;
  z-index: 99;
  display: flex;
  align-items: center;
  height: 52px;
  padding: 0 8px;
  background: var(--bg-white);
  border-bottom: 1px solid var(--border-color);
  gap: 8px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 2px;
}

.header-center {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  cursor: pointer;
}

.header-nickname {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-status {
  font-size: 11px;
  color: var(--text-placeholder);
}

.header-status--online {
  color: var(--color-secondary);
}

.header-right {
  min-width: 40px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
</style>
