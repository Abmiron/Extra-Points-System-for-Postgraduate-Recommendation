import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      // 简化代理配置，确保基本功能正常
      '/api': {
        target: 'http://localhost:9001',
        changeOrigin: true,
        secure: false
      }
    },
    port: 3000,
    // 增加调试信息
    debug: true
  }
})
