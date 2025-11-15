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
        <div class="stat-note">(满分: 15分)</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">综合表现成绩</div>
        <div class="stat-value">{{ statistics.comprehensiveScore }}</div>
        <div class="stat-note">(满分: 5分)</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">推免综合成绩</div>
        <div class="stat-value">{{ statistics.totalScore }}</div>
        <div class="stat-note">专业排名: {{ statistics.ranking }}</div>
      </div>
    </div>

    <!-- 学术专长成绩明细 -->
    <div class="card" :class="{ 'loading-content': loading }">
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
              <td>{{ item.finalScore || item.selfScore }}</td>
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
    <div class="card" :class="{ 'loading-content': loading }">
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
              <td>{{ item.finalScore || item.selfScore }}</td>
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
  ranking: '-'
})

// 计算属性
const academicApplications = computed(() => {
  return applications.value.filter(app =>
    app.applicationType === 'academic' && app.status === 'approved'
  )
})

const comprehensiveApplications = computed(() => {
  return applications.value.filter(app =>
    app.applicationType === 'comprehensive' && app.status === 'approved'
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
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const loadStatistics = async () => {
  loading.value = true
  error.value = null
  
  try {
    if (!authStore.isAuthenticated) {
      error.value = '用户未登录'
      return
    }
    
    // 调试：查看用户信息
    console.log('当前用户:', authStore.user)
    
    // 使用正确的学生学号字段（studentId）而不是用户ID（id）
    const studentId = authStore.user.studentId || 'student'
    console.log('使用的学生ID:', studentId)
    
    // 获取学生的所有申请
    console.log('开始获取申请记录...')
    await applicationsStore.fetchApplications({ studentId })
    applications.value = applicationsStore.applications
    console.log('获取到的申请记录:', applications.value)
    
    // 获取加分统计数据
    console.log('开始获取加分统计数据...')
    const statsData = await applicationsStore.fetchStatistics(studentId)
    console.log('获取到的加分统计数据:', statsData)
    
    // 更新统计信息
    // 注意：后端返回的是下划线命名，前端使用的是驼峰式命名
    statistics.academicScore = statsData.academic_score || 0
    statistics.gpa = statsData.gpa || 0
    statistics.specialtyScore = statsData.specialty_score || 0
    statistics.comprehensiveScore = statsData.comprehensive_score || 0
    statistics.totalScore = statsData.total_score || 0
    statistics.ranking = statsData.ranking || '-'
    
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

.loading-content {
  opacity: 0.5;
  pointer-events: none;
}

.loading-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.loading-spinner {
  border: 4px solid rgba(0, 51, 102, 0.1);
  border-left-color: #003366;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 16px;
  color: #003366;
  font-size: 16px;
  font-weight: 500;
}
</style>