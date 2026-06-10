<!-- Page-level error state with retry button -->
<template>
  <div class="page-error">
    <el-icon class="error-icon" :size="56">
      <WarningFilled />
    </el-icon>
    <h3 class="error-title">{{ title }}</h3>
    <p class="error-desc">{{ description }}</p>
    <el-button v-if="retryable" type="primary" @click="$emit('retry')">
      重新加载
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { WarningFilled } from '@element-plus/icons-vue'

withDefaults(defineProps<{
  title?: string
  description?: string
  retryable?: boolean
}>(), {
  title: '加载失败',
  description: '请检查网络连接后重试',
  retryable: true,
})

defineEmits<{
  retry: []
}>()
</script>

<style scoped>
.page-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  padding: 48px 24px;
  text-align: center;
}

.error-icon {
  color: var(--color-warning);
  margin-bottom: 16px;
}

.error-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.error-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 24px;
  max-width: 280px;
  line-height: 1.5;
}
</style>
