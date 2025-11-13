import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const role = ref(null)
  const isAuthenticated = ref(false)

  const userName = computed(() => {
    // 多重检查，确保能正确获取用户姓名
    // 1. 检查user.value?.name（标准字段）
    // 2. 检查user对象中的其他可能包含姓名的字段
    // 3. 提供默认值作为最后的保障
    return user.value?.name || (typeof user.value === 'object' ? Object.values(user.value).find(val => typeof val === 'string' && val.length > 0) : '') || '张三'
  })
  const userAvatar = computed(() => user.value?.avatar || '/images/default-avatar.jpg')

  const login = (userData) => {
    user.value = userData
    role.value = userData.role
    isAuthenticated.value = true
    localStorage.setItem('user', JSON.stringify(userData))
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
      login(userData)
    }
  }

  return {
    user,
    role,
    isAuthenticated,
    userName,
    userAvatar,
    login,
    logout,
    initialize
  }
})