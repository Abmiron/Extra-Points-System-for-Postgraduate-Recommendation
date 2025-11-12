import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'
import { useAuthStore } from './auth'

export const useApplicationsStore = defineStore('applications', () => {
  // 状态定义
  const applications = ref([])
  const loading = ref(false)
  const error = ref(null)
  const authStore = useAuthStore()
  
  // 模拟申请数据
  const mockApplications = [
    {
      id: 1,
      studentId: '2021001',
      studentName: '张三',
      faculty: '信息学院',
      major: '计算机科学与技术',
      applicationType: '科研竞赛',
      eventName: 'ACM程序设计竞赛',
      eventLevel: '国家级',
      awardLevel: '一等奖',
      score: 20,
      submissionDate: '2024-01-15',
      status: 'pending',
      reviewComments: '',
      reviewer: null,
      reviewDate: null
    },
    {
      id: 2,
      studentId: '2021002',
      studentName: '李四',
      faculty: '信息学院',
      major: '软件工程',
      applicationType: '学术论文',
      eventName: '计算机科学学术研讨会',
      eventLevel: '省级',
      awardLevel: '发表',
      score: 15,
      submissionDate: '2024-01-10',
      status: 'approved',
      reviewComments: '符合加分条件',
      reviewer: '王老师',
      reviewDate: '2024-01-12'
    }
  ]

  // 计算属性
  const pendingApplications = computed(() => {
    return applications.value.filter(app => app.status === 'pending')
  })

  const reviewedApplications = computed(() => {
    return applications.value.filter(app => app.status === 'approved' || app.status === 'rejected')
  })

  const totalApplications = computed(() => applications.value.length)

  // 从API加载申请数据
  const loadApplications = async (params = {}) => {
    loading.value = true
    error.value = null
    
    try {
      // 检查是否使用模拟数据模式（模拟令牌或启用了模拟数据）
      const token = localStorage.getItem('token')
      const isMockMode = token && token.includes('mock_')
      
      if (isMockMode) {
        console.log('使用模拟数据模式加载申请数据')
        // 根据用户角色返回适当的模拟数据
        if (authStore.role === 'student') {
            // 学生只能看到自己的申请，确保至少返回一些模拟数据
            const userStudentId = authStore.user?.studentId
            const filteredApps = userStudentId ? 
              mockApplications.filter(app => app.studentId === userStudentId) : 
              []
            
            // 如果没有匹配的数据，返回默认的模拟申请
            applications.value = filteredApps.length > 0 ? filteredApps : mockApplications.slice(0, 1)
          } else {
            // 教师和管理员可以看到所有申请
            applications.value = mockApplications
          }
        return applications.value
      }
      
      // 正常模式：调用API
      const response = await api.application.list(params)
      applications.value = response.data || []
      return applications.value
    } catch (err) {
      console.error('加载申请数据失败:', err)
      error.value = '加载数据失败，请稍后重试'
      
      // 即使API调用失败，也提供模拟数据作为备选
        const token = localStorage.getItem('token')
        const isMockMode = token && token.includes('mock_')
        if (isMockMode) {
          console.log('API调用失败，使用模拟数据作为备选')
          if (authStore.role === 'student') {
            // 学生只能看到自己的申请，确保至少返回一些模拟数据
            const userStudentId = authStore.user?.studentId
            const filteredApps = userStudentId ? 
              mockApplications.filter(app => app.studentId === userStudentId) : 
              []
            
            // 如果没有匹配的数据，返回默认的模拟申请
            applications.value = filteredApps.length > 0 ? filteredApps : mockApplications.slice(0, 1)
          } else {
            // 教师和管理员可以看到所有申请
            applications.value = mockApplications
          }
        } else {
          applications.value = []
        }
      return applications.value
    } finally {
      loading.value = false
    }
  }

  // 添加新申请
  const addApplication = async (applicationData) => {
    loading.value = true
    error.value = null
    
    try {
      const newApplication = await api.application.create(applicationData)
      applications.value.unshift(newApplication)
      return newApplication
    } catch (err) {
      console.error('创建申请失败:', err)
      error.value = '创建申请失败，请稍后重试'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新申请
  const updateApplication = async (id, applicationData) => {
    loading.value = true
    error.value = null
    
    try {
      const updatedApplication = await api.application.update(id, applicationData)
      const index = applications.value.findIndex(app => app.id === id)
      if (index !== -1) {
        applications.value[index] = updatedApplication
      }
      return updatedApplication
    } catch (err) {
      console.error('更新申请失败:', err)
      error.value = '更新申请失败，请稍后重试'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 提交申请
  const submitApplication = async (id) => {
    loading.value = true
    error.value = null
    
    try {
      await api.application.submit(id)
      const index = applications.value.findIndex(app => app.id === id)
      if (index !== -1) {
        applications.value[index].status = 'pending'
      }
      return true
    } catch (err) {
      console.error('提交申请失败:', err)
      error.value = '提交申请失败，请稍后重试'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除申请
  const deleteApplication = async (id) => {
    loading.value = true
    error.value = null
    
    try {
      await api.application.delete(id)
      applications.value = applications.value.filter(app => app.id !== id)
      return true
    } catch (err) {
      console.error('删除申请失败:', err)
      error.value = '删除申请失败，请稍后重试'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新申请状态（审核）
  const updateApplicationStatus = async (applicationId, status, reviewComment, finalScore) => {
    loading.value = true
    error.value = null
    
    try {
      let response
      if (status === 'approved') {
        response = await api.review.approve(applicationId, { comment: reviewComment, finalScore })
      } else if (status === 'rejected') {
        response = await api.review.reject(applicationId, { comment: reviewComment })
      }
      
      const index = applications.value.findIndex(app => app.id === applicationId)
      if (index !== -1) {
        applications.value[index] = response
      }
      
      return true
    } catch (err) {
      console.error('更新申请状态失败:', err)
      error.value = '审核操作失败，请稍后重试'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取单个申请详情
  const getApplicationById = (applicationId) => {
    return applications.value.find(app => app.id === applicationId)
  }

  // 过滤申请（按多种条件）
  const filterApplications = (filters = {}) => {
    return applications.value.filter(application => {
      // 按部门筛选
      if (filters.department && filters.department !== 'all' && application.department !== filters.department) {
        return false
      }
      
      // 按专业筛选
      if (filters.major && filters.major !== 'all' && application.major !== filters.major) {
        return false
      }
      
      // 按类型筛选
      if (filters.type && filters.type !== 'all' && application.applicationType !== filters.type) {
        return false
      }
      
      // 按时间段筛选
      if (filters.startDate) {
        const applicationDate = new Date(application.appliedAt)
        const startDate = new Date(filters.startDate)
        if (applicationDate < startDate) {
          return false
        }
      }
      
      if (filters.endDate) {
        const applicationDate = new Date(application.appliedAt)
        const endDate = new Date(filters.endDate)
        endDate.setHours(23, 59, 59, 999) // 设置为当天结束时间
        if (applicationDate > endDate) {
          return false
        }
      }
      
      return true
    })
  }

  // 获取待审核的申请
  const loadPendingApplications = async (params = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.review.pending(params)
      return response.data || []
    } catch (err) {
      console.error('加载待审核申请失败:', err)
      error.value = '加载数据失败，请稍后重试'
      return []
    } finally {
      loading.value = false
    }
  }

  // 获取审核历史
  const loadReviewedApplications = async (params = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.review.history(params)
      return response.data || []
    } catch (err) {
      console.error('加载审核历史失败:', err)
      error.value = '加载数据失败，请稍后重试'
      return []
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    applications,
    loading,
    error,
    
    // 计算属性
    pendingApplications,
    reviewedApplications,
    totalApplications,
    
    // 方法
    loadApplications,
    addApplication,
    updateApplication,
    submitApplication,
    deleteApplication,
    updateApplicationStatus,
    getApplicationById,
    filterApplications,
    loadPendingApplications,
    loadReviewedApplications
  }
})