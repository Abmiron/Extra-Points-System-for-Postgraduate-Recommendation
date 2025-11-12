import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// 导入Font Awesome相关模块
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { fas } from '@fortawesome/free-solid-svg-icons'

// 创建Vue应用
const app = createApp(App)

// 安装Pinia状态管理
const pinia = createPinia()
app.use(pinia)

// 安装Vue Router
app.use(router)

// 配置Font Awesome
// 添加所有solid图标到库中
library.add(fas)
// 全局注册FontAwesomeIcon组件
app.component('font-awesome-icon', FontAwesomeIcon)

// 挂载应用
app.mount('#app')

console.log('Vue应用已成功启动，已安装Pinia和Vue Router以及Font Awesome图标库')