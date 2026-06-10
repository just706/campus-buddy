<!-- Match status badge — colored label -->
<template>
  <span class="match-status-badge" :style="{ background: config.color + '18', color: config.color }">
    {{ config.label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { MATCH_STATUS_MAP } from '@/utils/constants'

const props = defineProps<{
  status: string
}>()

const config = computed(() => MATCH_STATUS_MAP[props.status] || MATCH_STATUS_MAP.pending)
</script>

<style scoped>
.match-status-badge {
  display: inline-block;
  padding: 3px 10px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 12px;
  line-height: 1.4;
}
</style>
