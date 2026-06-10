<!-- Post status badge — colored dot + status label -->
<template>
  <span class="post-status-badge" :style="{ color: config.color, borderColor: config.color }">
    {{ config.label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { POST_STATUS_MAP } from '@/utils/constants'

const props = defineProps<{
  status: string
}>()

const config = computed(() => POST_STATUS_MAP[props.status] || POST_STATUS_MAP.active)
</script>

<style scoped>
.post-status-badge {
  display: inline-block;
  padding: 2px 8px;
  font-size: 12px;
  border: 1px solid;
  border-radius: 4px;
  line-height: 1.4;
}
</style>
