<!-- Reusable top navigation bar with back button and title -->
<template>
  <header class="app-header">
    <div class="header-left">
      <el-button
        v-if="showBack"
        :icon="ArrowLeft"
        text
        @click="goBack"
      />
      <slot name="left" />
    </div>
    <h2 class="header-title">{{ title }}</h2>
    <div class="header-right">
      <slot name="right" />
    </div>
  </header>
</template>

<script setup lang="ts">
import { ArrowLeft } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

defineProps<{
  title: string
  showBack?: boolean
}>()

const router = useRouter()

function goBack() {
  router.back()
}
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 99;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 12px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.header-left,
.header-right {
  min-width: 48px;
  display: flex;
  align-items: center;
}

.header-right {
  justify-content: flex-end;
}

.header-title {
  font-size: 17px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
