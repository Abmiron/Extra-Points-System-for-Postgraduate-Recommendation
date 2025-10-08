<template>
  <div class="page-content">
    <div class="page-title">
      <span>数据管理</span>
      <div class="page-title-actions">
        <button class="btn btn-outline" @click="showCreateApplicationModal = true">
          <font-awesome-icon :icon="['fas', 'plus']" /> 代创建申请
        </button>
      </div>
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
      <button class="btn btn-outline" @click="batchArchive" :disabled="selectedApplications.length === 0">
        <font-awesome-icon :icon="['fas', 'archive']" /> 归档选中
      </button>
    </div>

    <!-- 数据表格 -->
    <div class="card">
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
            <tr v-for="application in paginatedApplications" :key="application.id">
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
                  <button class="btn-outline btn small-btn" @click="viewHistory(application.id)" title="操作历史">
                    <font-awesome-icon :icon="['fas', 'history']" />
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

    <!-- 申请详情模态框 -->
    <!-- <ApplicationDetailModal 
      v-if="selectedApplication"
      :application="selectedApplication"
      @close="closeDetailModal"
    /> -->

    <!-- 代创建申请模态框 -->
    <!-- <CreateApplicationModal 
      v-if="showCreateApplicationModal"
      @save="createApplication"
      @close="closeCreateModal"
    /> -->
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
// import ApplicationDetailModal from './ApplicationDetailModal.vue'
// import CreateApplicationModal from './CreateApplicationModal.vue'

const showCreateApplicationModal = ref(false)
const selectedApplication = ref(null)
const selectAll = ref(false)
const selectedApplications = ref([])
const currentPage = ref(1)
const pageSize = 10

const filters = reactive({
  studentName: '',
  studentId: '',
  applicationType: 'all',
  status: 'all',
  startDate: '',
  endDate: ''
})

// 模拟申请数据
const applications = ref([
  {
    id: 'APP20230001',
    studentName: '张同学',
    studentId: '12320253211234',
    applicationType: 'academic',
    projectName: '全国大学生程序设计竞赛',
    appliedAt: '2023-08-15T00:00:00Z',
    status: 'approved',
    selfScore: 5.0,
    finalScore: 5.0
  },
  {
    id: 'APP20230002',
    studentName: '李同学',
    studentId: '12320253215678',
    applicationType: 'comprehensive',
    projectName: '优秀志愿者',
    appliedAt: '2023-09-02T00:00:00Z',
    status: 'pending',
    selfScore: 2.0,
    finalScore: null
  },
  {
    id: 'APP20230003',
    studentName: '王同学',
    studentId: '12320253218765',
    applicationType: 'academic',
    projectName: '学术论文发表',
    appliedAt: '2023-07-20T00:00:00Z',
    status: 'rejected',
    selfScore: 3.0,
    finalScore: 0.0
  }
])

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

const searchApplications = () => {
  currentPage.value = 1
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

const batchArchive = () => {
  if (confirm(`确定要归档选中的 ${selectedApplications.value.length} 个申请吗？`)) {
    applications.value = applications.value.filter(app => !selectedApplications.value.includes(app.id))
    selectedApplications.value = []
    selectAll.value = false
    alert('选中申请已归档')
  }
}

const viewApplication = (application) => {
  selectedApplication.value = application
}

const editApplication = (application) => {
  alert(`编辑申请 ${application.id}`)
}

const viewHistory = (applicationId) => {
  alert(`查看申请 ${applicationId} 的历史记录`)
}

const createApplication = (applicationData) => {
  const newApplication = {
    id: 'APP' + Date.now(),
    ...applicationData,
    appliedAt: new Date().toISOString(),
    status: 'pending'
  }
  applications.value.push(newApplication)
  closeCreateModal()
  alert('申请创建成功')
}

const closeDetailModal = () => {
  selectedApplication.value = null
}

const closeCreateModal = () => {
  showCreateApplicationModal.value = false
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

// 生命周期
onMounted(() => {
  // 可以从API加载申请数据
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
</style>

<style>
/* 引入共享样式 */
@import '../common/shared-styles.css';
</style>