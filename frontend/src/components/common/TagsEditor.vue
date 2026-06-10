<!-- Inline tag editor — input with Enter to add, chips with X to remove -->
<template>
  <div class="tags-editor">
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
    <el-input
      v-if="modelValue.length < max"
      v-model="input"
      :placeholder="placeholder"
      size="small"
      @keyup.enter.prevent="addTag"
      @blur="addTag"
      class="tag-input"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: string[]
  max?: number
  placeholder?: string
}>(), {
  max: 10,
  placeholder: '输入标签，回车添加',
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
</script>

<style scoped>
.tags-editor {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
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
</style>
