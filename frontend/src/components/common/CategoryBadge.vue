<!-- Category badge — colored dot + label from CATEGORY_MAP -->
<template>
  <span class="category-badge" :class="`category-badge--${size}`" :style="{ color: cat.color }">
    <el-icon :size="iconSize"><component :is="cat.icon" /></el-icon>
    <span class="category-label">{{ cat.label }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CATEGORY_MAP } from '@/utils/constants'

const props = withDefaults(defineProps<{
  category: string
  size?: 'small' | 'default'
}>(), {
  size: 'default',
})

const cat = computed(() => CATEGORY_MAP[props.category] || CATEGORY_MAP.other)
const iconSize = computed(() => props.size === 'small' ? 14 : 16)
</script>

<style scoped>
.category-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
}

.category-badge--default {
  font-size: 14px;
}

.category-badge--small {
  font-size: 12px;
}
</style>
