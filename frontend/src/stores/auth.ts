/**
 * Auth store — manages authentication state, login/register/logout,
 * token storage, and session persistence.
 *
 * Security: access_token is stored ONLY in Pinia memory (not localStorage).
 * refresh_token is persisted to localStorage for session recovery.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserResponse, LoginRequest, RegisterRequest } from '@/types'
import * as authApi from '@/api/auth'
import * as usersApi from '@/api/users'
import { setupAuthInterceptors } from '@/api/client'

const REFRESH_TOKEN_KEY = 'campus_buddy_refresh_token'

export const useAuthStore = defineStore('auth', () => {
  // ===== State =====
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(localStorage.getItem(REFRESH_TOKEN_KEY))
  const currentUser = ref<UserResponse | null>(null)
  const isInitialized = ref(false)

  // ===== Getters =====
  const isAuthenticated = computed(() => !!accessToken.value && !!currentUser.value)

  // ===== Actions =====

  /** Register a new account, then auto-login and fetch profile. */
  async function register(data: RegisterRequest) {
    const tokens = await authApi.register(data)
    setTokens(tokens.access_token, tokens.refresh_token)
    await fetchUser()
  }

  /** Login with email/username + password. */
  async function login(data: LoginRequest) {
    const tokens = await authApi.login(data)
    setTokens(tokens.access_token, tokens.refresh_token)
    await fetchUser()
  }

  /** Fetch the current user's profile from the server. */
  async function fetchUser() {
    const user = await usersApi.getMe()
    currentUser.value = user
  }

  /** Update the current user's profile. */
  async function updateProfile(data: Parameters<typeof usersApi.updateMe>[0]) {
    const user = await usersApi.updateMe(data)
    currentUser.value = user
  }

  /**
   * Refresh the access token using the stored refresh token.
   * Called by the Axios response interceptor on 401.
   * Returns the new access token.
   */
  async function refreshAccessToken(): Promise<string> {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }
    const tokens = await authApi.refreshToken({
      refresh_token: refreshToken.value,
    })
    setTokens(tokens.access_token, tokens.refresh_token)
    return tokens.access_token
  }

  /** Clear all auth state and redirect to login. */
  function logout() {
    accessToken.value = null
    refreshToken.value = null
    currentUser.value = null
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  }

  /**
   * Try to restore a session from the stored refresh token.
   * Called at app startup by the router guard.
   * Returns true if session was restored, false otherwise.
   */
  async function init(): Promise<boolean> {
    if (isInitialized.value) return isAuthenticated.value
    isInitialized.value = true

    const stored = localStorage.getItem(REFRESH_TOKEN_KEY)
    if (!stored) return false

    refreshToken.value = stored
    try {
      await refreshAccessToken()
      await fetchUser()
      return true
    } catch {
      logout()
      return false
    }
  }

  // ===== Internal Helpers =====

  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
  }

  // ===== Register Axios interceptors =====
  setupAuthInterceptors({
    getAccessToken: () => accessToken.value,
    getRefreshToken: () => refreshToken.value,
    onRefreshSuccess: (access: string, refresh: string) => {
      setTokens(access, refresh)
    },
    onAuthFailure: () => {
      logout()
      // Navigation will be handled by the router guard
      window.location.href = '/login'
    },
  })

  return {
    // State
    accessToken,
    refreshToken,
    currentUser,
    isInitialized,
    // Getters
    isAuthenticated,
    // Actions
    register,
    login,
    fetchUser,
    updateProfile,
    refreshAccessToken,
    logout,
    init,
  }
})
