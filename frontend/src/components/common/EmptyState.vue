<!-- Empty state placeholder with icon, text, and optional action -->
<template>
  <div class="empty-state">
    <el-icon class="empty-icon" :size="64">
      <component :is="icon" />
    </el-icon>
    <p class="empty-text">{{ text }}</p>
    <el-button v-if="actionText" type="primary" @click="$emit('action')">
      {{ actionText }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { Document } from '@element-plus/icons-vue'

withDefaults(defineProps<{
  text?: string
  icon?: any
  actionText?: string
}>(), {
  text: '暂无数据',
  icon: () => Document,
  actionText: '',
})

defineEmits<{
  action: []
}>()
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 24px;
  color: #c0c4cc;
}

.empty-text {
  margin: 16px 0 24px;
  font-size: 14px;
  color: #909399;
  text-align: center;
  line-height: 1.6;
}
</style>
