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
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import Header from '../components/common/Header.vue'
import Sidebar from '../components/common/Sidebar.vue'
import ApplicationForm from '../components/student/ApplicationForm.vue'
import ApplicationRecord from '../components/student/ApplicationRecord.vue'
import Statistics from '../components/student/Statistics.vue'
import Profile from '../components/student/Profile.vue'

const authStore = useAuthStore()

const currentPage = ref('application-form')

const pageComponents = {
  'application-form': ApplicationForm,
  'application-record': ApplicationRecord,
  'statistics': Statistics,
  'profile': Profile
}

const currentPageComponent = computed(() => pageComponents[currentPage.value])

const userInfo = computed(() => ({
  name: authStore.userName,
  faculty: authStore.user?.faculty || '信息学院',
  major: authStore.user?.major || '计算机科学与技术'
}))

const switchPage = (page) => {
  currentPage.value = page
}
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