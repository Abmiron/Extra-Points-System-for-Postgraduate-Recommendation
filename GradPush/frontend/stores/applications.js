import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// API基础URL
const API_BASE_URL = '/api'

// 封装fetch请求
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  
  // 检查是否是FormData请求
  const isFormData = options.body && options.body instanceof FormData
  
  // 如果是FormData请求，不需要设置Content-Type
  const defaultOptions = {
    headers: isFormData ? {} : {
      'Content-Type': 'application/json',
    },
  }

  const config = { ...defaultOptions, ...options }

  try {
    const response = await fetch(url, config)
    
    // 先读取响应体为文本
    const responseText = await response.text()
    
    if (!response.ok) {
      // 尝试解析为JSON
      let errorDetails = responseText
      try {
        const errorData = JSON.parse(responseText)
        errorDetails = JSON.stringify(errorData, null, 2)
      } catch {
        // 如果解析失败，直接使用文本
      }
      throw new Error(`API请求失败: ${response.statusText}\n详细信息: ${errorDetails}`)
    }

    // 解析为JSON并返回
    return JSON.parse(responseText)
  } catch (error) {
    console.error('API请求错误:', error)
    throw error
  }
}

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

  // 从API获取所有申请
  const fetchApplications = async (filters = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const queryParams = new URLSearchParams()
      if (filters.studentId) queryParams.append('studentId', filters.studentId)
      if (filters.studentName) queryParams.append('studentName', filters.studentName)
      if (filters.department) queryParams.append('department', filters.department)
      if (filters.major) queryParams.append('major', filters.major)
      if (filters.status) queryParams.append('status', filters.status)
      if (filters.applicationType) queryParams.append('applicationType', filters.applicationType)
      if (filters.reviewedBy) queryParams.append('reviewedBy', filters.reviewedBy)
      if (filters.reviewedStartDate) queryParams.append('reviewedStartDate', filters.reviewedStartDate)
      if (filters.reviewedEndDate) queryParams.append('reviewedEndDate', filters.reviewedEndDate)
      
      const queryString = queryParams.toString() ? `?${queryParams.toString()}` : ''
      const data = await apiRequest(`/applications${queryString}`)
      applications.value = data
      return data
    } catch (err) {
      console.error('加载申请数据失败:', err)
      error.value = '加载数据失败，请刷新页面重试'
      applications.value = []
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 从API获取单个申请详情
  const fetchApplicationById = async (applicationId) => {
    loading.value = true
    error.value = null
    
    try {
      const data = await apiRequest(`/applications/${applicationId}`)
      return data
    } catch (err) {
      console.error('加载申请详情失败:', err)
      error.value = '加载申请详情失败'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 从API获取待审核申请
  const fetchPendingApplications = async (filters = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const queryParams = new URLSearchParams()
      if (filters.department) queryParams.append('department', filters.department)
      if (filters.major) queryParams.append('major', filters.major)
      if (filters.applicationType) queryParams.append('applicationType', filters.applicationType)
      if (filters.studentId) queryParams.append('studentId', filters.studentId)
      if (filters.studentName) queryParams.append('studentName', filters.studentName)
      
      const queryString = queryParams.toString() ? `?${queryParams.toString()}` : ''
      const data = await apiRequest(`/applications/pending${queryString}`)
      // 将获取到的待审核申请保存到store中
      applications.value = data
      return data
    } catch (err) {
      console.error('加载待审核申请失败:', err)
      error.value = '加载待审核申请失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 添加新申请
  const addApplication = async (application) => {
    loading.value = true
    error.value = null
    
    try {
      // 创建FormData对象来处理文件上传
      const formData = new FormData()
      
      // 将非文件字段添加到FormData
      const applicationData = { ...application }
      // 移除files字段，单独处理
      const files = applicationData.files || []
      delete applicationData.files
      
      // 字段名转换：将前端的驼峰式命名转换为后端的下划线命名
      const fieldMapping = {
        'studentId': 'student_id',
        'studentName': 'student_name',
        'name': 'student_name', // 兼容前端使用name字段的情况
        'department': 'department',
        'major': 'major',
        'applicationType': 'application_type',
        'selfScore': 'self_score',
        'projectName': 'project_name',
        'awardDate': 'award_date',
        'awardLevel': 'award_level',
        'awardType': 'award_type',
        'academicType': 'academic_type',
        'researchType': 'research_type',
        'innovationLevel': 'innovation_level',
        'innovationRole': 'innovation_role',
        'awardGrade': 'award_grade',
        'awardCategory': 'award_category',
        'authorRankType': 'author_rank_type',
        'authorOrder': 'author_order',
        'performanceType': 'performance_type',
        'performanceLevel': 'performance_level',
        'performanceParticipation': 'performance_participation',
        'teamRole': 'team_role',
        'finalScore': 'final_score',
        'reviewComment': 'review_comment',
        'reviewedAt': 'reviewed_at',
        'reviewedBy': 'reviewed_by',
        'appliedAt': 'applied_at',
        'createdAt': 'created_at',
        'updatedAt': 'updated_at'
      }
      
      // 转换数据字段
      const transformedData = {};
      for (const [key, value] of Object.entries(applicationData)) {
        const newKey = fieldMapping[key] || key;
        transformedData[newKey] = value;
      }
      
      // 将转换后的application数据作为JSON字符串添加到FormData
      formData.append('application', JSON.stringify(transformedData))
      
      // 添加文件到FormData
      files.forEach((file, index) => {
        formData.append(`files[${index}]`, file)
      })
      
      // 发送请求
      const data = await apiRequest('/applications', {
        method: 'POST',
        body: formData
      })
      
      // 获取完整的申请数据
      const newApplication = await fetchApplicationById(data.id)
      applications.value.unshift(newApplication)
      return true
    } catch (err) {
      console.error('创建申请失败:', err)
      error.value = '创建申请失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 更新申请状态（审核）
  const updateApplicationStatus = async (applicationId, status, reviewComment, finalScore, reviewedBy) => {
    loading.value = true
    error.value = null
    
    try {
      const updatedData = {
        status,
        reviewComment,
        finalScore,
        reviewedBy
      }
      
      // 使用审核接口而不是通用更新接口，以触发自动评分逻辑
      await apiRequest(`/applications/${applicationId}/review`, {
        method: 'POST',
        body: JSON.stringify(updatedData)
      })
      
      // 更新本地状态
      const application = applications.value.find(app => app.id === applicationId)
      if (application) {
        Object.assign(application, {
          status,
          reviewComment,
          finalScore,
          reviewedAt: new Date().toISOString(),
          reviewedBy
        })
      }
      
      return true
    } catch (err) {
      console.error('更新申请状态失败:', err)
      error.value = '更新申请状态失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 批准申请
  const approveApplication = async (applicationId, finalScore, comment, reviewedBy) => {
    return await updateApplicationStatus(applicationId, 'approved', comment, finalScore, reviewedBy)
  }

  // 驳回申请
  const rejectApplication = async (applicationId, comment, reviewedBy) => {
    return await updateApplicationStatus(applicationId, 'rejected', comment, 0, reviewedBy)
  }

  // 删除申请
  const deleteApplication = async (applicationId) => {
    loading.value = true
    error.value = null
    
    try {
      await apiRequest(`/applications/${applicationId}`, {
        method: 'DELETE'
      })
      
      // 更新本地状态
      const index = applications.value.findIndex(app => app.id === applicationId)
      if (index !== -1) {
        applications.value.splice(index, 1)
      }
      
      return true
    } catch (err) {
      console.error('删除申请失败:', err)
      error.value = '删除申请失败'
      return false
    } finally {
      loading.value = false
    }
  }
  
  // 更新申请信息
  const updateApplication = async (applicationId, applicationData) => {
    loading.value = true
    error.value = null
    
    try {
      // 字段名转换：将前端的驼峰式命名转换为后端的下划线命名
      const fieldMapping = {
        'studentId': 'student_id',
        'studentName': 'student_name',
        'gender': 'gender',
        'grade': 'grade',
        'department': 'department',
        'major': 'major',
        'applicationType': 'application_type',
        'projectName': 'project_name',
        'selfScore': 'self_score',
        'finalScore': 'final_score',
        'reviewComment': 'review_comment'
      }
      
      // 转换数据字段
      const transformedData = {};
      for (const [key, value] of Object.entries(applicationData)) {
        const newKey = fieldMapping[key] || key;
        transformedData[newKey] = value;
      }
      
      await apiRequest(`/applications/${applicationId}`, {
        method: 'PUT',
        body: JSON.stringify(transformedData)
      })
      
      // 更新本地状态
      const application = applications.value.find(app => app.id === applicationId)
      if (application) {
        Object.assign(application, applicationData)
      }
      
      return true
    } catch (err) {
      console.error('更新申请失败:', err)
      error.value = '更新申请失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 获取单个申请详情（从本地状态或API）
  const getApplicationById = async (applicationId) => {
    // 先从本地状态查找
    const localApp = applications.value.find(app => app.id === applicationId)
    if (localApp) {
      return localApp
    }
    
    // 如果本地没有，从API获取
    return await fetchApplicationById(applicationId)
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
      
      // 按学生学号筛选（模糊匹配）
      if (filters.studentId) {
        const searchTerm = filters.studentId.toLowerCase()
        const studentId = (application.studentId || '').toLowerCase()
        if (!studentId.includes(searchTerm)) {
          return false
        }
      }
      
      // 按学生姓名筛选（模糊匹配）
      if (filters.studentName) {
        const searchTerm = filters.studentName.toLowerCase()
        const studentName = (application.studentName || '').toLowerCase()
        if (!studentName.includes(searchTerm)) {
          return false
        }
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
      
      // 按审核人筛选（模糊匹配）
      if (filters.reviewedBy && filters.reviewedBy !== 'all') {
        const searchTerm = filters.reviewedBy.toLowerCase()
        const reviewedBy = (application.reviewedBy || '').toLowerCase()
        if (!reviewedBy.includes(searchTerm)) {
          return false
        }
      }
      
      // 只显示我审核的
      if (filters.myReviewsOnly) {
        if (application.reviewedBy !== filters.myReviewsOnly) {
          return false
        }
      }
      
      return true
    })
  }

  // 获取学生加分统计数据
  const fetchStatistics = async (studentId) => {
    loading.value = true
    error.value = null
    
    try {
      const data = await apiRequest(`/applications/statistics?studentId=${studentId}`)
      return data
    } catch (err) {
      console.error('加载加分统计数据失败:', err)
      error.value = '加载加分统计数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取学生推免成绩排名
  const fetchStudentsRanking = async (filters = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const queryParams = new URLSearchParams()
      if (filters.department && filters.department !== 'all') queryParams.append('department', filters.department)
      if (filters.major && filters.major !== 'all') queryParams.append('major', filters.major)
      
      const queryString = queryParams.toString() ? `?${queryParams.toString()}` : ''
      const data = await apiRequest(`/applications/students-ranking${queryString}`)
      return data
    } catch (err) {
      console.error('加载学生排名数据失败:', err)
      error.value = '加载学生排名数据失败'
      throw err
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
    fetchApplications,
    fetchApplicationById,
    fetchPendingApplications,
    addApplication,
    updateApplicationStatus,
    updateApplication,
    deleteApplication,
    getApplicationById,
    filterApplications,
    approveApplication,
    rejectApplication,
    fetchStatistics,
    fetchStudentsRanking
  }
})