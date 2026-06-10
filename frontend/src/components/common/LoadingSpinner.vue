<!-- Full-screen loading spinner -->
<template>
  <div class="loading-spinner" :class="{ 'loading-spinner--inline': inline }">
    <el-icon class="spinner-icon" :size="size">
      <Loading />
    </el-icon>
    <p v-if="text" class="spinner-text">{{ text }}</p>
  </div>
</template>

<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue'

withDefaults(defineProps<{
  text?: string
  size?: number
  inline?: boolean
}>(), {
  size: 32,
  inline: false,
})
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 0;
  color: #909399;
}

.loading-spinner--inline {
  padding: 16px 0;
}

.spinner-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spinner-text {
  margin-top: 12px;
  font-size: 14px;
  color: #909399;
}
</style>
