/**
 * Infinite scroll composable — triggers loadMore when user scrolls
 * near the bottom of a container.
 */

import { ref, onMounted, onUnmounted, type Ref } from 'vue'

export function useInfiniteScroll(
  loadMore: () => Promise<void> | void,
  options: {
    threshold?: number // px from bottom to trigger (default 100)
    containerRef?: Ref<HTMLElement | null>
  } = {},
) {
  const isLoading = ref(false)
  const isFinished = ref(false)
  const { threshold = 100, containerRef } = options

  let ticking = false

  function getScrollContainer(): HTMLElement | Window {
    if (containerRef?.value) return containerRef.value
    return window
  }

  function onScroll() {
    if (ticking || isLoading.value || isFinished.value) return
    ticking = true
    requestAnimationFrame(() => {
      const container = getScrollContainer()
      let scrollTop: number
      let scrollHeight: number
      let clientHeight: number

      if (container === window) {
        scrollTop = window.scrollY
        scrollHeight = document.documentElement.scrollHeight
        clientHeight = window.innerHeight
      } else {
        const el = container as HTMLElement
        scrollTop = el.scrollTop
        scrollHeight = el.scrollHeight
        clientHeight = el.clientHeight
      }

      if (scrollHeight - scrollTop - clientHeight < threshold) {
        isLoading.value = true
        Promise.resolve(loadMore()).finally(() => {
          isLoading.value = false
        })
      }
      ticking = false
    })
  }

  onMounted(() => {
    const container = getScrollContainer()
    container.addEventListener('scroll', onScroll, { passive: true })
  })

  onUnmounted(() => {
    const container = getScrollContainer()
    container.removeEventListener('scroll', onScroll)
  })

  function finish() {
    isFinished.value = true
  }

  function reset() {
    isFinished.value = false
    isLoading.value = false
  }

  return { isLoading, isFinished, finish, reset }
}
