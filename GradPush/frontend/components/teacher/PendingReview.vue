<template>
  <div class="page-content">
    <div class="page-title">
      <span>待审核申请</span>
    </div>

    <!-- 筛选区域 -->
    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">学号:</span>
        <input type="text" class="form-control small" v-model="filters.studentId" placeholder="请输入学号" @input="filterApplications">
      </div>
      <div class="filter-group">
        <span class="filter-label">姓名:</span>
        <input type="text" class="form-control small" v-model="filters.studentName" placeholder="请输入姓名" @input="filterApplications">
      </div>
      <div class="filter-group">
        <span class="filter-label">学院:</span>
        <select v-model="filters.faculty" @change="filterApplications">
          <option value="all">全部</option>
          <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.id">
            {{ faculty.name }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">所在系:</span>
        <select v-model="filters.department" @change="filterApplications">
          <option value="all">全部</option>
          <option v-for="department in departments" :key="department.id" :value="department.name">
            {{ department.name }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">专业:</span>
        <select v-model="filters.major" @change="filterApplications">
          <option value="all">全部</option>
          <option v-for="major in majors" :key="major.id" :value="major.name">
            {{ major.name }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">类型:</span>
        <select v-model="filters.type" @change="filterApplications">
          <option value="all">全部</option>
          <option value="academic">学术专长</option>
          <option value="comprehensive">综合表现</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">申请时间:</span>
        <input type="date" class="form-control small" v-model="filters.startDate" @change="filterApplications">
        至 <input type="date" class="form-control small" v-model="filters.endDate" @change="filterApplications">
      </div>
      <button class="btn btn-outline" @click="clearFilters">清空筛选</button>
    </div>

    <!-- 待审核申请表格 -->
    <div class="card">
      <div class="table-container">
        <table class="application-table">
          <thead>
            <tr>
              <th>学生姓名</th>
              <th>学号</th>
              <th>所在系</th>
              <th>专业</th>
              <th>申请类型</th>
              <th>申请时间</th>
              <th>自评分数</th>
              <th>选择规则</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="application in paginatedApplications" :key="application.id">
              <td>{{ application.studentName }}</td>
              <td>{{ application.studentId }}</td>
              <td>{{ getDepartmentText(application.department) }}</td>
              <td>{{ getMajorText(application.major) }}</td>
              <td>{{ getTypeText(application.applicationType) }}</td>
              <td>{{ formatDate(application.appliedAt) }}</td>
              <td>{{ application.selfScore }}</td>
              <td>{{ application.rule?.name || '未选择' }}</td>
              <td>
                <button class="btn-outline btn small-btn" @click="reviewApplication(application)">
                  <font-awesome-icon :icon="['fas', 'eye']" /> 审核
                </button>
              </td>
            </tr>
            <tr v-if="paginatedApplications.length === 0">
              <td colspan="9" class="no-data">暂无待审核申请</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 分页控件 -->
    <div class="pagination">
      <div>显示 {{ startIndex + 1 }}-{{ endIndex }} 条，共 {{ totalApplications }} 条记录</div>
      <div class="pagination-controls">
        <button class="btn-outline btn" :disabled="pagination.currentPage === 1" @click="prevPage">
          <font-awesome-icon :icon="['fas', 'chevron-left']" /> 上一页
        </button>
        <button class="btn-outline btn" :disabled="pagination.currentPage >= totalPages" @click="nextPage">
          下一页 <font-awesome-icon :icon="['fas', 'chevron-right']" />
        </button>
      </div>
    </div>

    <!-- 审核详情模态框 -->
    <ApplicationDetailModal v-if="selectedApplication" :application="selectedApplication" @approve="handleApprove"
      @reject="handleReject" @close="closeReviewModal" :is-review-mode="true" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useApplicationsStore } from '../../stores/applications'
import ApplicationDetailModal from '../common/ApplicationDetailModal.vue'
import api from '../../utils/api'

const authStore = useAuthStore()
const applicationsStore = useApplicationsStore()

// 筛选条件
const filters = ref({
  faculty: 'all',
  department: 'all',
  major: 'all',
  type: 'all',
  studentId: '',
  studentName: '',
  startDate: '',
  endDate: ''
})

// 学院、系和专业数据
const faculties = ref([])
const departments = ref([])
const majors = ref([])
const loadingDepartments = ref(false)
const loadingMajors = ref(false)

// 分页
const pagination = ref({
  currentPage: 1,
  pageSize: 10
})

// 当前选中的申请
const selectedApplication = ref(null)

// 加载状态
const loading = computed(() => applicationsStore.loading)

// 筛选和分页处理后的申请数据
const filteredAndPaginatedApplications = computed(() => {
  // 先筛选
  let filtered = applicationsStore.filterApplications({
    faculty: filters.value.faculty !== 'all' ? filters.value.faculty : undefined,
    department: filters.value.department !== 'all' ? filters.value.department : undefined,
    major: filters.value.major !== 'all' ? filters.value.major : undefined,
    type: filters.value.type !== 'all' ? filters.value.type : undefined,
    studentId: filters.value.studentId,
    studentName: filters.value.studentName,
    startDate: filters.value.startDate,
    endDate: filters.value.endDate
  })
  
  // 只保留待审核的
  filtered = filtered.filter(app => app.status === 'pending')
  
  // 再分页
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  const end = start + pagination.value.pageSize
  return filtered.slice(start, end)
})

// 总记录数
const totalApplications = computed(() => {
  let filtered = applicationsStore.filterApplications({
    faculty: filters.value.faculty !== 'all' ? filters.value.faculty : undefined,
    department: filters.value.department !== 'all' ? filters.value.department : undefined,
    major: filters.value.major !== 'all' ? filters.value.major : undefined,
    type: filters.value.type !== 'all' ? filters.value.type : undefined,
    studentId: filters.value.studentId,
    studentName: filters.value.studentName,
    startDate: filters.value.startDate,
    endDate: filters.value.endDate
  })
  return filtered.filter(app => app.status === 'pending').length
})

// 计算属性
const totalPages = computed(() => {
  return Math.ceil(totalApplications.value / pagination.value.pageSize)
})

const startIndex = computed(() => (pagination.value.currentPage - 1) * pagination.value.pageSize)
const endIndex = computed(() => Math.min(startIndex.value + pagination.value.pageSize, totalApplications.value))

const paginatedApplications = computed(() => {
  return filteredAndPaginatedApplications.value
})

// 方法
const getDepartmentText = (department) => {
  // 如果已经是完整名称，则直接返回
  if (department === '计算机科学系' || department === '软件工程系' || department === '人工智能系') {
    return department
  }
  // 否则尝试映射缩写
  const departments = {
    cs: '计算机科学系',
    se: '软件工程系',
    ai: '人工智能系'
  }
  return departments[department] || department
}

const getMajorText = (major) => {
  // 如果已经是完整名称，则直接返回
  if (major === '计算机科学与技术' || major === '软件工程' || major === '人工智能') {
    return major
  }
  // 否则尝试映射缩写
  const majors = {
    cs: '计算机科学与技术',
    se: '软件工程',
    ai: '人工智能'
  }
  return majors[major] || major
}

const getTypeText = (type) => {
  return type === 'academic' ? '学术专长' : '综合表现'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'  
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 清空筛选条件
const clearFilters = async () => {
  filters.value = {
    department: 'all',
    major: 'all',
    type: 'all',
    studentId: '',
    studentName: '',
    startDate: '',
    endDate: ''
  }
  // 重置到第一页
  pagination.value.currentPage = 1
  // 重新加载数据
  await applicationsStore.fetchApplications()
}

const filterApplications = () => {
  pagination.value.currentPage = 1
}

const applyFilters = () => {
  pagination.value.currentPage = 1
}

const prevPage = () => {
  if (pagination.value.currentPage > 1) {
    pagination.value.currentPage--
  }
}

const nextPage = () => {
  if (pagination.value.currentPage < totalPages.value) {
    pagination.value.currentPage++
  }
}

const reviewApplication = (application) => {
  //console.log('点击审核按钮，申请信息:', application)
  selectedApplication.value = { ...application }
  //console.log('selectedApplication 已设置:', selectedApplication.value)
  // 确保对象结构正确
  //console.log('selectedApplication 属性:', Object.keys(selectedApplication.value || {}))
}

const handleApprove = async (approveData) => {
  try {
    // 从对象参数中提取需要的字段
    const { applicationId, finalScore, approveComment } = approveData
    // 调用API批准申请
    await applicationsStore.approveApplication(
      applicationId,
      finalScore,
      approveComment,
      authStore.userName || '当前教师'
    )
    // 重新加载数据
    await applicationsStore.fetchApplications()
    closeReviewModal()
    alert('申请已通过审核')
  } catch (error) {
    console.error('批准申请失败:', error)
    alert('批准申请失败，请稍后重试')
  }
}

const handleReject = async (rejectData) => {
  try {
    // 从对象参数中提取需要的字段
    const { applicationId, rejectComment } = rejectData
    // 调用API拒绝申请
    await applicationsStore.rejectApplication(
      applicationId,
      rejectComment,
      authStore.userName || '当前教师'
    )
    // 重新加载数据
    await applicationsStore.fetchApplications()
    closeReviewModal()
    alert('申请已驳回')
  } catch (error) {
    console.error('拒绝申请失败:', error)
    alert('拒绝申请失败，请稍后重试')
  }
}

const closeReviewModal = () => {
  selectedApplication.value = null
}

// 重置筛选条件
const resetFilters = () => {
  filters.value = {
    department: 'all',
    major: 'all',
    type: 'all',
    studentId: '',
    studentName: '',
    startDate: '',
    endDate: ''
  }
  pagination.value.currentPage = 1
}

// 重新加载数据
const refreshData = async () => {
  // 老师页面只需要获取待审核申请
  await applicationsStore.fetchPendingApplications()
}

// 生命周期
onMounted(async () => {
  try {
    // 并行获取数据
    await Promise.all([
      loadPendingApplications(),
      loadFaculties(),
      loadDepartments(),
      loadMajors()
    ])
  } catch (error) {
    console.error('数据加载失败:', error)
    alert('数据加载失败，请稍后重试')
  }
})

// 加载待审核申请
const loadPendingApplications = async () => {
  try {
    await applicationsStore.fetchPendingApplications()
  } catch (error) {
    console.error('获取待审核申请失败:', error)
    throw error
  }
}

// 从后端获取所有系
const loadDepartments = async () => {
  try {
    loadingDepartments.value = true
    // 这里使用管理员接口，因为老师也需要查看所有系
    const response = await api.getDepartmentsAdmin()
    departments.value = response.departments || []
  } catch (error) {
    console.error('获取系列表失败:', error)
    // 如果管理员接口不可用，尝试使用普通接口
    try {
      // 假设facultyId为1（信息学院）
      const response = await api.getDepartmentsByFaculty(1)
      departments.value = response.departments || []
    } catch (error) {
      console.error('获取系列表失败:', error)
      // 如果都失败，使用默认值
      departments.value = []
    }
  } finally {
    loadingDepartments.value = false
  }
}

// 从后端获取所有学院
const loadFaculties = async () => {
  try {
    // 获取所有学院
    const response = await api.getFaculties()
    faculties.value = response.faculties || []
  } catch (error) {
    console.error('获取学院列表失败:', error)
    faculties.value = []
  }
}

// 从后端获取所有专业
const loadMajors = async () => {
  try {
    loadingMajors.value = true
    // 获取所有专业
    const response = await api.getMajors()
    majors.value = response.majors || []
  } catch (error) {
    console.error('获取专业列表失败:', error)
    // 如果失败，使用默认值
    majors.value = []
  } finally {
    loadingMajors.value = false
  }
}
</script>

<style scoped>
/* 组件特有样式 */
.date-range-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-separator {
  color: #999;
  font-size: 14px;
  white-space: nowrap;
}

.form-control.small {
  width: 120px;
}
</style>

<style>
/* 引入共享样式 */
@import '../common/shared-styles.css';
</style>