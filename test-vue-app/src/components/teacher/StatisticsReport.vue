<template>
  <div class="page-content">
    <div class="page-title">
      <span>统计报表</span>
      <button class="btn" @click="exportExcel">
        <font-awesome-icon :icon="['fas', 'download']" /> 导出Excel
      </button>
    </div>

    <!-- 筛选区域 -->
    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">所在系:</span>
        <select v-model="filters.department">
          <option value="all">全部</option>
          <option value="cs">计算机科学系</option>
          <option value="se">软件工程系</option>
          <option value="ai">人工智能系</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">专业:</span>
        <select v-model="filters.major">
          <option value="all">全部</option>
          <option value="cs">计算机科学与技术</option>
          <option value="se">软件工程</option>
          <option value="ai">人工智能</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">学年:</span>
        <select v-model="filters.academicYear">
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
            <tr v-for="stat in statistics" :key="stat.major">
              <td>{{ getMajorText(stat.major) }}</td>
              <td>{{ stat.applicationCount }}</td>
              <td>{{ stat.avgAcademicScore }}</td>
              <td>{{ stat.avgSpecialtyScore }}</td>
              <td>{{ stat.avgComprehensiveScore }}</td>
              <td>{{ stat.avgTotalScore }}</td>
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

const filters = reactive({
  department: 'all',
  major: 'all',
  academicYear: '2023'
})

// 模拟统计数据
const statistics = ref([
  {
    major: 'cs',
    applicationCount: 45,
    avgAcademicScore: 89.2,
    avgSpecialtyScore: 8.5,
    avgComprehensiveScore: 3.2,
    avgTotalScore: 82.3
  },
  {
    major: 'se',
    applicationCount: 38,
    avgAcademicScore: 88.7,
    avgSpecialtyScore: 7.8,
    avgComprehensiveScore: 3.5,
    avgTotalScore: 81.6
  },
  {
    major: 'ai',
    applicationCount: 32,
    avgAcademicScore: 90.5,
    avgSpecialtyScore: 9.2,
    avgComprehensiveScore: 3.0,
    avgTotalScore: 84.2
  }
])

// 计算属性
const filteredStatistics = computed(() => {
  if (filters.major === 'all') {
    return statistics.value
  }
  return statistics.value.filter(stat => stat.major === filters.major)
})

const totalStats = computed(() => {
  const totalApplications = filteredStatistics.value.reduce((sum, stat) => sum + stat.applicationCount, 0)
  const totalAvgScore = filteredStatistics.value.reduce((sum, stat) => sum + stat.avgTotalScore, 0)
  const avgTotalScore = totalAvgScore / filteredStatistics.value.length
  
  return {
    totalApplications,
    approvalRate: 75.6, // 模拟数据
    avgBonusScore: 8.2, // 模拟数据
    maxScore: 92.5, // 模拟数据
    avgTotalScore: avgTotalScore.toFixed(1)
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
  alert('导出Excel功能开发中...')
}

// 生命周期
onMounted(() => {
  // 可以从API加载统计数据
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
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

.help-text {
  font-size: 14px;
  color: #888;
  margin-top: 10px;
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
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