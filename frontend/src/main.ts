/**
 * Campus BUDDY — Application entry point.
 *
 * Sets up Vue 3 with Pinia, Vue Router, Element Plus (Chinese locale),
 * and global icon registration.
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import './assets/styles/global.css'

const app = createApp(App)

// Pinia (state management)
app.use(createPinia())

// Vue Router
app.use(router)

// Element Plus with Chinese locale
app.use(ElementPlus, { locale: zhCn })

// Register all Element Plus icons globally
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
