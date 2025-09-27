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
            <tr v-for="application in filteredApplications" :key="application.id">
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
            <tr v-if="filteredApplications.length === 0">
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
    <ReviewDetailModal 
      v-if="selectedApplication"
      :application="selectedApplication"
      :readonly="true"
      @close="closeDetailModal"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import ReviewDetailModal from './ReviewDetailModal.vue'

const selectedApplication = ref(null)

const filters = reactive({
  department: 'all',
  major: 'all',
  type: 'all',
  status: 'all',
  startDate: '',
  endDate: ''
})

const applications = ref([])
const currentPage = ref(1)
const pageSize = 10

// 计算属性
const filteredApplications = computed(() => {
  let filtered = applications.value.filter(app => {
    const departmentMatch = filters.department === 'all' || app.department === filters.department
    const majorMatch = filters.major === 'all' || app.major === filters.major
    const typeMatch = filters.type === 'all' || app.applicationType === filters.type
    const statusMatch = filters.status === 'all' || app.status === filters.status
    const dateMatch = !filters.startDate || !filters.endDate || 
                     (new Date(app.reviewedAt) >= new Date(filters.startDate) && 
                      new Date(app.reviewedAt) <= new Date(filters.endDate))
    
    return departmentMatch && majorMatch && typeMatch && statusMatch && dateMatch
  })
  
  // 按审核时间倒序排列
  return filtered.sort((a, b) => new Date(b.reviewedAt) - new Date(a.reviewedAt))
})

const totalApplications = computed(() => filteredApplications.value.length)
const totalPages = computed(() => Math.ceil(totalApplications.value / pageSize))
const startIndex = computed(() => (currentPage.value - 1) * pageSize)
const endIndex = computed(() => Math.min(startIndex.value + pageSize, totalApplications.value))

const paginatedApplications = computed(() => {
  return filteredApplications.value.slice(startIndex.value, endIndex.value)
})

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
  currentPage.value = 1
}

const applyFilters = () => {
  currentPage.value = 1
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const viewApplication = (application) => {
  selectedApplication.value = application
}

const closeDetailModal = () => {
  selectedApplication.value = null
}

// 生命周期
onMounted(() => {
  // 从本地存储加载已审核的申请数据
  const savedApplications = JSON.parse(localStorage.getItem('studentApplications') || '[]')
  applications.value = savedApplications.filter(app => 
    app.status === 'approved' || app.status === 'rejected'
  )
})
</script>

<style scoped>
.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

select, .form-control.small {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
}

.form-control.small {
  width: 120px;
}

.application-table {
  width: 100%;
  border-collapse: collapse;
}

.application-table th,
.application-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.application-table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.application-table tr:hover {
  background-color: #f8f9fa;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-approved {
  background-color: #eafaf1;
  color: #27ae60;
}

.status-rejected {
  background-color: #fdedec;
  color: #e74c3c;
}

.no-data {
  text-align: center;
  color: #666;
  padding: 40px;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.pagination-controls {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  background-color: #003366;
  color: white;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn:hover {
  background-color: #002244;
}

.btn-outline {
  background-color: transparent;
  color: #003366;
  border: 1px solid #003366;
}

.btn-outline:hover {
  background-color: #003366;
  color: white;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn:disabled:hover {
  background-color: #003366;
}

.small-btn {
  padding: 6px 10px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .pagination {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .application-table {
    font-size: 14px;
  }
  
  .application-table th,
  .application-table td {
    padding: 8px 10px;
  }
}
</style>