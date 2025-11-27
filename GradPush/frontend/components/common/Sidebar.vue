<template>
  <div class="sidebar-container">
    <aside class="sidebar" :class="{ 'sidebar-collapsed': !isSidebarOpen }">
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
    <button class="sidebar-toggle-btn" @click="toggleSidebar" aria-label="展开/收起侧边栏">
      <font-awesome-icon :icon="isSidebarOpen ? ['fas', 'angle-left'] : ['fas', 'angle-right']" />
    </button>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useAuthStore } from '../../stores/auth'

const props = defineProps({
  activePage: String,
  userInfo: Object,
  userType: {
    type: String,
    default: 'student'
  }
})

const emit = defineEmits(['page-change', 'sidebar-toggle'])

const authStore = useAuthStore()

const userAvatar = computed(() => authStore.userAvatar)

// 侧边栏展开/收起状态
const isSidebarOpen = ref(true)

// 切换侧边栏展开/收起状态
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
  emit('sidebar-toggle', isSidebarOpen.value)
}

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
    { key: 'profile', icon: ['fas', 'user'], title: '个人信息' }
  ],
  admin: [
    { key: 'user-management', icon: ['fas', 'users'], title: '用户管理' },
    { key: 'faculty-management', icon: ['fas', 'university'], title: '学院管理' },
    { key: 'data-management', icon: ['fas', 'database'], title: '申请管理' },
    { key: 'score-management', icon: ['fas', 'user-graduate'], title: '成绩管理' },
    { key: 'rule-management', icon: ['fas', 'ruler'], title: '规则管理' },
    { key: 'statistics-report', icon: ['fas', 'chart-pie'], title: '统计报表' },
    { key: 'system-settings', icon: ['fas', 'cog'], title: '系统设置' },
    { key: 'profile', icon: ['fas', 'user'], title: '个人信息' }
  ]
}

const menuItems = computed(() => menuConfig[props.userType] || [])
</script>

<style scoped>
.sidebar-container {
  display: flex;
  align-items: stretch;
  position: relative;
}

.sidebar {
  width: 240px;
  background-color: #ffffff;
  border-right: 1px solid #e1e4e8;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 3px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
  overflow-y: auto;
  transition: width 0.3s ease, opacity 0.3s ease, transform 0.3s ease;
}

.sidebar-nav li span {
  transition: opacity 0.2s ease;
}

.sidebar-toggle-btn {
  position: absolute;
  right: -18px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 60px;
  background-color: #ffffff;
  color: #0057b1;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.sidebar-toggle-btn svg {
  font-size: 16px;
  transition: transform 0.3s ease;
}

.sidebar-toggle-btn:hover {
  background-color: #0057b1;
  color:#ffffff;
}

.sidebar-collapsed {
  width: 0;
  padding: 20px 0;
  overflow: hidden;
  opacity: 0;
  transform: translateX(-10px);
}

/* 为用户信息区域添加过渡效果，避免收起时突然上移 */
.user-info {
  transition: all 0.3s ease;
}

/* 为导航项添加位置过渡效果 */
.sidebar-nav li {
  transition: all 0.3s ease;
}

.sidebar-collapsed .user-details div,
.sidebar-collapsed .sidebar-nav li span {
  opacity: 0;
  transform: translateX(-10px);
  /* 不使用display: none，以保持过渡效果 */
  visibility: hidden;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 0 20px 20px;
  border-bottom: 1px solid #e1e4e8;
  margin-bottom: 20px;
  /* 固定用户信息区域高度，防止展开时高度变化 */
  height: 80px;
  overflow: hidden;
}

.user-info .user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  margin-right: 12px;
  object-fit: cover;
  /* 添加抗锯齿效果 */
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
  /* 添加轻微阴影增强视觉效果 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  /* 确保用户详情文本即使透明度变化也保持占位 */
  min-height: 50px;
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
  transition: all 0.3s ease;
  /* 固定导航项高度，防止展开时高度变化 */
  height: 44px;
}

.sidebar-nav li a {
  height: 100%;
  /* 确保文本内容区域固定，不影响高度计算 */
  position: relative;
}

/* 为文本设置绝对定位，确保即使透明度变化也不会影响高度 */
.sidebar-nav li span {
  /* 改进过渡效果，添加transform使其平滑滑出 */
  transition: opacity 0.3s ease 0.1s, transform 0.3s ease 0.1s;
  position: relative;
  display: inline-block;
  /* 确保展开状态下有正确的transform值 */
  transform: translateX(0);
  visibility: visible;
}

/* 为用户详情文本也添加平滑过渡效果 */
.user-details div {
  transition: opacity 0.3s ease 0.1s, transform 0.3s ease 0.1s;
  position: relative;
  /* 确保展开状态下有正确的transform值 */
  transform: translateX(0);
  visibility: visible;
}

.sidebar-collapsed .sidebar-nav li {
  /* 收起状态保持相同高度 */
  height: 44px;
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