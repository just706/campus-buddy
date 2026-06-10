/**
 * UI store — global UI state: network status, loading, page-level errors.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  // ===== Network Status =====
  const isOnline = ref(navigator.onLine)

  /** Set up online/offline event listeners. Call once at app init. */
  function initNetworkDetection() {
    window.addEventListener('online', () => {
      isOnline.value = true
    })
    window.addEventListener('offline', () => {
      isOnline.value = false
    })
  }

  // ===== Global Loading =====
  const globalLoading = ref(false)

  function showLoading() {
    globalLoading.value = true
  }

  function hideLoading() {
    globalLoading.value = false
  }

  return {
    isOnline,
    initNetworkDetection,
    globalLoading,
    showLoading,
    hideLoading,
  }
})
