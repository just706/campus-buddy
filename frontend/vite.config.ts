import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },

  server: {
    port: 5173,
    proxy: {
      // HTTP API proxy to backend
      '/api/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // WebSocket proxy must be handled separately — configure ws
      '/api/v1/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
