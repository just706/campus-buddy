<!-- Profile (个人中心) — user info, stats, menu, logout -->
<template>
  <div class="profile-page" v-if="user">
    <!-- User Info Card -->
    <div class="profile-header">
      <UserAvatar :src="user.avatar" :name="user.nickname || user.username" :size="72" />
      <h2 class="profile-name">{{ user.nickname || user.username }}</h2>
      <p class="profile-school">{{ user.university }}<span v-if="user.major"> · {{ user.major }}</span></p>
      <p v-if="user.grade" class="profile-grade">{{ user.grade }}</p>
      <p v-if="user.bio" class="profile-bio">{{ user.bio }}</p>
      <div class="profile-tags" v-if="user.tags && user.tags.length">
        <el-tag v-for="tag in user.tags" :key="tag" size="small">#{{ tag }}</el-tag>
      </div>
      <el-button type="primary" size="small" plain @click="router.push('/profile/edit')" class="edit-btn">
        编辑资料
      </el-button>
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div class="stat-item" @click="router.push('/posts')">
        <span class="stat-num">{{ stats.posts }}</span>
        <span class="stat-label">我的邀约</span>
      </div>
      <div class="stat-item" @click="router.push('/matches')">
        <span class="stat-num">{{ stats.matches }}</span>
        <span class="stat-label">匹配数</span>
      </div>
      <div class="stat-item" @click="router.push('/chats')">
        <span class="stat-num">{{ stats.buddies }}</span>
        <span class="stat-label">我的搭子</span>
      </div>
    </div>

    <!-- Menu -->
    <div class="menu-list">
      <div class="menu-item" @click="router.push('/posts')">
        <el-icon :size="18"><Document /></el-icon>
        <span>我的邀约</span>
        <el-icon :size="14"><ArrowRight /></el-icon>
      </div>
      <div class="menu-item" @click="router.push('/matches')">
        <el-icon :size="18"><Connection /></el-icon>
        <span>我的匹配</span>
        <el-icon :size="14"><ArrowRight /></el-icon>
      </div>
      <div class="menu-item menu-item--disabled">
        <el-icon :size="18"><Setting /></el-icon>
        <span>账号设置</span>
        <span class="menu-hint">预留</span>
      </div>
      <div class="menu-item menu-item--disabled">
        <el-icon :size="18"><QuestionFilled /></el-icon>
        <span>帮助与反馈</span>
        <span class="menu-hint">预留</span>
      </div>
    </div>

    <!-- Logout -->
    <div class="logout-section">
      <el-button type="danger" size="large" plain @click="handleLogout" class="logout-btn">
        退出登录
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { Document, Connection, Setting, QuestionFilled, ArrowRight } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import UserAvatar from '@/components/common/UserAvatar.vue'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.currentUser)

// Stats (simplified — could be fetched from API)
const stats = ref({
  posts: 0,
  matches: 0,
  buddies: 0,
})

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确认退出登录？', '退出登录', {
      confirmButtonText: '退出',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }
  authStore.logout()
  router.replace('/login')
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  padding-bottom: 80px;
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 24px 20px;
  background: #fff;
  text-align: center;
}

.profile-name {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  margin: 12px 0 4px;
}

.profile-school {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.profile-grade {
  font-size: 13px;
  color: #909399;
  margin: 2px 0 0;
}

.profile-bio {
  font-size: 14px;
  color: #606266;
  margin: 10px 0 0;
  max-width: 280px;
  line-height: 1.5;
}

.profile-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
  margin-top: 10px;
}

.edit-btn {
  margin-top: 16px;
}

.stats-row {
  display: flex;
  background: #fff;
  margin-top: 8px;
  padding: 16px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  gap: 4px;
}

.stat-num {
  font-size: 22px;
  font-weight: 700;
  color: #409eff;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.menu-list {
  background: #fff;
  margin-top: 8px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f5f7fa;
  font-size: 15px;
  color: #303133;
  transition: background 0.15s;
}

.menu-item:active {
  background: #f5f7fa;
}

.menu-item .el-icon:last-child {
  margin-left: auto;
  color: #c0c4cc;
}

.menu-item--disabled {
  color: #c0c4cc;
  cursor: not-allowed;
}

.menu-hint {
  margin-left: auto;
  font-size: 12px;
  color: #c0c4cc;
}

.logout-section {
  padding: 24px 16px;
}

.logout-btn {
  width: 100%;
}
</style>
