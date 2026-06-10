<!-- Post Square (邀约广场) — main discovery page with search, category filter, infinite scroll -->
<template>
  <div class="post-square-page">
    <!-- Search Bar -->
    <div class="search-bar">
      <el-input
        v-model="searchInput"
        placeholder="搜索邀约标题或描述..."
        :prefix-icon="Search"
        clearable
        size="large"
        @clear="handleSearchClear"
        class="search-input"
      />
    </div>

    <!-- Category Tabs -->
    <div class="category-tabs">
      <div
        v-for="cat in allCategoryTab"
        :key="cat.value"
        class="category-tab"
        :class="{ 'category-tab--active': activeCategory === cat.value }"
        :style="activeCategory === cat.value ? { color: cat.color, borderColor: cat.color } : {}"
        @click="switchCategory(cat.value)"
      >
        {{ cat.label }}
      </div>
    </div>

    <!-- Post List -->
    <div class="post-list" ref="listRef">
      <!-- Skeleton loading on first load -->
      <template v-if="isLoading && posts.length === 0">
        <SkeletonCard
          v-for="i in 6"
          :key="'sk-' + i"
          :lines="3"
          :show-avatar="false"
        />
      </template>

      <EmptyState
        v-else-if="!isLoading && posts.length === 0"
        text="还没有邀约，快来发布第一个吧！"
        :icon="Document"
        action-text="发布邀约"
        @action="router.push('/posts/new')"
      />

      <template v-else>
        <div class="post-grid">
          <PostCard
            v-for="post in posts"
            :key="post.id"
            :post="post"
            @click="router.push(`/posts/${$event}`)"
            @tag-click="handleTagClick"
            @user-click="router.push(`/users/${$event}`)"
          />
        </div>
        <LoadingSpinner v-if="isLoading && posts.length > 0" text="加载更多..." :inline="true" />
        <p v-if="isFinished && posts.length > 0" class="list-end">— 没有更多了 —</p>
      </template>
    </div>

    <!-- FAB — Create Post -->
    <el-button
      type="primary"
      :icon="Plus"
      circle
      size="large"
      class="fab-btn"
      @click="router.push('/posts/new')"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Plus, Document } from '@element-plus/icons-vue'
import { usePostsStore } from '@/stores/posts'
import { CATEGORIES } from '@/utils/constants'
import { debounce } from '@/composables/useDebounce'
import PostCard from '@/components/post/PostCard.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import SkeletonCard from '@/components/common/SkeletonCard.vue'

const router = useRouter()
const postsStore = usePostsStore()

const searchInput = ref('')
const activeCategory = ref<string | undefined>(undefined)
const isLoading = ref(false)
const isFinished = ref(false)
const listRef = ref<HTMLElement | null>(null)

const allCategoryTab = computed(() => [
  { value: undefined, label: '全部', color: '#303133' },
  ...CATEGORIES.map(c => ({ value: c.value, label: c.label, color: c.color })),
])

const posts = computed(() => postsStore.posts)

const debouncedSearch = debounce((val: string) => {
  postsStore.setFilters({ keyword: val || undefined })
  loadPosts()
}, 500)

watch(searchInput, (val) => {
  debouncedSearch(val)
})

function switchCategory(cat: string | undefined) {
  activeCategory.value = cat
  postsStore.setFilters({ category: cat })
  loadPosts()
}

function handleSearchClear() {
  searchInput.value = ''
}

function handleTagClick(tag: string) {
  postsStore.setFilters({ tag })
  loadPosts()
}

async function loadPosts() {
  isLoading.value = true
  try {
    postsStore.page = 1
    await postsStore.fetchPosts()
    isFinished.value = postsStore.posts.length >= postsStore.total
  } finally {
    isLoading.value = false
  }
}

async function loadMore() {
  if (isLoading.value || isFinished.value) return
  postsStore.page++
  isLoading.value = true
  try {
    await postsStore.fetchPosts()
    if (postsStore.posts.length >= postsStore.total) {
      isFinished.value = true
    }
  } finally {
    isLoading.value = false
  }
}

// Infinite scroll
function onScroll() {
  const scrollTop = window.scrollY
  const scrollHeight = document.documentElement.scrollHeight
  const clientHeight = window.innerHeight
  if (scrollHeight - scrollTop - clientHeight < 200) {
    loadMore()
  }
}

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  if (posts.value.length === 0) {
    loadPosts()
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<style scoped>
.post-square-page {
  min-height: 100vh;
  padding-bottom: 56px;
}

.search-bar {
  padding: 12px 16px;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}

.search-input {
  --el-input-border-radius: 20px;
}

.category-tabs {
  display: flex;
  gap: 0;
  padding: 8px 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  overflow-x: auto;
}

.category-tab {
  flex-shrink: 0;
  padding: 6px 16px;
  font-size: 14px;
  color: #909399;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.category-tab--active {
  font-weight: 600;
  border-bottom-width: 2px;
}

.post-list {
  padding: 12px 16px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Responsive grid per PRD §7.5 */
.post-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

@media (min-width: 768px) {
  .post-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .post-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.list-end {
  text-align: center;
  color: #c0c4cc;
  font-size: 13px;
  padding: 16px 0;
  grid-column: 1 / -1;
}

.fab-btn {
  position: fixed;
  bottom: 72px;
  right: 20px;
  z-index: 50;
  width: 52px;
  height: 52px;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.4);
}
</style>
