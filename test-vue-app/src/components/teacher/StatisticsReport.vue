<template>
  <div class="page-content">
    <div class="page-title">
      <span>统计报表</span>
      <div class="page-title-actions">
        <button class="btn btn-outline" @click="exportExcel">
          <font-awesome-icon :icon="['fas', 'download']" /> 导出Excel
        </button>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">所在系:</span>
        <select class="form-control" v-model="filters.department">
          <option value="all">全部</option>
          <option value="cs">计算机科学系</option>
          <option value="se">软件工程系</option>
          <option value="ai">人工智能系</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">专业:</span>
        <select class="form-control" v-model="filters.major">
          <option value="all">全部</option>
          <option value="cs">计算机科学与技术</option>
          <option value="se">软件工程</option>
          <option value="ai">人工智能</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">学年:</span>
        <select class="form-control" v-model="filters.academicYear">
          <option value="2023">2023-2024</option>
          <option value="2022">2022-2023</option>
          <option value="2021">2021-2022</option>
        </select>
      </div>
      <button class="btn" @click="generateReport">生成报表</button>
    </div>

    <!-- 统计图表 -->
    <div class="card">
      <div class="card-title">推免成绩分布</div>
      <div class="chart-container">
        <div class="chart-placeholder">
          <font-awesome-icon :icon="['fas', 'chart-bar']" size="3x" />
          <p>成绩分布图表</p>
          <p class="help-text">此处将显示可视化成绩分布图表</p>
        </div>
      </div>
    </div>

    <!-- 统计数据表格 -->
    <div class="card">
      <div class="card-title">推免成绩统计表</div>
      <div class="table-container">
        <table class="application-table">
          <thead>
            <tr>
              <th>专业</th>
              <th>申请人数</th>
              <th>平均学业成绩</th>
              <th>平均学术专长加分</th>
              <th>平均综合表现加分</th>
              <th>平均推免综合成绩</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="stat in filteredStatistics" :key="stat.major">
              <td>{{ getMajorText(stat.major) }}</td>
              <td>{{ stat.applicationCount }}</td>
              <td>{{ stat.avgAcademicScore }}</td>
              <td>{{ stat.avgSpecialtyScore }}</td>
              <td>{{ stat.avgComprehensiveScore }}</td>
              <td>{{ stat.avgTotalScore }}</td>
            </tr>
            <tr v-if="filteredStatistics.length === 0">
              <td colspan="6" class="no-data">暂无统计数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 详细统计信息 -->
    <div class="card">
      <div class="card-title">详细统计信息</div>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">总申请人数</div>
          <div class="stat-value">{{ totalStats.totalApplications }}</div>
          <div class="stat-note">本学年申请总数</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">通过率</div>
          <div class="stat-value">{{ totalStats.approvalRate }}%</div>
          <div class="stat-note">申请通过比例</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">平均加分</div>
          <div class="stat-value">{{ totalStats.avgBonusScore }}</div>
          <div class="stat-note">平均加分分数</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">最高分</div>
          <div class="stat-value">{{ totalStats.maxScore }}</div>
          <div class="stat-note">最高推免成绩</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useApplicationsStore } from '../../stores/applications'

const applicationsStore = useApplicationsStore()
const filters = reactive({
  department: 'all',
  major: 'all',
  academicYear: '2023'
})

// 计算属性 - 使用store数据进行统计
const statistics = computed(() => {
  const allApplications = applicationsStore.applications
  
  // 根据专业分组统计
  const majorStats = {}
  
  allApplications.forEach(app => {
    const major = app.major || 'other'
    if (!majorStats[major]) {
      majorStats[major] = {
        major,
        applicationCount: 0,
        totalAcademicScore: 0,
        totalSpecialtyScore: 0,
        totalComprehensiveScore: 0,
        totalScore: 0
      }
    }
    
    majorStats[major].applicationCount++
    majorStats[major].totalAcademicScore += parseFloat(app.academicScore || 0)
    majorStats[major].totalSpecialtyScore += parseFloat(app.specialtyScore || 0)
    majorStats[major].totalComprehensiveScore += parseFloat(app.comprehensiveScore || 0)
    majorStats[major].totalScore += parseFloat(app.finalScore || 0)
  })
  
  // 计算平均值并格式化为数组
  return Object.values(majorStats).map(stat => ({
    major: stat.major,
    applicationCount: stat.applicationCount,
    avgAcademicScore: (stat.totalAcademicScore / stat.applicationCount).toFixed(1),
    avgSpecialtyScore: (stat.totalSpecialtyScore / stat.applicationCount).toFixed(1),
    avgComprehensiveScore: (stat.totalComprehensiveScore / stat.applicationCount).toFixed(1),
    avgTotalScore: (stat.totalScore / stat.applicationCount).toFixed(1)
  }))
})

// 计算属性
const filteredStatistics = computed(() => {
  if (filters.major === 'all') {
    return statistics.value
  }
  return statistics.value.filter(stat => stat.major === filters.major)
})

const totalStats = computed(() => {
  const totalApplications = filteredStatistics.value.reduce((sum, stat) => sum + stat.applicationCount, 0)
  const approvedApps = applicationsStore.applications.filter(app => app.status === 'approved')
  const approvalRate = totalApplications > 0 ? 
    (approvedApps.length / totalApplications * 100).toFixed(1) : 0
  
  // 计算平均加分
  const bonusScores = applicationsStore.applications.map(app => {
    const specialty = parseFloat(app.specialtyScore || 0)
    const comprehensive = parseFloat(app.comprehensiveScore || 0)
    return specialty + comprehensive
  }).filter(score => !isNaN(score))
  const avgBonusScore = bonusScores.length > 0 ? 
    (bonusScores.reduce((sum, score) => sum + score, 0) / bonusScores.length).toFixed(1) : 0
  
  // 计算最高分数
  const scores = applicationsStore.applications.map(app => parseFloat(app.finalScore || 0)).filter(score => !isNaN(score))
  const maxScore = scores.length > 0 ? Math.max(...scores) : 0
  
  // 计算平均总分
  const avgTotalScore = filteredStatistics.value.length > 0 ? 
    (filteredStatistics.value.reduce((sum, stat) => sum + parseFloat(stat.avgTotalScore), 0) / filteredStatistics.value.length).toFixed(1) : 0
  
  return {
    totalApplications,
    approvalRate: parseFloat(approvalRate),
    avgBonusScore: parseFloat(avgBonusScore),
    maxScore,
    avgTotalScore: parseFloat(avgTotalScore)
  }
})

// 方法
const getMajorText = (major) => {
  const majors = {
    cs: '计算机科学与技术',
    se: '软件工程',
    ai: '人工智能'
  }
  return majors[major] || major
}

const generateReport = () => {
  alert(`生成 ${filters.academicYear} 学年统计报表`)
}

const exportExcel = () => {
  const reportData = {
    generatedAt: new Date().toISOString(),
    filters: { ...filters },
    statistics: statistics.value,
    totalStats: totalStats.value
  }
  
  const dataStr = JSON.stringify(reportData, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
  
  const exportFileDefaultName = `statistics-report-${new Date().toISOString().split('T')[0]}.json`
  
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
}

// 重新加载数据
const refreshData = () => {
  applicationsStore.loadApplications()
}

// 生命周期
onMounted(() => {
  if (applicationsStore.applications.length === 0) {
    applicationsStore.loadApplications()
  }
})
</script>

<style scoped>
/* 组件特有样式 */
.chart-container {
  padding: 20px;
}

.chart-placeholder {
  height: 300px;
  background-color: #f8f9fa;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-radius: 8px;
  color: #666;
}

.chart-placeholder svg {
  margin-bottom: 15px;
  color: #003366;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  padding: 20px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  border-left: 4px solid #003366;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
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

.help-text {
  font-size: 14px;
  color: #888;
  margin-top: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .stat-card {
    padding: 15px;
  }

  .stat-value {
    font-size: 24px;
  }
}
</style>

<style>
/* 引入共享样式 */
@import '../common/shared-styles.css';
</style>