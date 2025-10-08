<template>
  <div class="page-content">
    <div class="page-title">
      <span>待审核申请</span>
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
        <span class="filter-label">时间段:</span>
        <input type="date" class="form-control small" v-model="filters.startDate">
        至 <input type="date" class="form-control small" v-model="filters.endDate">
      </div>
      <button class="btn" @click="applyFilters">应用筛选</button>
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
              <td>
                <button class="btn-outline btn small-btn" @click="reviewApplication(application)">
                  <font-awesome-icon :icon="['fas', 'eye']" /> 审核
                </button>
              </td>
            </tr>
            <tr v-if="paginatedApplications.length === 0">
              <td colspan="8" class="no-data">暂无待审核申请</td>
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

    <!-- 审核详情模态框 -->
    <ReviewDetailModal v-if="selectedApplication" :application="selectedApplication" @approve="handleApprove"
      @reject="handleReject" @close="closeReviewModal" />
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
    const dateMatch = !filters.startDate || !filters.endDate ||
      (new Date(app.appliedAt) >= new Date(filters.startDate) &&
        new Date(app.appliedAt) <= new Date(filters.endDate))

    return departmentMatch && majorMatch && typeMatch && dateMatch
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

const reviewApplication = (application) => {
  console.log('点击审核按钮，申请信息:', application)
  selectedApplication.value = application
  console.log('selectedApplication 已设置:', selectedApplication.value)
}

const handleApprove = (applicationId, finalScore, comment) => {
  // 更新申请状态为已通过
  const application = applications.value.find(app => app.id === applicationId)
  if (application) {
    application.status = 'approved'
    application.finalScore = finalScore
    application.reviewComment = comment
    application.reviewedAt = new Date().toISOString()
    application.reviewedBy = '当前教师'

    // 更新本地存储
    updateLocalStorage()
  }

  closeReviewModal()
  alert('申请已通过审核')
}

const handleReject = (applicationId, comment) => {
  // 更新申请状态为已驳回
  const application = applications.value.find(app => app.id === applicationId)
  if (application) {
    application.status = 'rejected'
    application.finalScore = 0
    application.reviewComment = comment
    application.reviewedAt = new Date().toISOString()
    application.reviewedBy = '当前教师'

    // 更新本地存储
    updateLocalStorage()
  }

  closeReviewModal()
  alert('申请已驳回')
}

const closeReviewModal = () => {
  selectedApplication.value = null
}

const updateLocalStorage = () => {
  // 更新本地存储中的申请数据
  localStorage.setItem('studentApplications', JSON.stringify(applications.value))
}

// 生命周期
onMounted(() => {
  // 从本地存储加载待审核的申请数据
  const savedApplications = JSON.parse(localStorage.getItem('studentApplications') || '[]')
  applications.value = savedApplications.filter(app => app.status === 'pending')

  if (savedApplications.length === 0) {
    // 如果没有数据，创建模拟数据
    const mockApplications = [
      {
        id: 'app001',
        studentName: '张三',
        studentId: '2020318001',
        department: 'cs',
        major: 'cs',
        applicationType: 'academic',
        appliedAt: '2024-03-15T10:30:00Z',
        selfScore: 4.5,
        status: 'pending',
        projectName: '全国大学生程序设计竞赛',
        awardDate: '2024-02-20',
        awardLevel: 'national',
        awardType: 'individual',
        description: '在2024年全国大学生程序设计竞赛中获得一等奖，展现了优秀的算法设计和编程能力。',
        files: [
          { name: '获奖证书.jpg', url: 'https://ts4.tc.mm.bing.net/th/id/OIP-C.vk0IckSexDI9OWpO2BieqwHaHa?cb=12&rs=1&pid=ImgDetMain&o=7&rm=3' },
          { name: '比赛成绩单.jpg', url: 'https://img95.699pic.com/excel/40015/8976.jpg!/crop/0x1400a0a0/fw/850/quality/90' }
        ]
      },
      {
        id: 'app002',
        studentName: '李四',
        studentId: '2020318002',
        department: 'se',
        major: 'se',
        applicationType: 'comprehensive',
        appliedAt: '2024-03-16T14:20:00Z',
        selfScore: 3.0,
        status: 'pending',
        projectName: '校级优秀学生干部',
        awardDate: '2024-01-10',
        awardLevel: 'school',
        awardType: 'individual',
        description: '担任班级学习委员，组织多次学习活动，获得校级优秀学生干部称号。',
        files: [
          { name: '优秀学生干部证书.pdf', url: '/certificates/cert002.pdf' }
        ]
      },
      {
        id: 'app003',
        studentName: '王五',
        studentId: '2020318003',
        department: 'ai',
        major: 'ai',
        applicationType: 'academic',
        appliedAt: '2024-03-14T09:15:00Z',
        selfScore: 5.0,
        status: 'pending',
        projectName: '国际人工智能创新大赛',
        awardDate: '2024-03-01',
        awardLevel: 'national',
        awardType: 'team',
        description: '作为团队核心成员参加国际人工智能创新大赛，获得特等奖。',
        files: [
          { name: '获奖证书.pdf', url: '/certificates/cert003.pdf' },
          { name: '项目报告.docx', url: '/certificates/report003.docx' },
          { name: '演示视频.mp4', url: '/certificates/demo003.mp4' }
        ]
      },
      {
        id: 'app004',
        studentName: '赵六',
        studentId: '2020318004',
        department: 'cs',
        major: 'cs',
        applicationType: 'academic',
        appliedAt: '2024-03-17T16:45:00Z',
        selfScore: 2.5,
        status: 'approved',
        finalScore: 2.0,
        reviewComment: '项目符合加分标准，但自评分数偏高，根据规定调整为2.0分。',
        reviewedAt: '2024-03-18T10:20:00Z',
        reviewedBy: '张老师',
        projectName: '省级数学建模竞赛',
        awardDate: '2024-02-28',
        awardLevel: 'provincial',
        awardType: 'team',
        description: '参加省级数学建模竞赛获得二等奖。',
        files: [
          { name: '获奖证书.pdf', url: '/certificates/cert004.pdf' }
        ]
      },
      {
        id: 'app005',
        studentName: '钱七',
        studentId: '2020318005',
        department: 'se',
        major: 'se',
        applicationType: 'comprehensive',
        appliedAt: '2024-03-13T11:10:00Z',
        selfScore: 4.0,
        status: 'rejected',
        finalScore: 0,
        reviewComment: '申请材料不完整，缺少必要的证明文件，请补充后重新提交。',
        reviewedAt: '2024-03-15T15:30:00Z',
        reviewedBy: '李老师',
        projectName: '社会实践优秀个人',
        awardDate: '2024-01-20',
        awardLevel: 'municipal',
        awardType: 'individual',
        description: '参与社会实践活动表现突出，获得市级表彰。',
        files: [
          { name: '社会实践证明.pdf', url: '/certificates/cert005.pdf' }
        ]
      }
    ]

    localStorage.setItem('studentApplications', JSON.stringify(mockApplications))
    applications.value = mockApplications.filter(app => app.status === 'pending')
    console.log('模拟数据已创建，待审核申请:', applications.value)
  } else {
    applications.value = savedApplications.filter(app => app.status === 'pending')
    console.log('加载待审核申请:', applications.value)
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