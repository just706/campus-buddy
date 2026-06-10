<!-- Inline tag editor — input with Enter to add, chips with X to remove, suggestion chips -->
<template>
  <div class="tags-editor">
    <!-- Selected tags -->
    <div class="tags-list">
      <el-tag
        v-for="(tag, idx) in modelValue"
        :key="idx"
        closable
        :disable-transitions="false"
        @close="removeTag(idx)"
        size="default"
        class="tag-chip"
      >
        {{ tag }}
      </el-tag>
    </div>

    <!-- Input for custom tags -->
    <el-input
      v-if="modelValue.length < max"
      v-model="input"
      :placeholder="placeholder"
      size="small"
      @keyup.enter.prevent="addTag"
      @blur="addTag"
      class="tag-input"
    />

    <!-- Suggested tags (only when suggestions provided and have room) -->
    <div v-if="suggestions.length > 0 && modelValue.length < max" class="suggestions-area">
      <template v-for="group in suggestions" :key="group.label">
        <div class="suggestion-group">
          <span class="suggestion-group-label">{{ group.label }}</span>
          <div class="suggestion-tags">
            <el-tag
              v-for="tag in group.tags"
              :key="tag"
              :type="modelValue.includes(tag) ? 'primary' : 'info'"
              :effect="modelValue.includes(tag) ? 'dark' : 'plain'"
              size="small"
              class="suggestion-tag"
              :class="{ 'suggestion-tag--added': modelValue.includes(tag) }"
              @click="toggleSuggestion(tag)"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: string[]
  max?: number
  placeholder?: string
  /** Grouped suggestions for quick tag selection. */
  suggestions?: Array<{ label: string; tags: string[] }>
}>(), {
  max: 10,
  placeholder: '输入标签，回车添加',
  suggestions: () => [],
})

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const input = ref('')

function addTag() {
  const trimmed = input.value.trim()
  if (!trimmed) return
  if (props.modelValue.includes(trimmed)) {
    input.value = ''
    return
  }
  if (props.modelValue.length >= props.max) return
  emit('update:modelValue', [...props.modelValue, trimmed])
  input.value = ''
}

function removeTag(idx: number) {
  const next = [...props.modelValue]
  next.splice(idx, 1)
  emit('update:modelValue', next)
}

/** Toggle a suggested tag on/off. */
function toggleSuggestion(tag: string) {
  if (props.modelValue.includes(tag)) {
    emit('update:modelValue', props.modelValue.filter((t) => t !== tag))
  } else if (props.modelValue.length < props.max) {
    emit('update:modelValue', [...props.modelValue, tag])
  }
  // Clear the input on suggestion click
  input.value = ''
}
</script>

<style scoped>
.tags-editor {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-chip {
  margin: 0;
}

.tag-input {
  width: 140px;
  flex-shrink: 0;
}

/* ===== Suggestions ===== */
.suggestions-area {
  background: #f9fafb;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 10px 12px;
  max-height: 220px;
  overflow-y: auto;
}

.suggestion-group {
  margin-bottom: 8px;
}

.suggestion-group:last-child {
  margin-bottom: 0;
}

.suggestion-group-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
  display: block;
}

.suggestion-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.suggestion-tag {
  cursor: pointer;
  user-select: none;
  transition: all 0.15s;
}

.suggestion-tag:hover {
  transform: scale(1.05);
}

.suggestion-tag--added {
  /* Already selected — shown as primary dark */
}
</style>
