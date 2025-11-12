<template>
  <div class="container">
    <Header :user-name="authStore.userName" :user-avatar="authStore.userAvatar" title="推免加分系统-审核端" />

    <div class="content-wrapper">
      <Sidebar :active-page="currentPage" @page-change="switchPage" :user-info="userInfo" user-type="teacher" />

      <main class="main-content">
        <!-- 动态显示当前页面 -->
        <component :is="currentPageComponent" @new-application="switchToPendingReview" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useApplicationsStore } from '../stores/applications'

import Header from '../components/common/Header.vue'
import Sidebar from '../components/common/Sidebar.vue'

// 导入教师端组件
import PendingReview from '../components/teacher/PendingReview.vue'
import ReviewHistory from '../components/teacher/ReviewHistory.vue'
import StatisticsReport from '../components/teacher/StatisticsReport.vue'
import TeacherProfile from '../components/teacher/TeacherProfile.vue'
// 导入调试组件
import DebugPage from '../components/teacher/DebugPage.vue'

const router = useRouter()
const authStore = useAuthStore()
const applicationsStore = useApplicationsStore()

// 当前活动页面
const currentPage = ref('pending-review')

// 页面组件映射
const pageComponents = {
  'pending-review': PendingReview,
  'review-history': ReviewHistory,
  'statistics-report': StatisticsReport,
  'profile': TeacherProfile,
  'debug': DebugPage // 添加调试页面
}

const currentPageComponent = computed(() => pageComponents[currentPage.value])

// 用户信息
const userInfo = computed(() => ({
  name: authStore.userName,
  faculty: authStore.user?.faculty || '信息学院',
  roleName: authStore.user?.roleName || ''  // 移除默认的审核员角色
}))

// 切换页面
const switchPage = (page) => {
  currentPage.value = page
}

// 切换到待审核页面（用于从其他页面跳转）
const switchToPendingReview = () => {
  currentPage.value = 'pending-review'
}

// 权限验证和数据加载
onMounted(() => {
  // 从localStorage直接获取用户信息进行双重验证，避免store状态不一致
  let localStorageRole = ''
  try {
    const storedUserInfo = localStorage.getItem('userInfo')
    if (storedUserInfo) {
      const userInfo = JSON.parse(storedUserInfo)
      localStorageRole = userInfo?.role || ''
    }
  } catch (e) {
    console.warn('解析localStorage用户信息失败:', e)
  }
  
  // 双重验证：同时检查store中的角色和localStorage中的角色
  const hasTeacherRole = authStore.role === 'teacher' && localStorageRole === 'teacher'
  
  console.log('Teacher组件权限验证:', {
    storeRole: authStore.role,
    localStorageRole,
    hasTeacherRole
  })
  
  if (!hasTeacherRole) {
    console.error('权限验证失败：不是教师账号，清除认证信息')
    // 清除可能有误的认证信息
    localStorage.removeItem('userInfo')
    localStorage.removeItem('token')
    // 重置authStore
    authStore.user = null
    authStore.token = ''
    
    alert('您没有权限访问教师端')
    router.push('/login')
  } else {
    // 只有有权限时才加载数据
    if (applicationsStore.applications.length === 0) {
      applicationsStore.loadApplications()
    }
  }
})
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  height: 100vh !important;
  width: 100vw !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.content-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
  min-height: 0;
  width: 100%;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f5f7fa;
  min-height: 0;
  width: 100%;
}
</style>