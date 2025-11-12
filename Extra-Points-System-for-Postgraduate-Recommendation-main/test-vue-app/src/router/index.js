import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import ForgotPassword from '../views/ForgotPassword.vue'
import Student from '../views/Student.vue'
import Teacher from '../views/Teacher.vue'
import Admin from '../views/Admin.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/forgot-password',
    component: ForgotPassword,
    meta: { requiresAuth: false }
  },
  {
    path: '/student',
    component: Student,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/teacher',
    component: Teacher,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/admin',
    component: Admin,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  // 从localStorage直接读取认证状态，避免在路由守卫中创建store实例导致的状态不一致
  const token = localStorage.getItem('token')
  const userInfoStr = localStorage.getItem('userInfo')
  const isAuthenticated = !!token && !!userInfoStr
  let userRole = ''
  
  try {
    const userInfo = JSON.parse(userInfoStr)
    // 确保userInfo不是null再访问role属性
    userRole = userInfo?.role || ''
  } catch (e) {
    console.warn('解析用户信息失败:', e)
  }
  
  console.log('路由守卫检查:', {
    path: to.path,
    requiresAuth: to.meta.requiresAuth,
    role: to.meta.role,
    isAuthenticated,
    userRole
  })

  // 首先检查是否需要认证
  if (to.meta.requiresAuth && !isAuthenticated) {
    console.log('未认证，重定向到登录页')
    next('/login')
  } 
  // 然后检查角色权限，添加更严格的验证
  else if (to.meta.role) {
    // 确保用户角色存在且与路由要求匹配
    if (!userRole || userRole !== to.meta.role) {
      console.log('角色不匹配，当前角色:', userRole, '需要角色:', to.meta.role, '重定向到登录页')
      // 清除可能有误的认证信息
      localStorage.removeItem('userInfo')
      localStorage.removeItem('token')
      next('/login')
    } else {
      console.log('角色匹配，允许访问')
      next()
    }
  } 
  // 其他情况允许访问
  else {
    console.log('允许访问')
    next()
  }
})

export default router