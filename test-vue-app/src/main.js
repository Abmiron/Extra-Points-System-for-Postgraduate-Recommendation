import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faUser, faLock , faSpinner, faFileUpload,faHistory,faChartPie,faBell,faSignOutAlt,faUsers,faDatabase,faRuler,faCog,
  faDownload,faPlus,faBan,faCheck,faKey,faTrash,faEdit,faChevronLeft,faChevronRight,faTimes,
  faArchive,faEye
} from '@fortawesome/free-solid-svg-icons'

// 添加图标到库
library.add(faUser, faLock, faSpinner, faFileUpload,faHistory,faChartPie,faBell,faSignOutAlt,faUsers,faDatabase,faRuler,faCog,
  faDownload,faPlus,faBan,faCheck,faKey,faTrash,faEdit,faChevronLeft,faChevronRight,faTimes,
  faArchive,faEye
)

// 全局样式
import './assets/styles/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(router)
app.use(pinia)
app.component('font-awesome-icon', FontAwesomeIcon)

document.addEventListener('DOMContentLoaded', () => {
  app.mount('#app')
})