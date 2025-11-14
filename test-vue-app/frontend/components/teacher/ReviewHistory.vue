<template>
  <div class="page-content">
    <div class="page-title">
      <span>审核记录</span>
    </div>

    <!-- 筛选区域 -->
    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">所在系:</span>
        <select v-model="filters.department" @change="filterApplications">
          <option value="all">全部</option>
          <option value="cs">计算机科学系</option>
          <option value="se">软件工程系</option>
          <option value="ai">人工智能系</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">专业:</span>
        <select v-model="filters.major" @change="filterApplications">
          <option value="all">全部</option>
          <option value="cs">计算机科学与技术</option>
          <option value="se">软件工程</option>
          <option value="ai">人工智能</option>
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
        <span class="filter-label">审核状态:</span>
        <select v-model="filters.status" @change="filterApplications">
          <option value="all">全部</option>
          <option value="approved">已通过</option>
          <option value="rejected">已驳回</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">时间段:</span>
        <input type="date" class="form-control small" v-model="filters.startDate">
        至 <input type="date" class="form-control small" v-model="filters.endDate">
      </div>
      <button class="btn" @click="applyFilters">应用筛选</button>
    </div>

    <!-- 审核记录表格 -->
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
              <th>审核时间</th>
              <th>自评分数</th>
              <th>核定分数</th>
              <th>审核状态</th>
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
              <td>{{ formatDate(application.reviewedAt) }}</td>
              <td>{{ application.selfScore }}</td>
              <td>{{ application.finalScore || '-' }}</td>
              <td>
                <span :class="`status-badge status-${application.status}`">
                  {{ getStatusText(application.status) }}
                </span>
              </td>
              <td>
                <button class="btn-outline btn small-btn" @click="viewApplication(application)">
                  <font-awesome-icon :icon="['fas', 'eye']" /> 查看
                </button>
              </td>
            </tr>
            <tr v-if="paginatedApplications.length === 0">
              <td colspan="11" class="no-data">暂无审核记录</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 分页控件 -->
    <div class="pagination">
      <div>显示 {{ startIndex + 1 }}-{{ endIndex }} 条，共 {{ totalApplications }} 条记录</div>
      <div class="pagination-controls">
        <button class="btn-outline btn" :disabled="currentPage === 1" @click="prevPage">
          <font-awesome-icon :icon="['fas', 'chevron-left']" /> 上一页
        </button>
        <button class="btn-outline btn" :disabled="currentPage >= totalPages" @click="nextPage">
          下一页 <font-awesome-icon :icon="['fas', 'chevron-right']" />
        </button>
      </div>
    </div>

    <!-- 申请详情模态框 -->
    <ReviewDetailModal v-if="selectedApplication" :application="selectedApplication" :readonly="true"
      @close="closeDetailModal" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import ReviewDetailModal from './ReviewDetailModal.vue'
import { useApplicationsStore } from '../../stores/applications'

const applicationsStore = useApplicationsStore()
const selectedApplication = ref(null)

// 筛选条件
const filters = ref({
  department: 'all',
  major: 'all',
  type: 'all',
  status: 'all',
  startDate: '',
  endDate: ''
})

// 分页
const pagination = ref({
  currentPage: 1,
  pageSize: 10
})

// 加载状态
const loading = computed(() => applicationsStore.loading)

// 筛选和分页处理后的申请数据
const paginatedApplications = computed(() => {
  // 先筛选
  let filtered = applicationsStore.filterApplications({
    department: filters.value.department !== 'all' ? filters.value.department : undefined,
    major: filters.value.major !== 'all' ? filters.value.major : undefined,
    type: filters.value.type !== 'all' ? filters.value.type : undefined,
    startDate: filters.value.startDate,
    endDate: filters.value.endDate
  })
  
  // 只保留已审核的
  filtered = filtered.filter(app => app.status === 'approved' || app.status === 'rejected')
  
  // 如果有状态筛选
  if (filters.value.status !== 'all') {
    filtered = filtered.filter(app => app.status === filters.value.status)
  }
  
  // 按审核时间倒序排序
  filtered.sort((a, b) => {
    const dateA = new Date(a.reviewedAt || 0)
    const dateB = new Date(b.reviewedAt || 0)
    return dateB - dateA
  })
  
  // 再分页
  const startIndex = (pagination.value.currentPage - 1) * pagination.value.pageSize
  const endIndex = startIndex + pagination.value.pageSize
  return filtered.slice(startIndex, endIndex)
})

// 总记录数
const totalApplications = computed(() => {
  let filtered = applicationsStore.filterApplications({
    department: filters.value.department !== 'all' ? filters.value.department : undefined,
    major: filters.value.major !== 'all' ? filters.value.major : undefined,
    type: filters.value.type !== 'all' ? filters.value.type : undefined,
    startDate: filters.value.startDate,
    endDate: filters.value.endDate
  })
  
  filtered = filtered.filter(app => app.status === 'approved' || app.status === 'rejected')
  
  if (filters.value.status !== 'all') {
    filtered = filtered.filter(app => app.status === filters.value.status)
  }
  
  return filtered.length
})

const totalPages = computed(() => Math.ceil(totalApplications.value / pagination.value.pageSize))
const startIndex = computed(() => (pagination.value.currentPage - 1) * pagination.value.pageSize)
const endIndex = computed(() => Math.min(startIndex.value + pagination.value.pageSize, totalApplications.value))

// 方法
const getDepartmentText = (department) => {
  const departments = {
    cs: '计算机科学系',
    se: '软件工程系',
    ai: '人工智能系'
  }
  return departments[department] || department
}

const getMajorText = (major) => {
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

const getStatusText = (status) => {
  const statusText = {
    approved: '已通过',
    rejected: '已驳回'
  }
  return statusText[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
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

const viewApplication = (application) => {
  // 从store获取完整的申请详情
  selectedApplication.value = applicationsStore.getApplicationById(application.id) || application
}

const closeDetailModal = () => {
  selectedApplication.value = null
}

// 重置筛选
const resetFilters = () => {
  filters.value = {
    department: 'all',
    major: 'all',
    type: 'all',
    status: 'all',
    startDate: '',
    endDate: ''
  }
  pagination.value.currentPage = 1
}

// 生命周期
onMounted(async () => {
  // 确保数据已加载
  if (applicationsStore.applications.length === 0) {
    await applicationsStore.fetchApplications()
  }
})
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