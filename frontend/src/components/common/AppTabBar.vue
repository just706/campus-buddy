<!-- Bottom Tab Bar — 5 tabs: Discover, Recommend, Messages, Notifications, Me -->
<template>
  <nav class="app-tab-bar">
    <router-link
      v-for="tab in tabs"
      :key="tab.route"
      :to="tab.route"
      class="tab-item"
      active-class="tab-item--active"
    >
      <el-badge :value="tab.badge" :hidden="!tab.badge" :max="99">
        <el-icon :size="22">
          <component :is="tab.icon" />
        </el-icon>
      </el-badge>
      <span class="tab-label">{{ tab.label }}</span>
    </router-link>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Search,
  Guide,
  ChatDotRound,
  Bell,
  User,
} from '@element-plus/icons-vue'
import { useChatsStore } from '@/stores/chats'
import { useNotificationsStore } from '@/stores/notifications'

const chatsStore = useChatsStore()
const notifStore = useNotificationsStore()

const tabs = computed(() => [
  {
    route: '/posts',
    label: '发现',
    icon: Search,
    badge: 0,
  },
  {
    route: '/recommendations',
    label: '推荐',
    icon: Guide,
    badge: 0,
  },
  {
    route: '/chats',
    label: '消息',
    icon: ChatDotRound,
    badge: chatsStore.unreadTotal || 0,
  },
  {
    route: '/notifications',
    label: '通知',
    icon: Bell,
    badge: notifStore.unreadCount || 0,
  },
  {
    route: '/profile',
    label: '我的',
    icon: User,
    badge: 0,
  },
])
</script>

<style scoped>
.app-tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: #fff;
  border-top: 1px solid #e4e7ed;
  z-index: 100;
  padding-bottom: env(safe-area-inset-bottom);
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  text-decoration: none;
  color: #909399;
  flex: 1;
  height: 100%;
  transition: color 0.2s;
}

.tab-item--active {
  color: #409eff;
}

.tab-label {
  font-size: 11px;
  line-height: 1;
}
</style>
