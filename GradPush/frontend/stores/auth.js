import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const API_BASE_URL = 'http://localhost:5001/api'

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
    if (!user.value) return null
    
    try {
      const response = await fetch(`${API_BASE_URL}/user/${user.value.username}`)
      
      if (!response.ok) {
        throw new Error('获取用户信息失败')
      }
      
      const data = await response.json()
      user.value = data.user
      role.value = data.user.role
      isAuthenticated.value = true
      localStorage.setItem('user', JSON.stringify(data.user)) // 保留localStorage作为缓存
      
      return data.user
    } catch (error) {
      console.error('获取用户信息错误:', error)
      return user.value // 出错时返回当前缓存的用户信息
    }
  }

  // 更新用户信息
  const updateUserInfo = (userInfo) => {
    user.value = userInfo
    role.value = userInfo.role
    isAuthenticated.value = true
    localStorage.setItem('user', JSON.stringify(userInfo)) // 保留localStorage作为缓存
    return '用户信息已更新'
  }

  // 登录
  const login = async (username, password) => {
    try {
      // 执行正常的登录流程
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || '登录失败')
      }
      
      const data = await response.json()
      user.value = data.user
      role.value = data.user.role
      isAuthenticated.value = true
      localStorage.setItem('user', JSON.stringify(data.user)) // 保留localStorage作为缓存
      
      return data.message
    } catch (error) {
      console.error('登录错误:', error)
      throw error
    }
  }

  // 注册
  const register = async (userData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || '注册失败')
      }
      
      const data = await response.json()
      return data.message
    } catch (error) {
      console.error('注册错误:', error)
      throw error
    }
  }

  // 密码重置
  const resetPassword = async (username, newPassword) => {
    try {
      const response = await fetch(`${API_BASE_URL}/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, newPassword })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || '密码重置失败')
      }
      
      const data = await response.json()
      return data.message
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