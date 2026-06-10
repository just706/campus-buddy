<!-- Edit Post (编辑邀约) — form pre-filled with existing post data -->
<template>
  <div class="edit-post-page">
    <AppHeader title="编辑邀约" :show-back="true" />

    <LoadingSpinner v-if="loading" text="加载中..." />

    <template v-else-if="post && isMyPost">
      <PostForm
        :initial-data="initialData"
        :is-submitting="isSubmitting"
        submit-label="保存修改"
        @submit="handleUpdate"
      />
    </template>

    <EmptyState
      v-else-if="!loading && !post"
      text="邀约不存在"
      action-text="返回"
      @action="router.push('/posts')"
    />

    <EmptyState
      v-else-if="!loading && !isMyPost"
      text="无权编辑此邀约"
      action-text="返回"
      @action="router.push('/posts')"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { usePostsStore } from '@/stores/posts'
import { useAuthStore } from '@/stores/auth'
import type { PostCreate, PostUpdate } from '@/types'
import AppHeader from '@/components/common/AppHeader.vue'
import PostForm from '@/components/post/PostForm.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const postsStore = usePostsStore()
const authStore = useAuthStore()

const loading = ref(true)
const isSubmitting = ref(false)

const post = computed(() => postsStore.currentPost)
const isMyPost = computed(() => post.value?.user_id === authStore.currentUser?.id)

const initialData = computed(() => {
  if (!post.value) return {}
  return {
    category: post.value.category,
    title: post.value.title,
    description: post.value.description,
    target_count: post.value.target_count,
    tags: post.value.tags || [],
    location: post.value.location || '',
    time_range: post.value.time_range || '',
    expires_at: post.value.expires_at || undefined,
  }
})

onMounted(async () => {
  const id = Number(route.params.id)
  try {
    await postsStore.fetchPostById(id)
  } catch {
    // handled in template
  } finally {
    loading.value = false
  }
})

async function handleUpdate(data: PostCreate) {
  if (!post.value) return
  isSubmitting.value = true
  const updateData: PostUpdate = { ...data }
  try {
    await postsStore.updatePost(post.value.id, updateData)
    ElMessage.success('修改已保存')
    router.replace(`/posts/${post.value.id}`)
  } catch (err: unknown) {
    ElMessage.error((err as Error)?.message || '保存失败')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.edit-post-page {
  min-height: 100vh;
  background: #fff;
}
</style>
