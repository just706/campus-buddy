/**
 * Vue Router configuration with authentication guards.
 *
 * Route meta:
 * - requiresAuth: true → redirect to /login if not authenticated
 * - tab: number → show bottom TabBar with this tab active
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Lazy-loaded page components
const LoginPage = () => import('@/views/LoginPage.vue')
const RegisterPage = () => import('@/views/RegisterPage.vue')
const PostSquarePage = () => import('@/views/PostSquarePage.vue')
const PostDetailPage = () => import('@/views/PostDetailPage.vue')
const CreatePostPage = () => import('@/views/CreatePostPage.vue')
const EditPostPage = () => import('@/views/EditPostPage.vue')
const RecommendationsPage = () => import('@/views/RecommendationsPage.vue')
const MyMatchesPage = () => import('@/views/MyMatchesPage.vue')
const ChatListPage = () => import('@/views/ChatListPage.vue')
const ChatWindowPage = () => import('@/views/ChatWindowPage.vue')
const NotificationsPage = () => import('@/views/NotificationsPage.vue')
const ProfilePage = () => import('@/views/ProfilePage.vue')
const EditProfilePage = () => import('@/views/EditProfilePage.vue')
const UserProfilePage = () => import('@/views/UserProfilePage.vue')

const routes: RouteRecordRaw[] = [
  // ===== Public Routes =====
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
    meta: { requiresAuth: false },
  },

  // ===== Authenticated Routes =====
  {
    path: '/posts',
    name: 'PostSquare',
    component: PostSquarePage,
    meta: { requiresAuth: true, tab: 1 },
  },
  {
    path: '/posts/new',
    name: 'CreatePost',
    component: CreatePostPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/posts/:id/edit',
    name: 'EditPost',
    component: EditPostPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/posts/:id',
    name: 'PostDetail',
    component: PostDetailPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/recommendations',
    name: 'Recommendations',
    component: RecommendationsPage,
    meta: { requiresAuth: true, tab: 2 },
  },
  {
    path: '/matches',
    name: 'MyMatches',
    component: MyMatchesPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/chats',
    name: 'ChatList',
    component: ChatListPage,
    meta: { requiresAuth: true, tab: 3 },
  },
  {
    path: '/chats/:id',
    name: 'ChatWindow',
    component: ChatWindowPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: NotificationsPage,
    meta: { requiresAuth: true, tab: 4 },
  },
  {
    path: '/profile/edit',
    name: 'EditProfile',
    component: EditProfilePage,
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfilePage,
    meta: { requiresAuth: true, tab: 5 },
  },
  {
    path: '/users/:id',
    name: 'UserProfile',
    component: UserProfilePage,
    meta: { requiresAuth: true },
  },

  // ===== Default Redirect =====
  {
    path: '/',
    redirect: '/posts',
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/posts',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ===== Navigation Guard =====
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  // Try to restore session on first navigation
  if (!authStore.isInitialized) {
    await authStore.init()
  }

  const isAuth = authStore.isAuthenticated

  if (to.meta.requiresAuth === false) {
    // Public routes (login, register)
    if (isAuth) {
      // Already logged in — redirect to home
      next('/posts')
    } else {
      next()
    }
  } else {
    // Protected routes
    if (isAuth) {
      next()
    } else {
      // Save the intended destination for post-login redirect
      next({ path: '/login', query: { redirect: to.fullPath } })
    }
  }
})

export default router
