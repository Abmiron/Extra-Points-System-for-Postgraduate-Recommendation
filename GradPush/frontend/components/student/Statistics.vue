<template>
  <div class="page-content">
    <div class="page-title">
      <span>加分统计</span>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid" :class="{ 'loading-content': loading }">
      <div class="stat-card">
        <div class="stat-label">学业综合成绩</div>
        <div class="stat-value">{{ statistics.academicScore }}</div>
        <div class="stat-note">(推免绩点: {{ statistics.gpa }})</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">学术专长成绩</div>
        <div class="stat-value">{{ statistics.specialtyScore }}</div>
        <div class="stat-note">(满分: {{ systemSettings.specialtyMaxScore }}分)</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">综合表现成绩</div>
        <div class="stat-value">{{ statistics.comprehensiveScore }}</div>
        <div class="stat-note">(满分: {{ systemSettings.performanceMaxScore }}分)</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">推免综合成绩</div>
        <div class="stat-value">{{ statistics.totalScore }}</div>
        <div class="stat-note">专业排名: {{ statistics.ranking }}/{{ statistics.majorTotalStudents }}</div>
      </div>
    </div>

    <!-- 学术专长成绩明细 -->
    <div class="card">
      <div class="card-title">学术专长成绩明细</div>
      <div class="table-container">
        <table class="application-table">
          <thead>
            <tr>
              <th>项目名称</th>
              <th>获奖时间</th>
              <th>级别</th>
              <th>类型</th>
              <th>核定分数</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in academicApplications" :key="item.id">
              <td>{{ item.projectName }}</td>
              <td>{{ formatDate(item.awardDate) }}</td>
              <td>{{ getLevelText(item.awardLevel) }}</td>
              <td>{{ item.awardType === 'individual' ? '个人' : '团队' }}</td>
              <td>{{ item.status === 'rejected' ? 0 : (item.finalScore ?? item.selfScore) }}</td>
              <td>
                <span :class="`status-badge status-${item.status}`">
                  {{ getStatusText(item.status) }}
                </span>
              </td>
            </tr>
            <tr v-if="academicApplications.length === 0">
              <td colspan="6" class="no-data">暂无学术专长申请记录</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 综合表现成绩明细 -->
    <div class="card">
      <div class="card-title">综合表现成绩明细</div>
      <div class="table-container">
        <table class="application-table">
          <thead>
            <tr>
              <th>项目名称</th>
              <th>获奖时间</th>
              <th>级别</th>
              <th>类型</th>
              <th>核定分数</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in comprehensiveApplications" :key="item.id">
              <td>{{ item.projectName }}</td>
              <td>{{ formatDate(item.awardDate) }}</td>
              <td>{{ getLevelText(item.awardLevel) }}</td>
              <td>{{ item.awardType === 'individual' ? '个人' : '团队' }}</td>
              <td>{{ item.status === 'rejected' ? 0 : (item.finalScore ?? item.selfScore) }}</td>
              <td>
                <span :class="`status-badge status-${item.status}`">
                  {{ getStatusText(item.status) }}
                </span>
              </td>
            </tr>
            <tr v-if="comprehensiveApplications.length === 0">
              <td colspan="6" class="no-data">暂无综合表现申请记录</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 加载状态指示器 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载中...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth.js'
import { useApplicationsStore } from '../../stores/applications.js'
import api from '../../utils/api.js'

const authStore = useAuthStore()
const applicationsStore = useApplicationsStore()

const applications = ref([])
const loading = ref(false)
const error = ref(null)

const statistics = reactive({
  academicScore: 0,
  gpa: 0,
  specialtyScore: 0,
  comprehensiveScore: 0,
  totalScore: 0,
  ranking: '-',
  majorTotalStudents: 0
})

const systemSettings = reactive({
  specialtyMaxScore: 15,
  performanceMaxScore: 5,
  academicScoreWeight: 80
})

// 计算属性
const academicApplications = computed(() => {
  // 学术专长包括：academic(旧类型)、research、competition、innovation
  return applications.value.filter(app =>
    (app.applicationType === 'academic' ||
      app.applicationType === 'research' ||
      app.applicationType === 'competition' ||
      app.applicationType === 'innovation') &&
    app.status === 'approved'
  )
})

const comprehensiveApplications = computed(() => {
  // 综合表现包括：comprehensive(旧类型)、international_internship、military_service、volunteer、social_work、sports、honor_title
  return applications.value.filter(app =>
    (app.applicationType === 'comprehensive' ||
      app.applicationType === 'international_internship' ||
      app.applicationType === 'military_service' ||
      app.applicationType === 'volunteer' ||
      app.applicationType === 'social_work' ||
      app.applicationType === 'sports' ||
      app.applicationType === 'honor_title') &&
    app.status === 'approved'
  )
})

// 方法
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

  // 直接使用本地时间显示，因为后端返回的已经是上海时间
  const date = new Date(dateString)

  return date.toLocaleDateString('zh-CN')
}

const loadSystemSettings = async () => {
  try {
    // 获取系统设置，包括满分值
    const settingsData = await api.getPublicSystemInfo()
    systemSettings.specialtyMaxScore = settingsData.data.specialtyMaxScore
    systemSettings.performanceMaxScore = settingsData.data.performanceMaxScore
    systemSettings.academicScoreWeight = settingsData.data.academicScoreWeight
  } catch (err) {
    console.error('加载系统设置失败:', err)
    // 使用默认值
    systemSettings.specialtyMaxScore = 15
    systemSettings.performanceMaxScore = 5
    systemSettings.academicScoreWeight = 0.7
  }
}

const loadStatistics = async () => {
  loading.value = true
  error.value = null

  try {
    if (!authStore.isAuthenticated) {
      error.value = '用户未登录'
      return
    }

    // 获取系统设置
    await loadSystemSettings()

    // 调试：查看用户信息
    //console.log('当前用户:', authStore.user)

    // 使用正确的学生学号字段（studentId）而不是用户ID（id）
    const studentId = authStore.user.studentId || 'student'
    //console.log('使用的学生ID:', studentId)

    // 获取学生的所有申请
    //console.log('开始获取申请记录...')
    const appData = await applicationsStore.fetchApplications({ studentId })
    applications.value = appData
    //console.log('获取到的申请记录:', applications.value)

    // 获取加分统计数据
    //console.log('开始获取加分统计数据...')
    const statsData = await applicationsStore.fetchStatistics(studentId)
    //console.log('获取到的加分统计数据:', statsData)

    // 更新统计信息
    // 注意：后端返回的是下划线命名，前端使用的是驼峰式命名
    statistics.academicScore = statsData.academic_score || 0
    statistics.gpa = statsData.gpa || 0
    statistics.specialtyScore = statsData.specialty_score || 0
    statistics.comprehensiveScore = statsData.comprehensive_performance_total || 0
    statistics.totalScore = statsData.total_score || statsData.comprehensive_score || 0
    statistics.ranking = statsData.ranking || '-'
    statistics.majorTotalStudents = statsData.major_total_students || 0

  } catch (err) {
    console.error('加载统计数据失败:', err)
    error.value = '加载统计数据失败，请刷新页面重试'
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  loadStatistics()
})
</script>

<style scoped>
/* 引入共享样式 */
@import '../common/shared-styles.css';

/* 统计卡片特有样式 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  text-align: center;
  border-left: 4px solid #003366;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #003366;
  margin: 10px 0;
}

.stat-label {
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.stat-note {
  color: #888;
  font-size: 12px;
  margin-top: 5px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

/* 加载状态样式 */
.page-content {
  position: relative;
}

</style>