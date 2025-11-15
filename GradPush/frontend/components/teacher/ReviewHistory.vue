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
                <div class="action-buttons">
                  <button class="btn-outline btn small-btn" @click="viewApplication(application)" title="查看">
                    <font-awesome-icon :icon="['fas', 'eye']" /> 
                  </button>
                  <button class="btn-outline btn small-btn" @click="editApplication(application)" title="编辑">
                    <font-awesome-icon :icon="['fas', 'edit']" /> 
                  </button>
                </div>
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
        <button class="btn-outline btn" :disabled="pagination.currentPage === 1" @click="prevPage">
          <font-awesome-icon :icon="['fas', 'chevron-left']" /> 上一页
        </button>
        <button class="btn-outline btn" :disabled="pagination.currentPage >= totalPages" @click="nextPage">
          下一页 <font-awesome-icon :icon="['fas', 'chevron-right']" />
        </button>
      </div>
    </div>

    <!-- 查看申请详情模态框 -->
    <TeacherViewDetailModal v-if="selectedApplication" :application="selectedApplication"
      @close="closeDetailModal" />

    <!-- 编辑申请详情模态框 -->
    <TeacherEditDetailModal v-if="editingApplication" :application="editingApplication"
      @close="closeEditDialog" @approve="handleApproveApplication" @reject="handleRejectApplication" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TeacherViewDetailModal from './TeacherViewDetailModal.vue'
import TeacherEditDetailModal from './TeacherEditDetailModal.vue'
import { useApplicationsStore } from '../../stores/applications'
import { useAuthStore } from '../../stores/auth'

const applicationsStore = useApplicationsStore()
const authStore = useAuthStore()
const selectedApplication = ref(null)

// 编辑弹窗相关
const editingApplication = ref(null)

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

const viewApplication = async (application) => {
  // 从store获取完整的申请详情
  selectedApplication.value = await applicationsStore.getApplicationById(application.id) || application
}

const closeDetailModal = () => {
  selectedApplication.value = null
}

// 编辑功能方法
const editApplication = async (application) => {
  // 从store获取完整的申请详情
  editingApplication.value = await applicationsStore.getApplicationById(application.id) || application
}

const closeEditDialog = () => {
  editingApplication.value = null
}

// 审核操作处理
const handleApproveApplication = async (applicationId, finalScore, comment) => {
  try {
    const success = await applicationsStore.approveApplication(applicationId, finalScore, comment, authStore.userName)
    if (success) {
      alert('审核通过成功')
      closeEditDialog()
    } else {
      alert('审核通过失败')
    }
  } catch (error) {
    console.error('审核通过失败:', error)
    alert('审核通过失败，请重试')
  }
}

const handleRejectApplication = async (applicationId, comment) => {
  try {
    const success = await applicationsStore.rejectApplication(applicationId, comment, authStore.userName)
    if (success) {
      alert('驳回成功')
      closeEditDialog()
    } else {
      alert('驳回失败')
    }
  } catch (error) {
    console.error('驳回失败:', error)
    alert('驳回失败，请重试')
  }
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

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.small-btn {
  padding: 6px 10px;
  font-size: 12px;
}

/* 操作列按钮悬停效果 */
.action-buttons .small-btn:hover {
  transform: none;
}

/* 编辑弹窗样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.dialog-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #e9ecef;
}

.dialog-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #666;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #333;
}

.dialog-body {
  padding: 20px;
}

.form-row {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.form-group {
  flex: 1;
}

.form-group.full-width {
  flex: 1 1 100%;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.detail-value {
  display: block;
  margin-top: 5px;
  padding: 8px 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
  color: #495057;
}

.detail-value.comment {
  white-space: pre-wrap;
  min-height: 80px;
  font-style: italic;
}
</style>

<style>
/* 引入共享样式 */
@import '../common/shared-styles.css';
</style>