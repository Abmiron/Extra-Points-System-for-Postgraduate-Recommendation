import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const role = ref(null)
  const isAuthenticated = ref(false)
  
  const userName = computed(() => user.value?.name || '')
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