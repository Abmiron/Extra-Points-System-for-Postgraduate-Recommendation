<template>
  <div class="page-content">
    <div class="page-title">
      <span>申请记录</span>
      <button class="btn" @click="$emit('new-application')">
        <font-awesome-icon :icon="['fas', 'plus']" /> 新建申请
      </button>
    </div>

    <!-- 筛选区域 -->
    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">状态:</span>
        <select v-model="filters.status" @change="filterApplications">
          <option value="all">全部</option>
          <option value="draft">草稿</option>
          <option value="pending">待审核</option>
          <option value="approved">已通过</option>
          <option value="rejected">未通过</option>
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
        <span class="filter-label">排序:</span>
        <select v-model="filters.sort" @change="filterApplications">
          <option value="newest">最新优先</option>
          <option value="oldest">最旧优先</option>
        </select>
      </div>
      <button class="btn" @click="resetFilters">重置筛选</button>
    </div>

    <!-- 申请记录表格 -->
    <div class="card">
      <div class="table-container">
        <table class="application-table">
          <thead>
            <tr>
              <th>申请时间</th>
              <th>类型</th>
              <th>级别</th>
              <th>项目名称</th>
              <th>状态</th>
              <th>预计分数</th>
              <th>最终分数</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="application in filteredApplications" :key="application.id">
              <td>{{ formatDate(application.appliedAt || application.createdAt) }}</td>
              <td>{{ getTypeText(application.applicationType) }}</td>
              <td>{{ getLevelText(application.awardLevel) }}</td>
              <td>{{ application.projectName }}</td>
              <td>
                <span :class="`status-badge status-${application.status}`">
                  {{ getStatusText(application.status) }}
                </span>
              </td>
              <td>{{ application.selfScore }}</td>
              <td>{{ application.finalScore || '-' }}</td>
              <td>
                <button class="btn-outline btn small-btn" @click="viewApplication(application)">
                  <font-awesome-icon :icon="['fas', 'eye']" />
                </button>
                <button v-if="application.status === 'draft'" 
                        class="btn-outline btn small-btn" 
                        @click="editApplication(application)">
                  <font-awesome-icon :icon="['fas', 'edit']" />
                </button>
                <button v-if="application.status === 'draft'" 
                        class="btn-outline btn small-btn" 
                        @click="deleteApplication(application.id)">
                  <font-awesome-icon :icon="['fas', 'trash']" />
                </button>
              </td>
            </tr>
            <tr v-if="filteredApplications.length === 0">
              <td colspan="8" class="no-data">暂无申请记录</td>
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
    <div v-if="selectedApplication" class="modal-overlay" @click="closeModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>申请详情</h3>
          <button class="close-btn" @click="closeModal">
            <font-awesome-icon :icon="['fas', 'times']" />
          </button>
        </div>
        <div class="modal-body">
          <div class="application-detail">
            <div class="detail-section">
              <h4>基本信息</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>申请类型:</label>
                  <span>{{ getTypeText(selectedApplication.applicationType) }}</span>
                </div>
                <div class="detail-item">
                  <label>项目名称:</label>
                  <span>{{ selectedApplication.projectName }}</span>
                </div>
                <div class="detail-item">
                  <label>获奖时间:</label>
                  <span>{{ formatDate(selectedApplication.awardDate) }}</span>
                </div>
                <div class="detail-item">
                  <label>奖项级别:</label>
                  <span>{{ getLevelText(selectedApplication.awardLevel) }}</span>
                </div>
                <div class="detail-item">
                  <label>奖项类型:</label>
                  <span>{{ selectedApplication.awardType === 'individual' ? '个人奖项' : '集体奖项' }}</span>
                </div>
                <div v-if="selectedApplication.awardType === 'team'" class="detail-item">
                  <label>作者排序:</label>
                  <span>第 {{ selectedApplication.authorOrder }} 作者</span>
                </div>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>评分信息</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>自评分数:</label>
                  <span>{{ selectedApplication.selfScore }}</span>
                </div>
                <div class="detail-item">
                  <label>最终分数:</label>
                  <span>{{ selectedApplication.finalScore || '-' }}</span>
                </div>
                <div class="detail-item">
                  <label>审核状态:</label>
                  <span :class="`status-badge status-${selectedApplication.status}`">
                    {{ getStatusText(selectedApplication.status) }}
                  </span>
                </div>
                <div v-if="selectedApplication.reviewedAt" class="detail-item">
                  <label>审核时间:</label>
                  <span>{{ formatDate(selectedApplication.reviewedAt) }}</span>
                </div>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>加分依据说明</h4>
              <p class="description">{{ selectedApplication.description }}</p>
            </div>
            
            <div v-if="selectedApplication.reviewComment" class="detail-section">
              <h4>审核意见</h4>
              <p class="review-comment">{{ selectedApplication.reviewComment }}</p>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="closeModal">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

const emit = defineEmits(['new-application'])

const applications = ref([])
const selectedApplication = ref(null)
const currentPage = ref(1)
const pageSize = 10

const filters = reactive({
  status: 'all',
  type: 'all',
  sort: 'newest'
})

// 计算属性
const filteredApplications = computed(() => {
  let filtered = applications.value.filter(app => {
    const statusMatch = filters.status === 'all' || app.status === filters.status
    const typeMatch = filters.type === 'all' || app.applicationType === filters.type
    return statusMatch && typeMatch
  })
  
  // 排序
  if (filters.sort === 'newest') {
    filtered.sort((a, b) => new Date(b.appliedAt || b.createdAt) - new Date(a.appliedAt || a.createdAt))
  } else {
    filtered.sort((a, b) => new Date(a.appliedAt || a.createdAt) - new Date(b.appliedAt || b.createdAt))
  }
  
  return filtered
})

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

const getLevelText = (level) => {
  const levels = {
    national: '国家级',
    provincial: '省级',
    municipal: '市级',
    school: '校级'
  }
  return levels[level] || level
}

const getStatusText = (status) => {
  const statusText = {
    draft: '草稿',
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

const filterApplications = () => {
  currentPage.value = 1
}

const resetFilters = () => {
  filters.status = 'all'
  filters.type = 'all'
  filters.sort = 'newest'
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

const editApplication = (application) => {
  // 这里可以跳转到编辑页面或填充表单
  emit('edit-application', application)
}

const deleteApplication = (id) => {
  if (confirm('确定要删除此申请吗？')) {
    applications.value = applications.value.filter(app => app.id !== id)
    // 更新本地存储
    localStorage.setItem('studentApplications', JSON.stringify(applications.value))
  }
}

const closeModal = () => {
  selectedApplication.value = null
}

// 生命周期
onMounted(() => {
  // 从本地存储加载数据
  const savedApplications = JSON.parse(localStorage.getItem('studentApplications') || '[]')
  const savedDrafts = JSON.parse(localStorage.getItem('applicationDrafts') || '[]')
  
  // 合并申请和草稿
  applications.value = [
    ...savedDrafts.map(draft => ({ ...draft, status: 'draft' })),
    ...savedApplications
  ]
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

select {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
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

.status-draft {
  background-color: #fef5e7;
  color: #e67e22;
}

.status-pending {
  background-color: #ebf5fb;
  color: #3498db;
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
  padding: 4px 8px;
  font-size: 12px;
}

/* 模态框样式 */
.modal-overlay {
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
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow: auto;
}

.modal-content.large {
  max-width: 1000px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 20px;
  border-top: 1px solid #eee;
}

/* 申请详情样式 */
.application-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section h4 {
  margin-bottom: 15px;
  color: #003366;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-item label {
  font-weight: 500;
  color: #666;
}

.description, .review-comment {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  line-height: 1.6;
}

.review-comment {
  background-color: #fff3cd;
  border-left: 4px solid #ffc107;
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
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
}
</style>