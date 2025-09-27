<template>
  <div class="page-content">
    <div class="page-title">
      <span>加分统计</span>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
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

    <!-- 成绩分布图表区域 -->
    <div class="card">
      <div class="card-title">成绩分布</div>
      <div class="chart-container">
        <div class="chart-placeholder">
          <font-awesome-icon :icon="['fas', 'chart-bar']" size="3x" />
          <p>成绩分布图表</p>
          <p class="help-text">此处将显示可视化成绩分布图表</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

const applications = ref([])

const statistics = reactive({
  academicScore: 92.5,
  gpa: 3.85,
  specialtyScore: 12.5,
  comprehensiveScore: 3.5,
  totalScore: 86.5,
  ranking: '5/120'
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

const calculateStatistics = () => {
  // 计算学术专长总分
  statistics.specialtyScore = academicApplications.value.reduce((total, app) => {
    return total + (app.finalScore || app.selfScore || 0)
  }, 0)
  
  // 计算综合表现总分
  statistics.comprehensiveScore = comprehensiveApplications.value.reduce((total, app) => {
    return total + (app.finalScore || app.selfScore || 0)
  }, 0)
  
  // 计算推免综合成绩（这里是一个简化公式）
  statistics.totalScore = statistics.academicScore * 0.8 + 
                         statistics.specialtyScore + 
                         statistics.comprehensiveScore
}

// 生命周期
onMounted(() => {
  // 从本地存储加载数据
  const savedApplications = JSON.parse(localStorage.getItem('studentApplications') || '[]')
  applications.value = savedApplications
  
  // 计算统计信息
  calculateStatistics()
})
</script>

<style scoped>
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

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-approved {
  background-color: #eafaf1;
  color: #27ae60;
}

.no-data {
  text-align: center;
  color: #666;
  padding: 40px;
}

.help-text {
  font-size: 14px;
  color: #888;
  margin-top: 10px;
}

@media (max-width: 768px) {
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