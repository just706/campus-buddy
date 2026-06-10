/**
 * Posts (邀约) store — post list, filtering, CRUD operations.
 * Placeholder: full implementation in Stage 2.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PostResponse, PostListResponse } from '@/types'
import * as postsApi from '@/api/posts'

export const usePostsStore = defineStore('posts', () => {
  // ===== State =====
  const posts = ref<PostResponse[]>([])
  const currentPost = ref<PostResponse | null>(null)
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const isLoading = ref(false)

  // ===== Filters =====
  const currentCategory = ref<string | undefined>(undefined)
  const currentTag = ref<string | undefined>(undefined)
  const currentKeyword = ref<string | undefined>(undefined)

  // ===== Actions =====

  async function fetchPosts() {
    isLoading.value = true
    try {
      const result: PostListResponse = await postsApi.listPosts({
        category: currentCategory.value,
        tag: currentTag.value,
        keyword: currentKeyword.value,
        page: page.value,
        page_size: pageSize.value,
      })
      posts.value = result.items
      total.value = result.total
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPostById(id: number) {
    currentPost.value = await postsApi.getPost(id)
    return currentPost.value
  }

  async function createPost(data: Parameters<typeof postsApi.createPost>[0]) {
    const post = await postsApi.createPost(data)
    return post
  }

  async function updatePost(id: number, data: Parameters<typeof postsApi.updatePost>[1]) {
    const post = await postsApi.updatePost(id, data)
    if (currentPost.value?.id === id) currentPost.value = post
    return post
  }

  async function closePost(id: number) {
    await postsApi.closePost(id)
    if (currentPost.value?.id === id) {
      currentPost.value.status = 'closed'
    }
  }

  function setFilters(filters: { category?: string; tag?: string; keyword?: string }) {
    if (filters.category !== undefined) currentCategory.value = filters.category
    if (filters.tag !== undefined) currentTag.value = filters.tag
    if (filters.keyword !== undefined) currentKeyword.value = filters.keyword
    page.value = 1
  }

  function reset() {
    posts.value = []
    currentPost.value = null
    total.value = 0
    page.value = 1
  }

  return {
    posts,
    currentPost,
    total,
    page,
    pageSize,
    isLoading,
    currentCategory,
    currentTag,
    currentKeyword,
    fetchPosts,
    fetchPostById,
    createPost,
    updatePost,
    closePost,
    setFilters,
    reset,
  }
})
