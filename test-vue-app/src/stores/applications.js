import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { generateMockApplications, getPendingApplications, getReviewedApplications } from '../utils/mockData'

export const useApplicationsStore = defineStore('applications', () => {
  // 状态定义
  const applications = ref([])
  const loading = ref(false)
  const error = ref(null)

  // 计算属性
  const pendingApplications = computed(() => {
    return applications.value.filter(app => app.status === 'pending')
  })

  const reviewedApplications = computed(() => {
    return applications.value.filter(app => app.status === 'approved' || app.status === 'rejected')
  })

  const totalApplications = computed(() => applications.value.length)

  // 初始化模拟数据
  const initializeMockData = () => {
    try {
      // 为每个mock申请添加学生信息（与显示组件保持一致）
      const storedApplications = localStorage.getItem('studentApplications')
      if (!storedApplications) {
        const mockApplications = generateMockApplications()
        // 为每个mock申请添加学生信息
        const enhancedApps = mockApplications.map(app => ({
          ...app,
          studentName: app.studentName || app.name || '模拟学生',
          studentId: app.studentId || '2020318000',
          department: app.department || 'cs',
          major: app.major || 'cs'
        }))
        localStorage.setItem('studentApplications', JSON.stringify(enhancedApps))
        console.log('模拟数据已初始化到本地存储')
      }
    } catch (error) {
      console.error('Error initializing mock data:', error)
    }
    loadApplications() // 初始化后立即加载数据
  }
  
  // 从本地存储加载申请数据
  const loadApplications = () => {
    loading.value = true
    error.value = null
    
    try {
      const storedApplications = localStorage.getItem('studentApplications')
      applications.value = storedApplications ? JSON.parse(storedApplications) : []
    } catch (err) {
      console.error('加载申请数据失败:', err)
      error.value = '加载数据失败，请刷新页面重试'
      applications.value = []
    } finally {
      loading.value = false
    }
  }

  // 保存申请数据到本地存储
  const saveApplications = () => {
    try {
      localStorage.setItem('studentApplications', JSON.stringify(applications.value))
      return true
    } catch (err) {
      console.error('保存申请数据失败:', err)
      error.value = '保存数据失败'
      return false
    }
  }

  // 添加新申请
  const addApplication = (application) => {
    const newApplication = {
      ...application,
      id: `app${Date.now()}`,
      appliedAt: new Date().toISOString(),
      status: 'pending'
    }
    
    applications.value.unshift(newApplication)
    return saveApplications()
  }

  // 更新申请状态（审核）
  const updateApplicationStatus = (applicationId, status, reviewComment, finalScore, reviewedBy) => {
    const application = applications.value.find(app => app.id === applicationId)
    if (application) {
      application.status = status
      application.reviewComment = reviewComment
      application.finalScore = finalScore
      application.reviewedAt = new Date().toISOString()
      application.reviewedBy = reviewedBy
      return saveApplications()
    }
    return false
  }

  // 删除申请
  const deleteApplication = (applicationId) => {
    const index = applications.value.findIndex(app => app.id === applicationId)
    if (index !== -1) {
      applications.value.splice(index, 1)
      return saveApplications()
    }
    return false
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
    initializeMockData,
    loadApplications,
    addApplication,
    updateApplicationStatus,
    deleteApplication,
    getApplicationById,
    filterApplications
  }
})