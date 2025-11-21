<template>
  <header class="header">
    <div class="logo-area">
      <img src="/images/logo(1).png" alt="厦门大学校徽" class="logo">
      <span class="university-name">{{ title }}</span>
    </div>
    <div class="header-right">
      <div class="notification" @click="showNotifications">
        <font-awesome-icon :icon="['fas', 'bell']" />
        <span class="notification-badge" v-if="notificationCount > 0">
          {{ notificationCount }}
        </span>
      </div>
      <div class="user-menu">
        <div class="user-info" @click="goToProfile">
          <img :src="userAvatar" alt="用户头像" class="user-avatar">
          <span>{{ userName }}</span>
        </div>
        <button class="logout-btn" @click="handleLogout">
          <font-awesome-icon :icon="['fas', 'sign-out-alt']" />
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useToastStore } from '../../stores/toast'
const toastStore = useToastStore()

const props = defineProps({
  userName: String,
  userAvatar: String,
  title: {
    type: String,
    default: '推免加分系统'
  }
})

const emit = defineEmits(['go-to-profile'])

const router = useRouter()
const authStore = useAuthStore()

const notificationCount = computed(() => {
  const roleCounts = {
    student: 3,
    teacher: 5,
    admin: 8
  }
  return roleCounts[authStore.role] || 0
})

const showNotifications = () => {
  toastStore.info(`您有${notificationCount.value}条未读通知`)
}

const goToProfile = () => {
  emit('go-to-profile')
}

const handleLogout = () => {
  if (confirm('确定要退出登录吗？')) {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #003d86, #0066cc);
  color: #fff;
  padding: 10px 20px;
  height: 60px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.logo-area {
  display: flex;
  align-items: center;
}

.logo {
  width: 150px;
  margin-right: 10px;
  border-radius: 4px;
  object-fit: contain;
}

.university-name {
  font-size: 20px;
  font-weight: bold;
  line-height: 60px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.notification {
  font-size: 18px;
  cursor: pointer;
  position: relative;
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 5px;
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -1px;
  background-color: #e74c3c;
  color: white;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  font-size: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-bottom: 0px;
  padding: 0px;
  border-bottom: 0px solid transparent;
}

.user-info .user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  margin-right: 8px;
  object-fit: cover;
  /* 添加抗锯齿效果 */
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
  /* 添加轻微阴影增强视觉效果 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logout-btn {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 16px;
  margin-left: 15px;
}

@media (max-width: 768px) {
  .header {
    padding: 10px 15px;
  }

  .logo {
    width: 120px;
  }

  .university-name {
    font-size: 16px;
  }

  .user-menu span {
    display: none;
  }
}
</style>