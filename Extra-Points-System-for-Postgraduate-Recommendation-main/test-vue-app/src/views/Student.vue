<template>
  <div class="container">
    <Header :user-name="authStore.userName" :user-avatar="authStore.userAvatar" title="推免加分系统" />

    <div class="content-wrapper">
      <Sidebar :active-page="currentPage" @page-change="switchPage" :user-info="userInfo" user-type="student" />

      <main class="main-content">
        <component :is="currentPageComponent" />
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
import ApplicationForm from '../components/student/ApplicationForm.vue'
import ApplicationHistory from '../components/student/ApplicationHistory.vue'
import Statistics from '../components/student/Statistics.vue'
import Profile from '../components/student/Profile.vue'

const router = useRouter()
const authStore = useAuthStore()
const applicationsStore = useApplicationsStore()

const currentPage = ref('application-form')

const pageComponents = {
  'application-form': ApplicationForm,
  'application-record': ApplicationHistory,
  'statistics': Statistics,
  'profile': Profile
}

const currentPageComponent = computed(() => pageComponents[currentPage.value])

const userInfo = computed(() => ({
  name: authStore.userName,
  faculty: authStore.user?.faculty || '信息学院',
  major: authStore.user?.major || '计算机科学与技术',
  studentId: authStore.user?.studentId || '',
  roleName: authStore.user?.roleName || '学生'  // 从authStore获取roleName，而不是硬编码
}))

const switchPage = (page) => {
  currentPage.value = page
}

// 切换到申请表单页面
const switchToApplicationForm = () => {
  currentPage.value = 'application-form'
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
  const hasStudentRole = authStore.role === 'student' && localStorageRole === 'student'
  
  console.log('Student组件权限验证:', {
    storeRole: authStore.role,
    localStorageRole,
    hasStudentRole
  })
  
  if (!hasStudentRole) {
    console.error('权限验证失败：不是学生账号，清除认证信息')
    // 清除可能有误的认证信息
    localStorage.removeItem('userInfo')
    localStorage.removeItem('token')
    // 重置authStore
    authStore.user = null
    authStore.token = ''
    
    alert('您没有权限访问学生端')
    router.push('/login')
  } else {
    // 确保数据已加载
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