/** Common type definitions shared across the entire frontend. */

/** Uniform API response wrapper — matches backend APIResponse schema. */
export interface APIResponse<T = unknown> {
  code: number
  message: string
  data: T | null
}

/** Paginated response data — matches backend PaginatedData schema. */
export interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
