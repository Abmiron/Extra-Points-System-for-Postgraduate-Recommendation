<template>
  <div class="page-content">
    <div class="page-title">
      <span>数据管理</span>
  
    </div>

    <!-- 搜索区域 - 修改为与用户管理组件相同样式 -->
    <div class="filters">
      <div class="filter-group">
        <input type="text" class="form-control" v-model="filters.studentName" placeholder="学生姓名">
      </div>
      <div class="filter-group">
        <input type="text" class="form-control" v-model="filters.studentId" placeholder="学号">
      </div>
      <div class="filter-group">
        <span class="filter-label">申请类型:</span>
        <select class="form-control" v-model="filters.applicationType">
          <option value="all">全部类型</option>
          <option value="academic">学术专长</option>
          <option value="comprehensive">综合表现</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">审核状态:</span>
        <select class="form-control" v-model="filters.status">
          <option value="all">全部状态</option>
          <option value="pending">待审核</option>
          <option value="approved">已通过</option>
          <option value="rejected">未通过</option>
        </select>
      </div>
      <div class="filter-group date-range-group">
        <span class="filter-label">申请时间:</span>
        <div class="date-range">
          <input type="date" class="form-control" v-model="filters.startDate">
          <span class="date-separator">至</span>
          <input type="date" class="form-control" v-model="filters.endDate">
        </div>
      </div>
      <button class="btn" @click="searchApplications">搜索</button>
      <button class="btn btn-outline" @click="resetFilters">重置</button>
    </div>

    <!-- 批量操作工具栏 -->
    <div class="batch-actions">
      <button class="btn btn-outline" @click="exportData">
        <font-awesome-icon :icon="['fas', 'download']" /> 导出数据
      </button>
      <button class="btn btn-outline" @click="batchDelete" :disabled="selectedApplications.length === 0">
        <font-awesome-icon :icon="['fas', 'trash']" /> 删除选中
      </button>
    </div>

    <!-- 数据表格 -->
    <div class="card">
      <!-- 加载状态指示器 -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">加载中...</div>
      </div>
      <div class="table-container">
        <table class="application-table">
          <thead>
            <tr>
              <th><input type="checkbox" v-model="selectAll" @change="toggleSelectAll"></th>
              <th>申请ID</th>
              <th>学生姓名</th>
              <th>学号</th>
              <th>申请类型</th>
              <th>项目名称</th>
              <th>申请时间</th>
              <th>状态</th>
              <th>自评分数</th>
              <th>核定分数</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="application in paginatedApplications" :key="application.id" class="table-row">
              <td><input type="checkbox" v-model="selectedApplications" :value="application.id"></td>
              <td>{{ application.id }}</td>
              <td>{{ application.studentName }}</td>
              <td>{{ application.studentId }}</td>
              <td>{{ getTypeText(application.applicationType) }}</td>
              <td>{{ application.projectName }}</td>
              <td>{{ formatDate(application.appliedAt) }}</td>
              <td>
                <span :class="`status-badge status-${application.status}`">
                  {{ getStatusText(application.status) }}
                </span>
              </td>
              <td>{{ application.selfScore }}</td>
              <td>{{ application.finalScore || '-' }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn-outline btn small-btn" @click="viewApplication(application)" title="查看">
                    <font-awesome-icon :icon="['fas', 'eye']" />
                  </button>
                  <button class="btn-outline btn small-btn" @click="editApplication(application)" title="编辑">
                    <font-awesome-icon :icon="['fas', 'edit']" />
                  </button>
                  <button class="btn-outline btn small-btn" @click="deleteApplication(application.id)" title="删除">
                    <font-awesome-icon :icon="['fas', 'trash']" />
                  </button>

                </div>
              </td>
            </tr>
            <tr v-if="paginatedApplications.length === 0">
              <td colspan="11" class="no-data">暂无申请数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 分页控件 -->
    <div class="pagination">
      <div class="pagination-info">显示 {{ startIndex + 1 }}-{{ endIndex }} 条，共 {{ totalApplications }} 条记录</div>
      <div class="pagination-controls">
        <button class="btn-outline btn" :disabled="currentPage === 1" @click="prevPage">
          <font-awesome-icon :icon="['fas', 'chevron-left']" /> 上一页
        </button>
        <button class="btn-outline btn" :disabled="currentPage >= totalPages" @click="nextPage">
          下一页 <font-awesome-icon :icon="['fas', 'chevron-right']" />
        </button>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <div v-if="editDialogVisible" class="dialog-overlay" @click="closeEditDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>编辑申请</h3>
          <button class="close-btn" @click="closeEditDialog">
            <font-awesome-icon :icon="['fas', 'times']" />
          </button>
        </div>
        <div class="dialog-body">
          <form @submit.prevent="saveApplication">
            <div class="form-row">
              <div class="form-group">
                <label>学生姓名</label>
                <input type="text" v-model="editForm.studentName" required>
              </div>
              <div class="form-group">
                <label>学号</label>
                <input type="text" v-model="editForm.studentId" required>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>性别</label>
                <select v-model="editForm.gender" required>
                  <option value="">请选择</option>
                  <option value="男">男</option>
                  <option value="女">女</option>
                </select>
              </div>
              <div class="form-group">
                <label>年级</label>
                <input type="text" v-model="editForm.grade" required>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>申请类型</label>
                <select v-model="editForm.applicationType" required>
                  <option value="">请选择</option>
                  <option value="graduation">毕业申请</option>
                  <option value="internship">实习申请</option>
                  <option value="transfer">转学申请</option>
                  <option value="other">其他申请</option>
                </select>
              </div>
              <div class="form-group">
                <label>申请状态</label>
                <select v-model="editForm.status" required>
                  <option value="">请选择</option>
                  <option value="pending">待审核</option>
                  <option value="approved">已通过</option>
                  <option value="rejected">已拒绝</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>申请日期</label>
                <input type="date" v-model="editForm.applicationDate" required>
              </div>
              <div class="form-group">
                <label>审核日期</label>
                <input type="date" v-model="editForm.reviewDate">
              </div>
            </div>
            <div class="form-row">
              <div class="form-group full-width">
                <label>审核意见</label>
                <textarea v-model="editForm.reviewerComments" rows="3"></textarea>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="closeEditDialog">取消</button>
              <button type="submit" class="btn btn-primary">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 查看详情模态框 -->
    <AdminViewDetailModal
      v-if="viewDetailModalVisible"
      :application="selectedApplication"
      @close="closeViewDetailModal"
    />

    <!-- 审核操作模态框 -->
    <AdminReviewDetailModal
      v-if="reviewDetailModalVisible"
      :application="selectedApplication"
      @approve="handleApproveApplication"
      @reject="handleRejectApplication"
      @close="closeReviewDetailModal"
    />


  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import AdminViewDetailModal from './AdminViewDetailModal.vue'
import AdminReviewDetailModal from './AdminReviewDetailModal.vue'
import { useApplicationsStore } from '../../stores/applications'
import { useAuthStore } from '../../stores/auth'



const applicationsStore = useApplicationsStore()
const authStore = useAuthStore()
const selectedApplication = ref(null)
const selectAll = ref(false)
const selectedApplications = ref([])
const currentPage = ref(1)
const pageSize = 10
const isLoading = ref(false)

// 编辑弹窗相关
const editDialogVisible = ref(false)
const editingApplication = ref(null)
const editForm = ref({
  studentName: '',
  studentId: '',
  gender: '',
  grade: '',
  applicationType: '',
  status: '',
  applicationDate: '',
  reviewDate: '',
  reviewerComments: ''
})

// 模态框显示状态
const viewDetailModalVisible = ref(false)
const reviewDetailModalVisible = ref(false)

const filters = reactive({
  studentName: '',
  studentId: '',
  applicationType: 'all',
  status: 'all',
  startDate: '',
  endDate: ''
})

// 使用store中的applications数据
const applications = computed(() => applicationsStore.applications)

// 计算属性
const filteredApplications = computed(() => {
  let filtered = applications.value.filter(app => {
    const nameMatch = !filters.studentName || app.studentName.includes(filters.studentName)
    const idMatch = !filters.studentId || app.studentId.includes(filters.studentId)
    const typeMatch = filters.applicationType === 'all' || app.applicationType === filters.applicationType
    const statusMatch = filters.status === 'all' || app.status === filters.status
    const dateMatch = !filters.startDate || !filters.endDate ||
      (new Date(app.appliedAt) >= new Date(filters.startDate) &&
        new Date(app.appliedAt) <= new Date(filters.endDate))

    return nameMatch && idMatch && typeMatch && statusMatch && dateMatch
  })

  return filtered
})

// 监听筛选结果变化，确保当前页码有效
watch(filteredApplications, () => {
  if (currentPage.value > totalPages.value && totalPages.value > 0) {
    currentPage.value = totalPages.value
  } else if (totalPages.value === 0) {
    currentPage.value = 1
  }
}, { deep: true })

const totalApplications = computed(() => filteredApplications.value.length)
const totalPages = computed(() => Math.ceil(totalApplications.value / pageSize))
const startIndex = computed(() => (currentPage.value - 1) * pageSize)
const endIndex = computed(() => Math.min(startIndex.value + pageSize, totalApplications.value))

const paginatedApplications = computed(() => {
  return filteredApplications.value.slice(startIndex.value, endIndex.value)
})

// 方法
const getTypeText = (type) => {
  return type === 'academic' ? '学术专长' : '综合表现'
}

const getStatusText = (status) => {
  const statusText = {
    pending: '待审核',
    approved: '已通过',
    rejected: '未通过'
  }
  return statusText[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const getApplicationTypeText = (type) => {
  const typeMap = {
    graduation: '毕业申请',
    internship: '实习申请',
    transfer: '转学申请',
    other: '其他申请'
  }
  return typeMap[type] || '未知类型'
}



const searchApplications = () => {
  currentPage.value = 1
  // 由于后端API不支持所有筛选条件，我们在前端进行筛选
}

const resetFilters = () => {
  Object.assign(filters, {
    studentName: '',
    studentId: '',
    applicationType: 'all',
    status: 'all',
    startDate: '',
    endDate: ''
  })
  currentPage.value = 1
}

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedApplications.value = filteredApplications.value.map(app => app.id)
  } else {
    selectedApplications.value = []
  }
}

const exportData = () => {
  alert('数据导出功能开发中...')
}

const batchDelete = async () => {
  if (confirm(`确定要删除选中的 ${selectedApplications.value.length} 个申请吗？`)) {
    isLoading.value = true
    let successCount = 0
    let failCount = 0
    
    try {
      // 循环删除每个选中的申请
      for (const id of selectedApplications.value) {
        const success = await applicationsStore.deleteApplication(id)
        if (success) {
          successCount++
        } else {
          failCount++
        }
      }
      
      // 清空选中列表
      selectedApplications.value = []
      selectAll.value = false
      
      // 显示结果
      alert(`批量删除完成：成功 ${successCount} 条，失败 ${failCount} 条`)
    } catch (error) {
      console.error('批量删除失败:', error)
      alert('批量删除过程中发生错误，请重试')
    } finally {
      isLoading.value = false
    }
  }
}

const viewApplication = (application) => {
  selectedApplication.value = application
  viewDetailModalVisible.value = true
}

const closeViewDetailModal = () => {
  viewDetailModalVisible.value = false
  selectedApplication.value = null
}

const handleApproveApplication = async (applicationId, finalScore, comment) => {
  try {
    isLoading.value = true
    const success = await applicationsStore.updateApplicationStatus(applicationId, 'approved', comment, finalScore, authStore.userName)
    if (success) {
      alert('审核通过成功')
      reviewDetailModalVisible.value = false
      selectedApplication.value = null
    } else {
      alert('审核通过失败')
    }
  } catch (error) {
    console.error('审核通过失败:', error)
    alert('审核通过失败，请重试')
  } finally {
    isLoading.value = false
  }
}

const handleRejectApplication = async (applicationId, comment) => {
  try {
    isLoading.value = true
    const success = await applicationsStore.updateApplicationStatus(applicationId, 'rejected', comment, 0, authStore.userName)
    if (success) {
      alert('驳回成功')
      reviewDetailModalVisible.value = false
      selectedApplication.value = null
    } else {
      alert('驳回失败')
    }
  } catch (error) {
    console.error('驳回失败:', error)
    alert('驳回失败，请重试')
  } finally {
    isLoading.value = false
  }
}

const editApplication = (application) => {
  selectedApplication.value = application
  reviewDetailModalVisible.value = true
}

const deleteApplication = async (applicationId) => {
  if (confirm('确定要删除这条申请记录吗？')) {
    try {
      const success = await applicationsStore.deleteApplication(applicationId)
      if (success) {
        alert('删除成功')
      } else {
        alert('删除失败')
      }
    } catch (error) {
      console.error('删除申请失败:', error)
      alert('删除失败，请重试')
    }
  }
}



const closeDetailModal = () => {
  selectedApplication.value = null
}

const closeReviewDetailModal = () => {
  reviewDetailModalVisible.value = false
  selectedApplication.value = null
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

// 方法
const loadApplications = async () => {
  isLoading.value = true
  try {
    await applicationsStore.fetchApplications()
    // 数据加载完成后，确保当前页码有效
    if (currentPage.value > totalPages.value && totalPages.value > 0) {
      currentPage.value = totalPages.value
    } else if (totalPages.value === 0) {
      currentPage.value = 1
    }
  } catch (error) {
    console.error('加载申请数据失败:', error)
  } finally {
      isLoading.value = false
  }
}

// 生命周期
onMounted(() => {
  loadApplications()
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

.batch-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

/* 覆盖或补充共享样式 */
.application-table th:last-child,
.application-table td:last-child {
  width: 140px;
  min-width: 140px;
  text-align: center;
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

.application-details .form-group label {
  font-weight: 600;
  color: #333;
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

.status-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.status-pending {
  background-color: #e3f2fd;
  color: #1976d2;
}

.status-approved {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-rejected {
  background-color: #ffebee;
  color: #c62828;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
  border-color: #dc3545;
}

/* 卡片相对定位，确保加载状态只在卡片内显示 */
.card {
  position: relative;
}

/* 加载状态样式 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}

/* 表格行悬停效果 */
.table-row {
  transition: background-color 0.2s;
}

.table-row:hover {
  background-color: #f8f9fa;
}

/* 分页控件样式优化 */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  font-size: 14px;
}

.pagination-info {
  color: #666;
}

.pagination-controls {
  display: flex;
  gap: 10px;
}

/* 按钮悬停效果 */
.btn:hover,
.btn-outline:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* 操作列按钮悬停效果 - 取消上移 */
.action-buttons .small-btn:hover {
  transform: none;
}

/* 小按钮样式优化 */
.small-btn {
  padding: 6px 10px;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    margin-bottom: 10px;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .pagination {
    flex-direction: column;
    gap: 10px;
  }
}


</style>

<style>
/* 引入共享样式 */
@import '../common/shared-styles.css';
</style>