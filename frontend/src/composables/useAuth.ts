/**
 * Auth composable — convenience wrapper around auth store for components.
 */

import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useAuth() {
  const authStore = useAuthStore()

  return {
    user: computed(() => authStore.currentUser),
    isAuthenticated: computed(() => authStore.isAuthenticated),
    isInitialized: computed(() => authStore.isInitialized),
    login: authStore.login,
    register: authStore.register,
    logout: authStore.logout,
    updateProfile: authStore.updateProfile,
    fetchUser: authStore.fetchUser,
  }
}
