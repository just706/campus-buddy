<!-- Post form — shared create/edit form for buddy-finding posts -->
<template>
  <div class="post-form">
    <!-- Category Selection -->
    <div class="form-section">
      <label class="form-label">类别 <span class="required">*</span></label>
      <div class="category-options">
        <div
          v-for="cat in CATEGORIES"
          :key="cat.value"
          class="category-option"
          :class="{ 'category-option--active': form.category === cat.value }"
          :style="form.category === cat.value ? { borderColor: cat.color, background: cat.color + '10' } : {}"
          @click="form.category = cat.value"
        >
          <el-icon :size="24" :color="form.category === cat.value ? cat.color : '#909399'">
            <component :is="cat.icon" />
          </el-icon>
          <span class="category-label" :style="{ color: form.category === cat.value ? cat.color : '#909399' }">
            {{ cat.label }}
          </span>
        </div>
      </div>
    </div>

    <!-- Title -->
    <div class="form-section">
      <label class="form-label">标题 <span class="required">*</span></label>
      <el-input
        v-model="form.title"
        placeholder="如：找期末复习搭子，图书馆每天"
        maxlength="200"
        show-word-limit
        size="large"
      />
    </div>

    <!-- Description -->
    <div class="form-section">
      <label class="form-label">描述</label>
      <el-input
        v-model="form.description"
        type="textarea"
        placeholder="描述一下你想找什么样的搭子、计划安排等..."
        maxlength="5000"
        show-word-limit
        :autosize="{ minRows: 3, maxRows: 6 }"
      />
    </div>

    <!-- Target Count -->
    <div class="form-section">
      <label class="form-label">目标人数</label>
      <el-input-number v-model="form.target_count" :min="1" :max="100" size="large" />
    </div>

    <!-- Tags -->
    <div class="form-section">
      <label class="form-label">标签</label>
      <TagsEditor v-model="form.tags" :max="10" :suggestions="SUGGESTED_TAGS" />
    </div>

    <!-- Location -->
    <div class="form-section">
      <label class="form-label">地点</label>
      <el-input
        v-model="form.location"
        placeholder="如：图书馆三楼、体育馆"
        maxlength="200"
        size="large"
      />
    </div>

    <!-- Time Range -->
    <div class="form-section">
      <label class="form-label">时间</label>
      <el-input
        v-model="form.time_range"
        placeholder="如：每周三下午 3-5点"
        maxlength="200"
        size="large"
      />
    </div>

    <!-- Expires At -->
    <div class="form-section">
      <label class="form-label">截止日期</label>
      <el-date-picker
        v-model="form.expires_at"
        type="datetime"
        placeholder="选填，超时自动关闭"
        size="large"
        style="width: 100%"
      />
    </div>

    <!-- Submit -->
    <div class="form-actions">
      <el-button
        type="primary"
        size="large"
        :loading="isSubmitting"
        :disabled="!canSubmit"
        @click="handleSubmit"
        class="submit-btn"
      >
        {{ isSubmitting ? '提交中...' : submitLabel }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed } from 'vue'
import { CATEGORIES, SUGGESTED_TAGS } from '@/utils/constants'
import TagsEditor from '@/components/common/TagsEditor.vue'
import type { PostCreate } from '@/types'

const props = withDefaults(defineProps<{
  initialData?: Partial<PostCreate>
  isSubmitting?: boolean
  submitLabel?: string
}>(), {
  isSubmitting: false,
  submitLabel: '发布邀约',
})

const emit = defineEmits<{
  submit: [data: PostCreate]
}>()

const form = reactive<{
  category: string
  title: string
  description: string
  target_count: number
  tags: string[]
  location: string
  time_range: string
  expires_at: Date | null
}>({
  category: props.initialData?.category || '',
  title: props.initialData?.title || '',
  description: props.initialData?.description || '',
  target_count: props.initialData?.target_count || 1,
  tags: props.initialData?.tags || [],
  location: props.initialData?.location || '',
  time_range: props.initialData?.time_range || '',
  expires_at: props.initialData?.expires_at ? new Date(props.initialData.expires_at) : null,
})

const canSubmit = computed(() => form.category && form.title.trim())

function handleSubmit() {
  if (!canSubmit.value) return
  emit('submit', {
    category: form.category,
    title: form.title.trim(),
    description: form.description.trim() || undefined,
    target_count: form.target_count,
    tags: form.tags.length ? form.tags : undefined,
    location: form.location.trim() || undefined,
    time_range: form.time_range.trim() || undefined,
    expires_at: form.expires_at?.toISOString(),
  })
}
</script>

<style scoped>
.post-form {
  padding: 16px;
}

.form-section {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.required {
  color: #f56c6c;
}

.category-options {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.category-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 16px;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 64px;
  flex-shrink: 0;
}

.category-option:hover {
  border-color: #409eff;
}

.category-label {
  font-size: 12px;
  font-weight: 600;
}

.form-actions {
  padding-top: 16px;
}

.submit-btn {
  width: 100%;
}
</style>
