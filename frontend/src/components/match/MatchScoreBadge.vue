<!-- Match score badge — circular progress display with color threshold -->
<template>
  <div class="match-score-badge" :class="`match-score-badge--${size}`">
    <svg class="score-ring" viewBox="0 0 60 60" v-if="size === 'large'">
      <circle
        class="ring-bg"
        cx="30" cy="30" r="26"
        fill="none"
        stroke-width="4"
      />
      <circle
        class="ring-fill"
        cx="30" cy="30" r="26"
        fill="none"
        stroke-width="4"
        :stroke="color"
        :stroke-dasharray="dashArray"
        stroke-linecap="round"
        transform="rotate(-90 30 30)"
      />
    </svg>
    <span class="score-text" :style="{ color, fontSize: size === 'large' ? '18px' : '14px' }">
      {{ score }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getScoreColor } from '@/utils/constants'

const props = withDefaults(defineProps<{
  score: number
  size?: 'small' | 'large'
}>(), {
  size: 'large',
})

const color = computed(() => getScoreColor(props.score))
const circumference = 2 * Math.PI * 26
const dashArray = computed(() => {
  const pct = props.score / 100
  const filled = circumference * pct
  return `${filled} ${circumference - filled}`
})
</script>

<style scoped>
.match-score-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.match-score-badge--large {
  width: 64px;
  height: 64px;
}

.match-score-badge--small {
  width: 36px;
  height: 36px;
}

.score-ring {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.ring-bg {
  stroke: #e4e7ed;
}

.ring-fill {
  transition: stroke-dasharray 0.6s ease;
}

.score-text {
  font-weight: 700;
  z-index: 1;
}
</style>
