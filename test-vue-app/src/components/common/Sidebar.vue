<template>
  <aside class="sidebar">
    <div class="user-info">
      <img :src="userAvatar" alt="用户头像" class="user-avatar">
      <div class="user-details">
        <div class="user-name">{{ userInfo.name }}</div>
        <div class="user-faculty">{{ userInfo.faculty }}</div>
        <div class="user-role">{{ userInfo.roleName || '用户' }}</div>
      </div>
    </div>
    <nav class="sidebar-nav">
      <ul>
        <li v-for="item in menuItems" :key="item.key" :class="{ active: activePage === item.key }"
          @click="$emit('page-change', item.key)">
          <a href="#" @click.prevent>
            <font-awesome-icon :icon="item.icon" />
            <span>{{ item.title }}</span>
          </a>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../../stores/auth'

const props = defineProps({
  activePage: String,
  userInfo: Object,
  userType: {
    type: String,
    default: 'student'
  }
})

defineEmits(['page-change'])

const authStore = useAuthStore()

const userAvatar = computed(() => authStore.userAvatar)

// 菜单配置
const menuConfig = {
  student: [
    { key: 'application-form', icon: ['fas', 'file-upload'], title: '加分申请' },
    { key: 'application-record', icon: ['fas', 'history'], title: '申请记录' },
    { key: 'statistics', icon: ['fas', 'chart-pie'], title: '加分统计' },
    { key: 'profile', icon: ['fas', 'user'], title: '个人信息' }
  ],
  teacher: [
    { key: 'pending-review', icon: ['fas', 'file-upload'], title: '待审核申请' },
    { key: 'review-history', icon: ['fas', 'history'], title: '审核记录' },
    { key: 'statistics-report', icon: ['fas', 'chart-pie'], title: '统计报表' },
    { key: 'profile', icon: ['fas', 'user'], title: '个人信息' },
    { key: 'debug', icon: ['fas', 'bug'], title: '调试页面' } // 添加调试菜单
  ],
  admin: [
    { key: 'user-management', icon: ['fas', 'users'], title: '用户管理' },
    { key: 'data-management', icon: ['fas', 'database'], title: '数据管理' },
    { key: 'rule-management', icon: ['fas', 'ruler'], title: '规则管理' },
    { key: 'statistics-report', icon: ['fas', 'chart-pie'], title: '统计报表' },
    { key: 'system-settings', icon: ['fas', 'cog'], title: '系统设置' }
  ]
}

const menuItems = computed(() => menuConfig[props.userType] || [])
</script>

<style scoped>
.sidebar {
  width: 240px;
  background-color: #ffffff;
  border-right: 1px solid #e1e4e8;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
  overflow-y: auto;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 0 20px 20px;
  border-bottom: 1px solid #e1e4e8;
  margin-bottom: 20px;
}

.user-info .user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  margin-right: 12px;
  object-fit: cover;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-name {
  font-weight: bold;
  font-size: 16px;
  color: #333;
}

.user-faculty,
.user-role {
  font-size: 13px;
  color: #666;
  line-height: 1.3;
}

.sidebar-nav ul {
  list-style: none;
}

.sidebar-nav li {
  margin-bottom: 4px;
  cursor: pointer;
}

.sidebar-nav li a {
  text-decoration: none;
  color: #333;
  display: flex;
  align-items: center;
  padding: 12px 20px;
  border-radius: 0 4px 4px 0;
  transition: all 0.3s;
  font-size: 15px;
}

.sidebar-nav li a svg {
  margin-right: 10px;
  width: 20px;
  text-align: center;
}

.sidebar-nav li a:hover {
  background-color: #f0f2f5;
}

.sidebar-nav li.active a {
  background-color: #0057b1;
  color: #ffffff;
  font-weight: 500;
}

@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    height: auto;
  }

  .sidebar-nav ul {
    display: flex;
    overflow-x: auto;
    padding: 0 10px;
  }

  .sidebar-nav li {
    flex-shrink: 0;
    margin-bottom: 0;
  }

  .sidebar-nav li a {
    border-radius: 4px;
    margin: 0 4px;
    white-space: nowrap;
  }
}
</style>