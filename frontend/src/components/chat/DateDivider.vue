<!-- Date divider between message groups in chat -->
<template>
  <div class="date-divider">
    <span class="date-text">{{ formatted }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatDateDivider } from '@/utils/format'

const props = defineProps<{
  date: string
}>()

const formatted = computed(() => formatDateDivider(props.date))
</script>

<style scoped>
.date-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px 0 8px;
}

.date-text {
  font-size: 12px;
  color: var(--text-placeholder);
  background: var(--bg-page);
  padding: 2px 12px;
  border-radius: 4px;
}
</style>
