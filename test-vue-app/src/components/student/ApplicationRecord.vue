<template>
  <div class="page-content">
    <div class="page-title">
      <span>申请记录</span>
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
                <div class="action-buttons">
                  <button class="btn-outline btn small-btn" @click="viewApplication(application)" title="查看">
                    <font-awesome-icon :icon="['fas', 'eye']" />
                  </button>
                  <button v-if="application.status === 'draft'" class="btn-outline btn small-btn"
                    @click="editApplication(application)" title="编辑">
                    <font-awesome-icon :icon="['fas', 'edit']" />
                  </button>
                  <button v-if="application.status === 'draft'" class="btn-outline btn small-btn"
                    @click="deleteApplication(application.id)" title="删除">
                    <font-awesome-icon :icon="['fas', 'trash']" />
                  </button>
                </div>
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
    <ApplicationDetailModal v-if="selectedApplication" :application="selectedApplication" @close="closeModal" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import ApplicationDetailModal from './ApplicationDetailModal.vue'

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
/* 引入共享样式 */
@import '../common/shared-styles.css';

/* 状态徽章特有样式 */
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

/* 申请详情模态框特有样式 */
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

.description,
.review-comment {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  line-height: 1.6;
}

.review-comment {
  background-color: #fff3cd;
  border-left: 4px solid #ffc107;
}

/* 大尺寸模态框 */
.modal-content.large {
  max-width: 1000px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }

  .modal-content.large {
    width: 95%;
    margin: 20px;
  }
}

/* 操作按钮组优化 */
.action-buttons {
  display: flex;
  gap: 6px;
  justify-content: center;
  align-items: center;
  flex-wrap: nowrap;
}

.action-buttons .small-btn {
  width: 32px;
  height: 32px;
  min-width: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border-radius: 4px;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.action-buttons .small-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 操作列宽度设置 */
.application-table th:last-child,
.application-table td:last-child {
  width: 140px;
  min-width: 140px;
  text-align: center;
}

@media (max-width: 480px) {
  .action-buttons {
    gap: 3px;
  }

  .action-buttons .small-btn {
    width: 26px;
    height: 26px;
    min-width: 26px;
    font-size: 11px;
  }
}
</style>