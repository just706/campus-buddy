<!-- Root App component — router view + conditional TabBar -->
<template>
  <div class="app-container">
    <router-view v-slot="{ Component, route }">
      <transition name="page-fade" mode="out-in">
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
/* Page transition animations */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease;
}
.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}
</style>
