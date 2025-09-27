<template>
  <div class="container">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="logo-area">
        <img src="/images/logo(1).png" alt="厦门大学校徽" class="logo">
        <span class="university-name">推免加分系统</span>
      </div>
      <div class="header-right">
        <div class="notification" @click="showNotifications">
          <i class="fas fa-bell"></i>
          <span class="notification-badge">3</span>
        </div>
        <div class="user-menu">
          <img src="/images/头像1.jpg" alt="用户头像" class="user-avatar">
          <span>张同学</span>
          <button class="logout-btn" @click="logout"><i class="fas fa-sign-out-alt"></i></button>
        </div>
      </div>
    </header>

    <div class="content-wrapper">
      <!-- 左侧边栏 -->
      <aside class="sidebar">
        <div class="user-info">
          <img src="/images/头像1.jpg" alt="用户头像" class="user-avatar">
          <div class="user-details">
            <div class="user-name">张同学</div>
            <div class="user-faculty">信息学院</div>
            <div class="user-major">计算机科学与技术</div>
          </div>
        </div>
        <nav class="sidebar-nav">
          <ul>
            <li v-for="item in menuItems" :key="item.target" 
                :class="{ active: currentPage === item.target }"
                @click="switchPage(item.target)">
              <a href="#"><i :class="item.icon"></i> <span>{{ item.name }}</span></a>
            </li>
          </ul>
        </nav>
      </aside>

      <!-- 主内容区 -->
      <main class="main-content">
        <!-- 加分申请页面 -->
        <div v-if="currentPage === 'application-form'" class="page-content">
          <ApplicationForm />
        </div>

        <!-- 申请记录页面 -->
        <div v-if="currentPage === 'application-record'" class="page-content">
          <ApplicationRecord />
        </div>

        <!-- 加分统计页面 -->
        <div v-if="currentPage === 'statistics'" class="page-content">
          <Statistics />
        </div>

        <!-- 个人信息页面 -->
        <div v-if="currentPage === 'profile'" class="page-content">
          <Profile />
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ApplicationForm from '../components/student/ApplicationForm.vue'
import ApplicationRecord from '../components/student/ApplicationRecord.vue'
import Statistics from '../components/student/Statistics.vue'
import Profile from '../components/student/Profile.vue'

export default {
  name: 'Student',
  components: {
    ApplicationForm,
    ApplicationRecord,
    Statistics,
    Profile
  },
  setup() {
    const router = useRouter()
    const currentPage = ref('application-form')
    
    const menuItems = [
      { target: 'application-form', name: '加分申请', icon: 'fas fa-file-upload' },
      { target: 'application-record', name: '申请记录', icon: 'fas fa-history' },
      { target: 'statistics', name: '加分统计', icon: 'fas fa-chart-pie' },
      { target: 'profile', name: '个人信息', icon: 'fas fa-user' }
    ]

    const switchPage = (page) => {
      currentPage.value = page
    }

    const showNotifications = () => {
      alert('您有3条未读通知')
    }

    const logout = () => {
      if (confirm('确定要退出登录吗？')) {
        router.push('/login')
      }
    }

    return {
      currentPage,
      menuItems,
      switchPage,
      showNotifications,
      logout
    }
  }
}
</script>