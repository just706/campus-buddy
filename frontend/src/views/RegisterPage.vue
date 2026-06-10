<!-- Register page — 2-step form: Account info → School info -->
<template>
  <div class="register-page">
    <div class="register-card">
      <!-- Header -->
      <div class="register-header">
        <el-button :icon="ArrowLeft" text @click="goBack" class="back-btn" />
        <h1 class="register-title">创建账号</h1>
      </div>

      <!-- Steps -->
      <el-steps :active="step" align-center class="register-steps">
        <el-step title="账号信息" />
        <el-step title="学校信息" />
      </el-steps>

      <!-- Error Alert -->
      <el-alert
        v-if="errorMsg"
        :title="errorMsg"
        type="error"
        show-icon
        closable
        @close="errorMsg = ''"
        class="register-error"
      />

      <!-- Step 1: Account Info -->
      <el-form
        v-show="step === 0"
        ref="formRef1"
        :model="form"
        :rules="rules1"
        label-position="top"
        @keyup.enter="nextStep"
      >
        <el-form-item prop="username" label="用户名">
          <el-input v-model="form.username" placeholder="3-50个字符" size="large" maxlength="50" />
        </el-form-item>

        <el-form-item prop="email" label="邮箱">
          <el-input v-model="form.email" placeholder="用于账号验证" size="large" />
        </el-form-item>

        <el-form-item prop="phone" label="手机号（选填）">
          <el-input v-model="form.phone" placeholder="选填" size="large" maxlength="20" />
        </el-form-item>

        <el-form-item prop="password" label="密码">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="6-128个字符"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item prop="confirmPassword" label="确认密码">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="再次输入密码"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" @click="nextStep" class="step-btn">
            下一步
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Step 2: School Info -->
      <el-form
        v-show="step === 1"
        ref="formRef2"
        :model="form"
        :rules="rules2"
        label-position="top"
        @keyup.enter="handleRegister"
      >
        <el-form-item prop="university" label="大学">
          <el-input v-model="form.university" placeholder="请输入学校全称" size="large" maxlength="100" />
        </el-form-item>

        <el-form-item prop="college" label="学院（选填）">
          <el-input v-model="form.college" placeholder="如：计算机学院" size="large" maxlength="100" />
        </el-form-item>

        <el-form-item prop="major" label="专业（选填）">
          <el-input v-model="form.major" placeholder="如：软件工程" size="large" maxlength="100" />
        </el-form-item>

        <el-form-item prop="grade" label="年级（选填）">
          <el-select v-model="form.grade" placeholder="请选择年级" size="large" clearable style="width: 100%">
            <el-option
              v-for="g in GRADE_OPTIONS"
              :key="g.value"
              :label="g.label"
              :value="g.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item prop="nickname" label="昵称（选填）">
          <el-input v-model="form.nickname" placeholder="你的显示名称" size="large" maxlength="50" />
        </el-form-item>

        <el-form-item prop="gender" label="性别（选填）">
          <el-radio-group v-model="form.gender">
            <el-radio v-for="g in GENDER_OPTIONS" :key="g.value" :value="g.value">
              {{ g.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item>
          <div class="step-actions">
            <el-button size="large" @click="step = 0">上一步</el-button>
            <el-button
              type="primary"
              size="large"
              :loading="isSubmitting"
              :disabled="isSubmitting"
              @click="handleRegister"
            >
              {{ isSubmitting ? '注册中...' : '完成注册' }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <!-- Footer -->
      <div class="register-footer">
        <span>已有账号？</span>
        <router-link to="/login" class="login-link">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { GRADE_OPTIONS, GENDER_OPTIONS } from '@/utils/constants'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const step = ref(0)
const isSubmitting = ref(false)
const errorMsg = ref('')
const formRef1 = ref<FormInstance>()
const formRef2 = ref<FormInstance>()

const form = reactive({
  // Step 1
  username: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  // Step 2
  university: '',
  college: '',
  major: '',
  grade: '',
  nickname: '',
  gender: '',
})

const validateConfirmPassword = (_rule: unknown, value: string, callback: (e?: Error) => void) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules1: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为 3-50 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度为 6-128 个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

const rules2: FormRules = {
  university: [
    { required: true, message: '请输入学校名称', trigger: 'blur' },
  ],
}

async function nextStep() {
  if (!formRef1.value) return
  const valid = await formRef1.value.validate().catch(() => false)
  if (!valid) return
  step.value = 1
}

async function handleRegister() {
  if (!formRef2.value) return
  const valid = await formRef2.value.validate().catch(() => false)
  if (!valid) return

  isSubmitting.value = true
  errorMsg.value = ''

  try {
    await authStore.register({
      username: form.username,
      email: form.email,
      password: form.password,
      phone: form.phone || undefined,
      university: form.university,
      college: form.college || undefined,
      major: form.major || undefined,
      grade: form.grade || undefined,
      nickname: form.nickname || undefined,
      gender: form.gender || undefined,
    })
    ElMessage.success('注册成功')
    router.replace('/posts')
  } catch (err: unknown) {
    const msg =
      (err as { response?: { data?: { message?: string } } })?.response?.data
        ?.message ||
      (err as Error)?.message ||
      '注册失败，请稍后再试'
    errorMsg.value = msg
  } finally {
    isSubmitting.value = false
  }
}

function goBack() {
  if (step.value === 1) {
    step.value = 0
  } else {
    router.push('/login')
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #409eff15 0%, #67c23a10 100%);
  padding: 24px;
}

.register-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 16px;
  padding: 24px 28px 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.register-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
}

.back-btn {
  position: absolute;
  left: -8px;
}

.register-title {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  margin: 0 auto;
}

.register-steps {
  margin-bottom: 24px;
}

.register-error {
  margin-bottom: 16px;
}

.step-btn {
  width: 100%;
}

.step-actions {
  display: flex;
  gap: 12px;
  width: 100%;
}

.step-actions .el-button {
  flex: 1;
}

.register-footer {
  text-align: center;
  font-size: 14px;
  color: #909399;
  margin-top: 16px;
}

.login-link {
  color: #409eff;
  text-decoration: none;
  margin-left: 4px;
  font-weight: 500;
}
</style>
