import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'

// 引入整个 solid 图标包
import { fas } from '@fortawesome/free-solid-svg-icons'

// 添加所有 solid 图标到库
library.add(fas)

// 全局样式
import './assets/styles/main.css'

// 引入stores
import { useAuthStore } from './stores/auth'
import { useApplicationsStore } from './stores/applications'

const app = createApp(App)
const pinia = createPinia()

app.use(router)
app.use(pinia)
app.component('font-awesome-icon', FontAwesomeIcon)

document.addEventListener('DOMContentLoaded', () => {
  // 初始化stores
  const authStore = useAuthStore()
  const applicationsStore = useApplicationsStore()
  
  // 初始化auth store（检查是否有保存的登录状态）
  authStore.initialize()
  
  // 加载申请数据
  applicationsStore.fetchApplications()
  
  app.mount('#app')
})