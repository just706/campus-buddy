<!-- Persistent network offline banner — shows at top of page when disconnected -->
<template>
  <Transition name="banner-slide">
    <div v-if="!isOnline" class="network-banner">
      <el-icon :size="16"><WarningFilled /></el-icon>
      <span>网络连接已断开，部分功能不可用</span>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { WarningFilled } from '@element-plus/icons-vue'
import { useUiStore } from '@/stores/ui'
import { storeToRefs } from 'pinia'

const uiStore = useUiStore()
const { isOnline } = storeToRefs(uiStore)
</script>

<style scoped>
.network-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  background: #fef0f0;
  color: var(--color-danger);
  font-size: 13px;
  border-bottom: 1px solid #fde2e2;
}

.banner-slide-enter-active,
.banner-slide-leave-active {
  transition: all 0.3s ease;
}

.banner-slide-enter-from,
.banner-slide-leave-to {
  opacity: 0;
  transform: translateY(-100%);
}
</style>
