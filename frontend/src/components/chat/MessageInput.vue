<!-- Chat message input bar — Enter to send, Shift+Enter for newline -->
<template>
  <div class="message-input-bar">
    <div class="input-wrapper">
      <textarea
        ref="textareaRef"
        v-model="text"
        class="input-textarea"
        :placeholder="placeholder"
        rows="1"
        :disabled="disabled"
        @keydown.enter.exact.prevent="handleSend"
        @input="autoResize"
      />
    </div>
    <el-button
      class="send-btn"
      :disabled="!canSend || disabled"
      type="primary"
      :icon="Promotion"
      circle
      @click="handleSend"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { Promotion } from '@element-plus/icons-vue'

const props = withDefaults(defineProps<{
  placeholder?: string
  disabled?: boolean
}>(), {
  placeholder: '输入消息...',
  disabled: false,
})

const emit = defineEmits<{
  send: [content: string]
}>()

const text = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

const canSend = computed(() => text.value.trim().length > 0)

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

function handleSend() {
  const content = text.value.trim()
  if (!content || props.disabled) return
  emit('send', content)
  text.value = ''
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  })
}
</script>

<style scoped>
.message-input-bar {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 8px 12px;
  padding-bottom: calc(8px + env(safe-area-inset-bottom));
  background: var(--bg-white);
  border-top: 1px solid var(--border-color);
}

.input-wrapper {
  flex: 1;
  background: #f0f2f5;
  border-radius: 20px;
  padding: 6px 14px;
}

.input-textarea {
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  font-size: 15px;
  line-height: 1.5;
  resize: none;
  font-family: inherit;
  color: var(--text-primary);
  max-height: 120px;
  overflow-y: auto;
}

.input-textarea::placeholder {
  color: var(--text-placeholder);
}

.input-textarea:disabled {
  opacity: 0.6;
}

.send-btn {
  flex-shrink: 0;
  align-self: center;
}
</style>
