<!-- Login page — email/username + password -->
<template>
  <div class="login-page">
    <div class="login-card">
      <!-- Logo & Title -->
      <div class="login-header">
        <el-icon :size="48" color="#409EFF">
          <Connection />
        </el-icon>
        <h1 class="login-title">Campus BUDDY</h1>
        <p class="login-subtitle">校园搭子社交平台</p>
      </div>

      <!-- Error Alert -->
      <el-alert
        v-if="errorMsg"
        :title="errorMsg"
        type="error"
        show-icon
        closable
        @close="errorMsg = ''"
        class="login-error"
      />

      <!-- Login Form -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="login" label="账号">
          <el-input
            v-model="form.login"
            placeholder="请输入邮箱或用户名"
            :prefix-icon="User"
            size="large"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password" label="密码">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="isSubmitting"
            :disabled="isSubmitting"
            @click="handleLogin"
            class="login-btn"
          >
            {{ isSubmitting ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Footer -->
      <div class="login-footer">
        <span>还没有账号？</span>
        <router-link to="/register" class="register-link">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Connection } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const isSubmitting = ref(false)
const errorMsg = ref('')

const form = reactive({
  login: '',
  password: '',
})

const rules: FormRules = {
  login: [
    { required: true, message: '请输入邮箱或用户名', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 1, max: 128, message: '密码长度不超过 128 个字符', trigger: 'blur' },
  ],
}

async function handleLogin() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  isSubmitting.value = true
  errorMsg.value = ''

  try {
    await authStore.login({
      login: form.login,
      password: form.password,
    })
    ElMessage.success('登录成功')
    // Redirect to intended page or default
    const redirect = (route.query.redirect as string) || '/posts'
    router.replace(redirect)
  } catch (err: unknown) {
    const msg =
      (err as { response?: { data?: { message?: string } } })?.response?.data
        ?.message ||
      (err as Error)?.message ||
      '登录失败，请稍后再试'
    errorMsg.value = msg
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #409eff15 0%, #67c23a10 100%);
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 380px;
  background: #fff;
  border-radius: 16px;
  padding: 40px 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-title {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin: 12px 0 4px;
}

.login-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.login-error {
  margin-bottom: 16px;
}

.login-btn {
  width: 100%;
}

.login-footer {
  text-align: center;
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.register-link {
  color: #409eff;
  text-decoration: none;
  margin-left: 4px;
  font-weight: 500;
}
</style>
