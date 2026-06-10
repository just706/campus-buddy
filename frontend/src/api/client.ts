/**
 * Axios client instance with request/response interceptors.
 *
 * Uses a token-getter pattern to avoid circular imports:
 * the auth store registers its token getter + refresh function at setup time,
 * so this module never imports from stores directly.
 */

import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

// ===== Token provider (set by auth store at initialization) =====
let _getAccessToken: (() => string | null) | null = null
let _getRefreshToken: (() => string | null) | null = null
let _onRefreshSuccess: ((accessToken: string, refreshToken: string) => void) | null = null
let _onAuthFailure: (() => void) | null = null

export function setupAuthInterceptors(options: {
  getAccessToken: () => string | null
  getRefreshToken: () => string | null
  onRefreshSuccess: (accessToken: string, refreshToken: string) => void
  onAuthFailure: () => void
}) {
  _getAccessToken = options.getAccessToken
  _getRefreshToken = options.getRefreshToken
  _onRefreshSuccess = options.onRefreshSuccess
  _onAuthFailure = options.onAuthFailure
}

// ===== Axios Instance =====
const http = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// ===== Request Interceptor =====
http.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = _getAccessToken?.()
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// ===== Token refresh queue =====
let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: unknown) => void
}> = []

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else if (token) resolve(token)
  })
  failedQueue = []
}

// ===== Response Interceptor =====
http.interceptors.response.use(
  (response) => {
    // Extract data from APIResponse { code, message, data }
    const body = response.data
    if (body && typeof body === 'object' && 'code' in body && 'data' in body) {
      if (body.code >= 400) {
        ElMessage.error(body.message || 'Request failed')
        return Promise.reject(new Error(body.message || 'Request failed'))
      }
      return body.data
    }
    return response.data
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }

    // 401 → try token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = _getRefreshToken?.()
      if (!refreshToken) {
        _onAuthFailure?.()
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token: string) => {
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${token}`
              }
              resolve(http(originalRequest))
            },
            reject,
          })
        })
      }

      isRefreshing = true
      originalRequest._retry = true

      try {
        // Call refresh endpoint directly (bypass interceptors to avoid loops)
        const res = await axios.post('/api/v1/auth/refresh', {
          refresh_token: refreshToken,
        })
        const body = res.data
        if (body?.code === 200 && body?.data) {
          const { access_token, refresh_token } = body.data
          _onRefreshSuccess?.(access_token, refresh_token)
          processQueue(null, access_token)
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`
          }
          return http(originalRequest)
        }
        throw new Error('Token refresh failed')
      } catch (refreshError) {
        processQueue(refreshError, null)
        _onAuthFailure?.()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // Other errors
    const msg =
      (error.response?.data as { message?: string })?.message ||
      error.message ||
      'Network error'
    if (error.response?.status !== 401) {
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  },
)

export default http
