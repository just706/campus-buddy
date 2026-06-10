/**
 * Pagination composable — manages page state for list views.
 */

import { ref, computed } from 'vue'

export function usePagination(defaultPageSize = 20) {
  const page = ref(1)
  const pageSize = ref(defaultPageSize)
  const total = ref(0)

  const hasMore = computed(() => page.value * pageSize.value < total.value)
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  function nextPage() {
    if (hasMore.value) page.value++
  }

  function reset() {
    page.value = 1
    total.value = 0
  }

  return {
    page,
    pageSize,
    total,
    hasMore,
    totalPages,
    nextPage,
    reset,
  }
}
