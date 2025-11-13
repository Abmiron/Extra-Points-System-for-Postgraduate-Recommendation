import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const API_BASE_URL = 'http://localhost:5000/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const role = ref(null)
  const isAuthenticated = ref(false)

  const userName = computed(() => {
    return user.value?.name || '张三'
  })
  const userAvatar = computed(() => user.value?.avatar || '/images/default-avatar.jpg')

  // 登录
  const login = async (username, password) => {
    try {
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
      localStorage.setItem('user', JSON.stringify(data.user))
      
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

  const initialize = () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      const userData = JSON.parse(savedUser)
      user.value = userData
      role.value = userData.role
      isAuthenticated.value = true
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
    initialize
  }
})