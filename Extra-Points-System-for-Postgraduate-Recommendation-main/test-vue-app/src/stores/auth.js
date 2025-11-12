import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'
import { validateLogin } from '../utils/mockData'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const role = computed(() => user.value?.role || '')
  const userName = computed(() => {
    // 添加日志记录以调试姓名显示问题
    console.log('计算userName - user对象:', user.value);
    console.log('计算userName - 检查字段: name=', user.value?.name, 'studentName=', user.value?.studentName);
    
    // 尝试多种可能的名称字段
    const nameValue = user.value?.name || 
                     user.value?.studentName || 
                     user.value?.username || 
                     '';
    
    console.log('计算userName - 最终值:', nameValue);
    return nameValue;
  })
  const userAvatar = computed(() => user.value?.avatar || '/images/default-avatar.jpg')
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const loading = ref(false)
  const error = ref(null)

  // 初始化函数 - 检查本地存储中的令牌并验证
  const initialize = async () => {
    console.log('开始初始化authStore...')
    const storedToken = localStorage.getItem('token')
    console.log('发现存储的token:', !!storedToken)
    
    // 先尝试从localStorage直接获取userInfo
    const storedUserInfo = localStorage.getItem('userInfo')
    if (storedUserInfo) {
      try {
        const parsedUser = JSON.parse(storedUserInfo)
        console.log('从localStorage获取userInfo:', parsedUser)
        user.value = { ...parsedUser }
        
        // 确保有角色信息
        if (!user.value.role) {
          const username = user.value.username || user.value.userName || ''
          if (username === 'admin') {
            user.value.role = 'admin'
            user.value.roleName = '系统管理员'
          } else if (username === 'teacher') {
            user.value.role = 'teacher'
            user.value.roleName = '审核员'
          } else {
            user.value.role = 'student'
            user.value.roleName = '学生'
          }
        } else if (!user.value.roleName) {
          // 根据已有角色设置roleName
          if (user.value.role === 'admin') {
            user.value.roleName = '系统管理员'
          } else if (user.value.role === 'teacher') {
            user.value.roleName = '审核员'
          } else if (user.value.role === 'student') {
            user.value.roleName = '学生'
          }
        }
        
        // 确保有名称信息
        if (!user.value.name && !user.value.studentName && user.value.username) {
          console.log('用户对象缺少名称字段，使用username作为备选:', user.value.username)
          user.value.name = user.value.username
        }
        
        console.log('初始化后的user对象:', user.value)
        return
      } catch (parseErr) {
        console.error('解析localStorage中的userInfo失败:', parseErr)
      }
    }
    
    if (storedToken) {
      token.value = storedToken
      try {
        // 调用API获取用户信息，验证令牌有效性
        console.log('调用API获取用户信息...')
        const userInfo = await api.user.getInfo()
        console.log('API返回的用户信息:', userInfo)
        user.value = { ...userInfo } // 创建新对象避免引用问题
        
        // 确保有角色信息 - 修复所有学生账号显示为管理员的问题
        if (!user.value.role) {
          // 从用户信息中尝试获取用户名
          const username = user.value.username || user.value.userName || ''
          // 根据用户名推断角色
          if (username === 'admin') {
            user.value.role = 'admin'
            user.value.roleName = '系统管理员'
          } else if (username === 'teacher') {
            user.value.role = 'teacher'
            user.value.roleName = '审核员'
          } else {
            user.value.role = 'student'
            user.value.roleName = '学生'
          }
        } else if (!user.value.roleName) {
          // 根据已有角色设置roleName
          if (user.value.role === 'admin') {
            user.value.roleName = '系统管理员'
          } else if (user.value.role === 'teacher') {
            user.value.roleName = '审核员'
          } else if (user.value.role === 'student') {
            user.value.roleName = '学生'
          }
        }
        
        // 确保有名称信息
        if (!user.value.name && !user.value.studentName && user.value.username) {
          console.log('用户对象缺少名称字段，使用username作为备选:', user.value.username)
          user.value.name = user.value.username
        }
        
        localStorage.setItem('userInfo', JSON.stringify(user.value))
        console.log('初始化完成，user对象:', user.value)
      } catch (err) {
        console.error('验证令牌失败:', err)
        // 令牌无效，清除状态
        logout()
      }
    }
  }

  // 登录函数
  const login = async (credentials) => {
    loading.value = true
    error.value = null
    
    try {
      // 确保credentials是一个对象
      const loginData = typeof credentials === 'object' ? credentials : { username: credentials, password: '' }
      
      // 首先尝试使用真实的登录API
      try {
        const response = await api.auth.login(loginData)
        
        // 保存令牌（兼容不同格式的响应）
        const tokenValue = response.token || response.data?.token || ''
        if (tokenValue) {
          token.value = tokenValue
          localStorage.setItem('token', tokenValue)
        }
        
        // 处理用户信息（兼容响应中直接返回用户信息的情况）
        if (response.user || response.data?.user) {
          user.value = { ...(response.user || response.data.user) } // 创建新对象避免引用问题
          
          // 确保有角色信息 - 修复所有学生账号显示为管理员的问题
          if (!user.value.role) {
            // 根据用户名推断角色
            if (loginData.username === 'admin') {
              user.value.role = 'admin'
              user.value.roleName = '系统管理员'
            } else if (loginData.username === 'teacher') {
              user.value.role = 'teacher'
              user.value.roleName = '审核员'
            } else {
              user.value.role = 'student'
              user.value.roleName = '学生'
            }
          } else if (!user.value.roleName) {
            // 根据已有角色设置roleName
            if (user.value.role === 'admin') {
              user.value.roleName = '系统管理员'
            } else if (user.value.role === 'teacher') {
              user.value.roleName = '审核员'
            } else if (user.value.role === 'student') {
              user.value.roleName = '学生'
            }
          }
          
          localStorage.setItem('userInfo', JSON.stringify(user.value))
        } else {
          // 尝试单独获取用户信息
          try {
            const userInfo = await api.user.getInfo()
            user.value = { ...userInfo } // 创建新对象避免引用问题
            
            // 确保有角色信息 - 修复所有学生账号显示为管理员的问题
            if (!user.value.role) {
              // 根据用户名推断角色
              if (loginData.username === 'admin') {
                user.value.role = 'admin'
                user.value.roleName = '系统管理员'
              } else if (loginData.username === 'teacher') {
                user.value.role = 'teacher'
                user.value.roleName = '审核员'
              } else {
                user.value.role = 'student'
                user.value.roleName = '学生'
              }
            } else if (!user.value.roleName) {
              // 根据已有角色设置roleName
              if (user.value.role === 'admin') {
                user.value.roleName = '系统管理员'
              } else if (user.value.role === 'teacher') {
                user.value.roleName = '审核员'
              } else if (user.value.role === 'student') {
                user.value.roleName = '学生'
              }
            }
            
            localStorage.setItem('userInfo', JSON.stringify(user.value))
          } catch (infoErr) {
            console.warn('获取用户信息失败，但登录成功:', infoErr)
            // 即使获取用户信息失败，也要确保有角色信息
            if (!user.value) {
              // 如果user.value为null或undefined，初始化一个新对象
              user.value = {}
            }
            if (!user.value.role) {
              if (loginData.username === 'admin') {
                user.value.role = 'admin'
                user.value.roleName = '系统管理员'
              } else if (loginData.username === 'teacher') {
                user.value.role = 'teacher'
                user.value.roleName = '审核员'
              } else {
                user.value.role = 'student'
                user.value.roleName = '学生'
              }
              localStorage.setItem('userInfo', JSON.stringify(user.value))
            }
          }
        }
        
        console.log('使用真实API登录成功', '角色:', user.value?.role)
        return true
      } catch (apiErr) {
        console.warn('真实API登录失败，尝试使用模拟登录:', apiErr)
        
        // 如果真实API失败，尝试使用模拟登录作为备选方案
        console.log('尝试模拟登录，用户名:', loginData.username)
        const userInfo = validateLogin(loginData.username, loginData.password)
        
        if (userInfo) {
          // 确保用户信息包含status字段
          if (!userInfo.hasOwnProperty('status')) {
            userInfo.status = 'active' // 默认设置为活跃状态
          }
          
          // 模拟登录成功，设置用户信息
          user.value = { ...userInfo } // 创建新对象避免引用问题
          localStorage.setItem('userInfo', JSON.stringify(user.value))
          
          // 确保有角色信息
          if (!user.value.role) {
            // 根据用户名推断角色
            if (loginData.username === 'admin') {
              user.value.role = 'admin'
              user.value.roleName = '系统管理员'
            } else if (loginData.username === 'teacher') {
              user.value.role = 'teacher'
              user.value.roleName = '审核员'
            } else {
              user.value.role = 'student'
              user.value.roleName = '学生'
            }
          } else if (!user.value.roleName) {
            // 根据已有角色设置roleName
            if (user.value.role === 'admin') {
              user.value.roleName = '系统管理员'
            } else if (user.value.role === 'teacher') {
              user.value.roleName = '审核员'
            } else if (user.value.role === 'student') {
              user.value.roleName = '学生'
            }
          }
          
          // 生成模拟令牌（实际项目中应该由后端生成）
          const mockToken = `mock_${Date.now()}`
          token.value = mockToken
          localStorage.setItem('token', mockToken)
          
          console.log('使用模拟登录成功，角色:', user.value.role, '用户信息:', user.value)
          return true
        } else {
          // 模拟登录也失败，抛出原始错误
          console.error('模拟登录失败，用户名或密码错误')
          throw new Error('用户名或密码错误')
        }
      }
    } catch (err) {
      console.error('登录失败:', err)
      error.value = err.message || '登录失败，请检查用户名和密码'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 登出函数
  const logout = async () => {
    try {
      // 尝试调用登出API
      await api.auth.logout()
    } catch (err) {
      console.error('登出API调用失败，但仍清除本地状态:', err)
    } finally {
      // 清除状态
      token.value = ''
      user.value = null
      // 清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    }
  }

  return {
    token,
    user,
    role,
    userName,
    userAvatar,
    loading,
    error,
    initialize,
    login,
    logout
  }
})