<!-- Root App component — router view + conditional TabBar + NetworkBanner -->
<template>
  <div class="app-container">
    <NetworkBanner />
    <router-view v-slot="{ Component, route }">
      <transition :name="(route.meta.transition as string | undefined) || 'page-fade'" mode="out-in">
        <component :is="Component" :key="route.path" />
      </transition>
    </router-view>
    <AppTabBar v-if="showTabBar" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppTabBar from '@/components/common/AppTabBar.vue'
import NetworkBanner from '@/components/common/NetworkBanner.vue'

const route = useRoute()

const showTabBar = computed(() => {
  return typeof route.meta.tab === 'number'
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: #f5f7fa;
}

/* Pages with TabBar need bottom padding to avoid being covered */
.app-container:has(.app-tab-bar) {
  padding-bottom: 56px;
}
</style>

<style>
/* ===== Page Transition Animations ===== */

/* Fade — default for most pages */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease;
}
.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}

/* Slide left — for navigating deeper (e.g., post list → detail) */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.25s ease;
}
.slide-left-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* Slide right — for navigating back (e.g., detail → list) */
/* Currently same timing, reverse direction */
</style>
