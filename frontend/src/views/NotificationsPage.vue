<!-- Notifications (通知列表) — notification list with read/unread filter and batch actions -->
<template>
  <div class="notifications-page">
    <AppHeader title="通知">
      <template #right>
        <el-button
          v-if="unreadCount > 0"
          type="primary"
          text
          size="small"
          :loading="markingAll"
          @click="handleMarkAllRead"
        >
          全部已读
        </el-button>
      </template>
    </AppHeader>

    <!-- Filter Tabs -->
    <div class="filter-tabs">
      <div
        v-for="tab in filterTabs"
        :key="tab.value"
        class="filter-tab"
        :class="{ 'filter-tab--active': (tab.value === 'unread') === unreadOnly }"
        @click="switchFilter(tab.value)"
      >
        {{ tab.label }}
      </div>
    </div>

    <!-- Notification List -->
    <LoadingSpinner v-if="loading" text="加载中..." />

    <EmptyState
      v-else-if="!loading && notifications.length === 0"
      text="还没有通知"
    />

    <div v-else class="notif-list">
      <NotificationItem
        v-for="item in notifications"
        :key="item.id"
        :notification="item"
        @click="handleClick(item)"
      />
    </div>

    <LoadingSpinner v-if="loading && notifications.length > 0" :inline="true" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useNotificationsStore } from '@/stores/notifications'
import type { NotificationResponse } from '@/types'
import AppHeader from '@/components/common/AppHeader.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import NotificationItem from '@/components/notification/NotificationItem.vue'

const router = useRouter()
const notifStore = useNotificationsStore()

const loading = ref(true)
const markingAll = ref(false)
const unreadOnly = ref(false)

const filterTabs = [
  { value: 'all', label: '全部' },
  { value: 'unread', label: '未读' },
]

const notifications = ref(notifStore.notifications)
const unreadCount = ref(notifStore.unreadCount)

onMounted(async () => {
  await loadNotifications()
})

async function loadNotifications() {
  loading.value = true
  try {
    await notifStore.fetchNotifications(1, 20, unreadOnly.value)
    notifications.value = notifStore.notifications
    unreadCount.value = notifStore.unreadCount
  } finally {
    loading.value = false
  }
}

function switchFilter(val: string) {
  unreadOnly.value = val === 'unread'
  loadNotifications()
}

async function handleClick(notification: NotificationResponse) {
  // Mark as read
  if (!notification.is_read) {
    try {
      await notifStore.markRead(notification.id)
    } catch {
      // ignore
    }
  }

  // Navigate based on type
  if (notification.type === 'match') {
    router.push('/matches')
  } else if (notification.type === 'message') {
    router.push('/chats')
  } else {
    // system notification — stay on page
  }
}

async function handleMarkAllRead() {
  markingAll.value = true
  try {
    await notifStore.markAllRead()
    ElMessage.success('全部已读')
    notifications.value = notifStore.notifications
    unreadCount.value = 0
  } catch {
    ElMessage.error('操作失败')
  } finally {
    markingAll.value = false
  }
}
</script>

<style scoped>
.notifications-page {
  min-height: 100vh;
  padding-bottom: 56px;
}

.filter-tabs {
  display: flex;
  padding: 0 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  gap: 24px;
}

.filter-tab {
  padding: 10px 0;
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

.notif-list {
  background: #fff;
}
</style>
