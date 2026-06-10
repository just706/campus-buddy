<!-- Create Post (发布邀约) — form page for creating a new buddy-finding post -->
<template>
  <div class="create-post-page">
    <AppHeader title="发布邀约" :show-back="true" />
    <PostForm
      :is-submitting="isSubmitting"
      @submit="handleCreate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePostsStore } from '@/stores/posts'
import type { PostCreate } from '@/types'
import AppHeader from '@/components/common/AppHeader.vue'
import PostForm from '@/components/post/PostForm.vue'

const router = useRouter()
const postsStore = usePostsStore()
const isSubmitting = ref(false)

async function handleCreate(data: PostCreate) {
  isSubmitting.value = true
  try {
    const post = await postsStore.createPost(data)
    ElMessage.success('邀约发布成功')
    router.replace(`/posts/${post.id}`)
  } catch (err: unknown) {
    const msg = (err as Error)?.message || '发布失败'
    // Check if it's an AI moderation block
    if (msg.includes('violates') || msg.includes('违规')) {
      await ElMessageBox.alert(msg, '内容审核未通过', { confirmButtonText: '修改', type: 'warning' })
    } else {
      ElMessage.error(msg)
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.create-post-page {
  min-height: 100vh;
  background: #fff;
}
</style>
