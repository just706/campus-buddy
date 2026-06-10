<!-- Chat list page — list of chat sessions with last message preview and unread badges -->
<template>
  <div class="chat-list-page">
    <AppHeader title="消息" />

    <!-- Skeleton loading on first load -->
    <div v-if="isLoading && chatList.length === 0" class="chat-list-scroll">
      <SkeletonCard
        v-for="i in 6"
        :key="'sk-' + i"
        :lines="2"
        :inline="true"
      />
    </div>

    <!-- Chat list -->
    <div
      v-else
      class="chat-list-scroll"
      @scroll="handleScroll"
      ref="scrollRef"
    >
      <ChatListItem
        v-for="chat in chatList"
        :key="chat.id"
        :chat="chat"
        @click="goToChat(chat.id)"
      />

      <!-- Load more indicator -->
      <div v-if="isLoading && chatList.length > 0" class="load-more">
        <LoadingSpinner :size="24" />
      </div>

      <!-- End of list -->
      <div v-if="!hasMore && chatList.length > 0" class="list-end">
        没有更多了
      </div>

      <!-- Empty state -->
      <EmptyState
        v-if="!isLoading && chatList.length === 0"
        text="还没有聊天，去发现页找个搭子吧！"
        icon="ChatDotRound"
        actionText="去发现"
        @action="router.push('/posts')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound } from '@element-plus/icons-vue'
import AppHeader from '@/components/common/AppHeader.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import SkeletonCard from '@/components/common/SkeletonCard.vue'
import ChatListItem from '@/components/chat/ChatListItem.vue'
import { useChatsStore } from '@/stores/chats'
import { usePagination } from '@/composables/usePagination'

const router = useRouter()
const chatsStore = useChatsStore()
const scrollRef = ref<HTMLElement | null>(null)

const { page, pageSize, hasMore, reset, nextPage } = usePagination()

const chatList = computed(() => chatsStore.chatList)
const isLoading = computed(() => chatsStore.isLoading)

/** Initial load + refresh on page activation. */
async function loadChats() {
  reset()
  await chatsStore.fetchChatList(1, pageSize)
}

// Fetch on mount
loadChats()

// Re-fetch when tab is activated (come back from chat window)
onActivated(() => {
  chatsStore.fetchChatList(1, pageSize)
})

/** Infinite scroll — load more when near bottom. */
function handleScroll() {
  const el = scrollRef.value
  if (!el || !hasMore.value || isLoading.value) return
  const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 100
  if (nearBottom) {
    nextPage()
    chatsStore.fetchChatList(page.value, pageSize)
  }
}

/** Navigate to chat window. */
function goToChat(chatId: number) {
  router.push(`/chats/${chatId}`)
}
</script>

<style scoped>
.chat-list-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-page);
}

.chat-list-scroll {
  flex: 1;
  overflow-y: auto;
}

/* Divider between chat items */
.chat-list-scroll :deep(.chat-list-item) {
  border-bottom: 1px solid #f0f2f5;
}

.load-more {
  display: flex;
  justify-content: center;
  padding: 16px;
}

.list-end {
  text-align: center;
  padding: 16px;
  font-size: 12px;
  color: var(--text-placeholder);
}
</style>
