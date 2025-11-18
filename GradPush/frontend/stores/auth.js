import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const role = ref(null)
  const isAuthenticated = ref(false)

  const userName = computed(() => {
    return user.value?.name || '张三'
  })
  const userAvatar = computed(() => {
    if (!user.value?.avatar || user.value.avatar === '') {
      // 默认头像在前端public目录下，直接返回相对路径
      return '/images/default-avatar.jpg'
    }
    // 检查头像URL是否已经包含完整路径
    if (user.value.avatar.startsWith('http://') || user.value.avatar.startsWith('https://')) {
      return user.value.avatar
    }
    // 检查是否是本地默认头像路径
    if (user.value.avatar.startsWith('/images/')) {
      return user.value.avatar
    }
    // 添加服务器地址前缀
    return `http://localhost:5001${user.value.avatar}`
  })

  // 获取当前用户信息
  const getCurrentUser = async () => {
    try {
      // 使用当前已有的username调用API
      const username = user.value?.username
      if (!username) {
        throw new Error('用户名不可用')
      }
      const userData = await api.getCurrentUser(username)
      user.value = userData
      role.value = userData.role
      isAuthenticated.value = true
      localStorage.setItem('user', JSON.stringify(userData))
      return userData
    } catch (error) {
      console.error('获取当前用户失败:', error)
      // 失败时不抛出错误，继续使用当前数据
      return user.value
    }
  }

  const updateUserInfo = async (userData) => {
    try {
      const updatedUser = await api.updateUserInfo(userData)
      user.value = updatedUser
      localStorage.setItem('user', JSON.stringify(updatedUser))
      return updatedUser
    } catch (error) {
      console.error('更新用户信息失败:', error)
      throw error
    }
  }

  // 登录
  const login = async (username, password) => {
    try {
      const data = await api.apiRequest('/login', 'POST', { username, password })
      user.value = data.user
      role.value = data.user.role
      isAuthenticated.value = true
      localStorage.setItem('user', JSON.stringify(data.user))
      return data.user
    } catch (error) {
      console.error('登录错误:', error)
      throw error
    }
  }

  // 注册
  const register = async (userData) => {
    try {
      const message = await api.apiRequest('/register', 'POST', userData)
      return message
    } catch (error) {
      console.error('注册错误:', error)
      throw error
    }
  }

  // 密码重置
  const resetPassword = async (username, newPassword) => {
    try {
      const message = await api.apiRequest('/reset-password', 'POST', { username, newPassword })
      return message
    } catch (error) {
      console.error('密码重置错误:', error)
      throw error
    }
  }

  const logout = () => {
    user.value = null
    role.value = null
    isAuthenticated.value = false
    localStorage.removeItem('user')
  }

  const initialize = async () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      const userData = JSON.parse(savedUser)
      
      // 验证用户数据是否有效，防止username为"student"等错误值
      if (userData.username && userData.username !== 'student') {
        user.value = userData
        role.value = userData.role
        isAuthenticated.value = true
        
        // 初始化后尝试从API获取最新的用户信息
        try {
          await getCurrentUser()
        } catch (error) {
          console.error('初始化时获取用户信息失败:', error)
          // 失败时继续使用localStorage中的数据
        }
      } else {
        // 如果用户数据无效，清除localStorage并重置状态
        localStorage.removeItem('user')
        user.value = null
        role.value = null
        isAuthenticated.value = false
        console.log('检测到无效的用户数据，已清除')
      }
    }
  }

  return {
    user,
    role,
    isAuthenticated,
    userName,
    userAvatar,
    login,
    register,
    resetPassword,
    logout,
    initialize,
    getCurrentUser,
    updateUserInfo
  }
})