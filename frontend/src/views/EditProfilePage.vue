<!-- Edit Profile (编辑资料) — form pre-filled with current user data -->
<template>
  <div class="edit-profile-page" v-if="user">
    <AppHeader title="编辑资料" :show-back="true" />

    <div class="edit-form">
      <!-- Avatar URL -->
      <div class="form-section">
        <label class="form-label">头像 URL</label>
        <el-input v-model="form.avatar" placeholder="输入头像图片地址" size="large" />
      </div>

      <!-- Nickname -->
      <div class="form-section">
        <label class="form-label">昵称</label>
        <el-input v-model="form.nickname" placeholder="你的显示名称" maxlength="50" size="large" />
      </div>

      <!-- Gender -->
      <div class="form-section">
        <label class="form-label">性别</label>
        <el-radio-group v-model="form.gender">
          <el-radio v-for="g in GENDER_OPTIONS" :key="g.value" :value="g.value">
            {{ g.label }}
          </el-radio>
        </el-radio-group>
      </div>

      <!-- Bio -->
      <div class="form-section">
        <label class="form-label">个人简介</label>
        <el-input
          v-model="form.bio"
          type="textarea"
          placeholder="介绍一下自己..."
          maxlength="500"
          show-word-limit
          :autosize="{ minRows: 2, maxRows: 4 }"
        />
      </div>

      <!-- Tags -->
      <div class="form-section">
        <label class="form-label">兴趣标签</label>
        <TagsEditor v-model="form.tags" :max="10" :suggestions="SUGGESTED_TAGS" />
      </div>

      <!-- Phone -->
      <div class="form-section">
        <label class="form-label">手机号</label>
        <el-input v-model="form.phone" placeholder="选填" maxlength="20" size="large" />
      </div>

      <!-- University -->
      <div class="form-section">
        <label class="form-label">大学</label>
        <el-input v-model="form.university" placeholder="学校全称" maxlength="100" size="large" />
      </div>

      <!-- College -->
      <div class="form-section">
        <label class="form-label">学院</label>
        <el-input v-model="form.college" placeholder="如：计算机学院" maxlength="100" size="large" />
      </div>

      <!-- Major -->
      <div class="form-section">
        <label class="form-label">专业</label>
        <el-input v-model="form.major" placeholder="如：软件工程" maxlength="100" size="large" />
      </div>

      <!-- Grade -->
      <div class="form-section">
        <label class="form-label">年级</label>
        <el-select v-model="form.grade" placeholder="选择年级" clearable size="large" style="width: 100%">
          <el-option v-for="g in GRADE_OPTIONS" :key="g.value" :label="g.label" :value="g.value" />
        </el-select>
      </div>

      <!-- Submit -->
      <div class="form-actions">
        <el-button
          type="primary"
          size="large"
          :loading="isSubmitting"
          @click="handleSave"
          class="save-btn"
        >
          {{ isSubmitting ? '保存中...' : '保存' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { GRADE_OPTIONS, GENDER_OPTIONS, SUGGESTED_TAGS } from '@/utils/constants'
import type { UserUpdateRequest } from '@/types'
import AppHeader from '@/components/common/AppHeader.vue'
import TagsEditor from '@/components/common/TagsEditor.vue'

const router = useRouter()
const authStore = useAuthStore()
const isSubmitting = ref(false)

const user = computed(() => authStore.currentUser)

const form = reactive({
  avatar: user.value?.avatar || '',
  nickname: user.value?.nickname || '',
  gender: user.value?.gender || '',
  bio: user.value?.bio || '',
  tags: (user.value?.tags || []) as string[],
  phone: user.value?.phone || '',
  university: user.value?.university || '',
  college: user.value?.college || '',
  major: user.value?.major || '',
  grade: user.value?.grade || '',
})

async function handleSave() {
  isSubmitting.value = true
  try {
    const data: UserUpdateRequest = {}
    if (form.avatar !== (user.value?.avatar || '')) data.avatar = form.avatar || undefined
    if (form.nickname !== (user.value?.nickname || '')) data.nickname = form.nickname || undefined
    if (form.gender !== (user.value?.gender || '')) data.gender = form.gender || undefined
    if (form.bio !== (user.value?.bio || '')) data.bio = form.bio || undefined
    if (JSON.stringify(form.tags) !== JSON.stringify(user.value?.tags || [])) data.tags = form.tags.length ? form.tags : undefined
    if (form.phone !== (user.value?.phone || '')) data.phone = form.phone || undefined
    if (form.university !== (user.value?.university || '')) data.university = form.university || undefined
    if (form.college !== (user.value?.college || '')) data.college = form.college || undefined
    if (form.major !== (user.value?.major || '')) data.major = form.major || undefined
    if (form.grade !== (user.value?.grade || '')) data.grade = form.grade || undefined

    await authStore.updateProfile(data)
    ElMessage.success('资料已保存')
    router.push('/profile')
  } catch (err: unknown) {
    ElMessage.error((err as Error)?.message || '保存失败')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.edit-profile-page {
  min-height: 100vh;
  background: #fff;
}

.edit-form {
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

.form-actions {
  padding-top: 16px;
}

.save-btn {
  width: 100%;
}
</style>
