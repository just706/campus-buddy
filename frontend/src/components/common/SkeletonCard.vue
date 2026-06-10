<!-- Generic skeleton card used as loading placeholder for list items -->
<template>
  <div class="skeleton-card" :class="{ 'skeleton-card--inline': inline }">
    <!-- Avatar placeholder -->
    <el-skeleton animated v-if="showAvatar">
      <template #template>
        <el-skeleton-item variant="circle" :style="avatarStyle" />
      </template>
    </el-skeleton>

    <div class="skeleton-body">
      <!-- Title line -->
      <el-skeleton animated>
        <template #template>
          <el-skeleton-item variant="text" style="width: 60%; height: 18px" />
        </template>
      </el-skeleton>

      <!-- Subtitle lines -->
      <el-skeleton animated v-if="lines >= 2">
        <template #template>
          <el-skeleton-item variant="text" style="width: 85%; height: 14px" />
        </template>
      </el-skeleton>

      <el-skeleton animated v-if="lines >= 3">
        <template #template>
          <el-skeleton-item variant="text" style="width: 45%; height: 14px" />
        </template>
      </el-skeleton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  /** Number of text lines after the title. Default matches a PostCard layout. */
  lines?: number
  /** Show a circle avatar placeholder. */
  showAvatar?: boolean
  /** Inline variant for horizontal layouts (e.g., ChatListItem). */
  inline?: boolean
}>(), {
  lines: 3,
  showAvatar: true,
  inline: false,
})

const avatarStyle = computed(() => {
  const size = props.inline ? '40px' : '44px'
  return { width: size, height: size }
})
</script>

<style scoped>
.skeleton-card {
  display: flex;
  gap: 12px;
  padding: 14px 16px;
  background: var(--bg-white);
}

.skeleton-card--inline {
  align-items: center;
}

.skeleton-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}
</style>
