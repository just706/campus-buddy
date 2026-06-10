<!-- User avatar with fallback to initial letter -->
<template>
  <el-avatar
    :size="size"
    :src="src || undefined"
    :style="{ backgroundColor: bgColor }"
  >
    {{ initial }}
  </el-avatar>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  src?: string | null
  name?: string | null
  size?: number | 'small' | 'default' | 'large'
}>(), {
  size: 'default',
})

const initial = computed(() => {
  const n = props.name || '?'
  return n.charAt(0).toUpperCase()
})

const bgColor = computed(() => {
  if (props.src) return undefined
  // Generate a consistent color from the name
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
  const idx = (props.name || '?').charCodeAt(0) % colors.length
  return colors[idx]
})
</script>
