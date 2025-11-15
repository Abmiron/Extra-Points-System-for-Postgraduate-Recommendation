<template>
  <div class="page-content">
    <div class="page-title">
      <span>统计报表</span>
    </div>

    <!-- 筛选区域 -->
    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">所在系:</span>
        <select class="form-control" v-model="filters.department" @change="refreshData">
          <option value="all">全部</option>
          <option value="cs">计算机科学系</option>
          <option value="se">软件工程系</option>
          <option value="ai">人工智能系</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">专业:</span>
        <select class="form-control" v-model="filters.major" @change="refreshData">
          <option value="all">全部</option>
          <option value="cs">计算机科学与技术</option>
          <option value="se">软件工程</option>
          <option value="ai">人工智能</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">学年:</span>
        <select class="form-control" v-model="filters.academicYear" @change="refreshData">
          <option value="2023">2023-2024</option>
          <option value="2022">2022-2023</option>
          <option value="2021">2021-2022</option>
        </select>
      </div>
      <button class="btn" @click="generateReport">生成报表</button>
    </div>

    <!-- 成绩分布总表 -->
    <div class="card">
      <div class="card-title">学生成绩分布总表</div>
      <div class="table-container">
        <table class="application-table comprehensive-table">
          <thead>
            <tr>
              <!-- A-H: 学生基本信息 -->
              <th>序号</th>
              <th>系</th>
              <th>所在专业</th>
              <th>学号</th>
              <th>姓名</th>
              <th>性别</th>
              <th>CET4成绩</th>
              <th>CET6成绩</th>
              <!-- I-J: 学业综合成绩（占总分80%） -->
              <th>推免绩点(满分4分)</th>
              <th>换算后的成绩(满分100分)</th>
              <!-- K-S: 学术专长成绩（占总分12%） -->
              <th>学术专长项目</th>
              <th>学术专长获奖时间</th>
              <th>学术专长奖项级别</th>
              <th>学术专长个人或集体</th>
              <th>学术专长集体奖项排序</th>
              <th>学术专长自评加分</th>
              <th>学术专长加分依据</th>
              <th>学术专长学院核定加分</th>
              <th>学术专长学院核定总分</th>
              <!-- T-AB: 综合表现加分（占总分8%） -->
              <th>综合表现项目</th>
              <th>综合表现获奖时间</th>
              <th>综合表现奖项级别</th>
              <th>综合表现个人或集体</th>
              <th>综合表现集体奖项排序</th>
              <th>综合表现自评加分</th>
              <th>综合表现加分依据</th>
              <th>综合表现学院核定加分</th>
              <th>综合表现学院核定总分</th>
              <!-- AC-AF: 总分与排名 -->
              <th>考核综合成绩总分</th>
              <th>综合成绩</th>
              <th>专业成绩排名</th>
              <th>排名人数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(student, index) in filteredStudents" :key="`${student.studentId}-${index}`">
              <!-- A-H: 学生基本信息 -->
              <td v-if="student.isFirstRow">{{ student.sequence }}</td>
              <td v-else></td>
              <td v-if="student.isFirstRow">{{ getDepartmentText(student.department) }}</td>
              <td v-else></td>
              <td v-if="student.isFirstRow">{{ getMajorText(student.major) }}</td>
              <td v-else></td>
              <td v-if="student.isFirstRow">{{ student.studentId }}</td>
              <td v-else></td>
              <td v-if="student.isFirstRow">{{ student.studentName }}</td>
              <td v-else></td>
              <td v-if="student.isFirstRow">{{ student.gender }}</td>
              <td v-else></td>
              <td v-if="student.isFirstRow">{{ student.cet4Score }}</td>
              <td v-else></td>
              <td v-if="student.isFirstRow">{{ student.cet6Score }}</td>
              <td v-else></td>
              <!-- I-J: 学业综合成绩（占总分80%） -->
              <td v-if="student.isFirstRow">{{ student.gpa ? student.gpa.toFixed(3) : 0 }}</td>
              <td v-else></td>
              <td v-if="student.isFirstRow">{{ student.academicScore ? student.academicScore.toFixed(2) : 0 }}</td>
              <td v-else></td>
              <!-- K-S: 学术专长成绩（占总分12%） -->
              <td v-if="student.academicItem">
               {{ student.academicItem.projectName }}
              </td>
              <td v-else></td>
              <td v-if="student.academicItem">
                {{ student.academicItem.awardTime }}
              </td>
              <td v-else></td>
              <td v-if="student.academicItem">
                {{ student.academicItem.awardLevel }}
              </td>
              <td v-else></td>
              <td v-if="student.academicItem">
                {{ student.academicItem.individualCollective }}
              </td>
              <td v-else></td>
              <td v-if="student.academicItem">
                {{ student.academicItem.authorOrder }}
              </td>
              <td v-else></td>
              <td v-if="student.academicItem">
                {{ student.academicItem.selfEvalScore ? student.academicItem.selfEvalScore.toFixed(2) : 0 }}
              </td>
              <td v-else></td>
              <td v-if="student.academicItem">
                {{ student.academicItem.scoreBasis }}
              </td>
              <td v-else></td>
              <td v-if="student.academicItem">
                {{ student.academicItem.collegeApprovedScore ? student.academicItem.collegeApprovedScore.toFixed(2) : 0 }}
              </td>
              <td v-else></td>
              <td v-if="student.isFirstRow">
                {{ student.specialtyScore ? student.specialtyScore.toFixed(2) : 0 }}
              </td>
              <td v-else></td>
              <!-- T-AB: 综合表现加分（占总分8%） -->
              <td v-if="student.comprehensiveItem">
               {{ student.comprehensiveItem.projectName }}
              </td>
              <td v-else></td>
              <td v-if="student.comprehensiveItem">
                {{ student.comprehensiveItem.awardTime }}
              </td>
              <td v-else></td>
              <td v-if="student.comprehensiveItem">
                {{ student.comprehensiveItem.awardLevel }}
              </td>
              <td v-else></td>
              <td v-if="student.comprehensiveItem">
                {{ student.comprehensiveItem.individualCollective }}
              </td>
              <td v-else></td>
              <td v-if="student.comprehensiveItem">
                {{ student.comprehensiveItem.authorOrder }}
              </td>
              <td v-else></td>
              <td v-if="student.comprehensiveItem">
                {{ student.comprehensiveItem.selfEvalScore ? student.comprehensiveItem.selfEvalScore.toFixed(2) : 0 }}
              </td>
              <td v-else></td>
              <td v-if="student.comprehensiveItem">
                {{ student.comprehensiveItem.scoreBasis }}
              </td>
              <td v-else></td>
              <td v-if="student.comprehensiveItem">
                {{ student.comprehensiveItem.collegeApprovedScore ? student.comprehensiveItem.collegeApprovedScore.toFixed(2) : 0 }}
              </td>
              <td v-else></td>
              <td v-if="student.isFirstRow">
                {{ student.comprehensiveScore ? student.comprehensiveScore.toFixed(2) : 0 }}
              </td>
              <td v-else></td>
              <!-- AC-AF: 总分与排名 -->
              <td v-if="student.isFirstRow">{{ student.totalComprehensiveScore ? student.totalComprehensiveScore.toFixed(2) : 0 }}</td>
              <td v-else></td>
              <td v-if="student.isFirstRow">{{ student.finalScore ? student.finalScore.toFixed(2) : 0 }}</td>
              <td v-else></td>
              <td v-if="student.isFirstRow">{{ student.majorRanking }}</td>
              <td v-else></td>
              <td v-if="student.isFirstRow">{{ student.majorTotalStudents }}</td>
              <td v-else></td>
            </tr>
            <tr v-if="filteredStudents.length === 0">
              <td colspan="34" class="no-data">暂无数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useApplicationsStore } from '../../stores/applications'
import * as XLSX from 'xlsx'


const applicationsStore = useApplicationsStore()
const filters = reactive({
  department: 'all',
  major: 'all',
  academicYear: '2023'
})

// 学生排名数据
const studentsRanking = ref([])
// 所有申请记录
const allApplications = ref([])

// 从API获取学生排名数据
const fetchStudentsRanking = async () => {
  try {
    // 获取所有申请记录
    await applicationsStore.fetchApplications()
    allApplications.value = applicationsStore.applications
    
    // 按学生分组整理数据
    const studentMap = new Map()
    
    // 遍历所有申请记录，按学生ID分组
    allApplications.value.forEach(application => {
      const studentId = application.studentId
      if (!studentMap.has(studentId)) {
        studentMap.set(studentId, {
          studentId: application.studentId,
          studentName: application.studentName,
          department: application.department,
          major: application.major,
          gender: application.gender || '',
          cet4Score: 0,
          cet6Score: 0,
          gpa: 0,
          academicScore: 0,
          academicItems: [],
          comprehensiveItems: [],
          specialtyScore: 0,
          comprehensiveScore: 0,
          totalScore: 0,
          finalComprehensiveScore: 0,
          academicWeighted: 0,
          sequence: 0,
          finalScore: 0,
          majorRanking: 0,
          majorTotalStudents: 0
        })
      }
      
      const studentData = studentMap.get(studentId)
      
      // 根据申请类型添加到对应的项目列表
      const item = {
        projectName: application.projectName,
        awardTime: application.awardDate,
        awardLevel: application.awardLevel,
        individualCollective: application.awardType === 'individual' ? '个人' : '团队',
        authorOrder: application.authorOrder || '',
        selfEvalScore: application.selfScore || 0,
        scoreBasis: '',
        collegeApprovedScore: application.finalScore || 0,
        totalScore: application.finalScore || 0
      }
      
      if (application.applicationType === 'academic') {
        studentData.academicItems.push(item)
        studentData.specialtyScore += item.totalScore
      } else if (application.applicationType === 'comprehensive') {
        studentData.comprehensiveItems.push(item)
        studentData.comprehensiveScore += item.totalScore
      }
      
      // 更新总分
      studentData.totalScore = studentData.specialtyScore + studentData.comprehensiveScore
    })
    
    // 转换为数组并按总分排序
    let students = Array.from(studentMap.values())
    
    // 如果需要按系和专业筛选
    if (filters.department !== 'all') {
      students = students.filter(student => student.department === filters.department)
    }
    if (filters.major !== 'all') {
      students = students.filter(student => student.major === filters.major)
    }
    
    // 按总分降序排序
    students.sort((a, b) => b.totalScore - a.totalScore)
    
    // 为每个学生添加排名
    students.forEach((student, index) => {
      student.sequence = index + 1
      student.majorRanking = index + 1
      student.majorTotalStudents = students.length
    })
    
    // 转换为表格行数据
    let formattedStudents = []
    students.forEach(student => {
      // 获取学术专长项目和综合表现项目的最大数量
      const maxItemsCount = Math.max(student.academicItems.length, student.comprehensiveItems.length)
      
      // 循环创建行，让学术专长项目和综合表现项目按索引一一对应显示
      for (let i = 0; i < maxItemsCount; i++) {
        const row = {
          ...student,
          isFirstRow: i === 0, // 只有第一行显示基本信息
          itemType: 'both', // 每一行都可能同时显示两种类型的项目
          // 获取当前索引的学术专长项目，如果不存在则使用空对象
          academicItem: student.academicItems[i] || {
            projectName: '',
            awardTime: '',
            awardLevel: '',
            individualCollective: '',
            authorOrder: '',
            selfEvalScore: 0,
            scoreBasis: '',
            collegeApprovedScore: 0,
            totalScore: 0
          },
          // 获取当前索引的综合表现项目，如果不存在则使用空对象
          comprehensiveItem: student.comprehensiveItems[i] || {
            projectName: '',
            awardTime: '',
            awardLevel: '',
            individualCollective: '',
            authorOrder: '',
            selfEvalScore: 0,
            scoreBasis: '',
            collegeApprovedScore: 0,
            totalScore: 0
          }
        }
        formattedStudents.push(row)
      }
    })
    
    studentsRanking.value = formattedStudents
  } catch (error) {
    console.error('获取学生排名失败:', error)
    studentsRanking.value = []
  }
}

// 计算属性 - 筛选后的学生排名
const filteredStudents = computed(() => {
  let students = studentsRanking.value
  
  if (filters.department !== 'all') {
    students = students.filter(student => student.department === filters.department)
  }
  
  if (filters.major !== 'all') {
    students = students.filter(student => student.major === filters.major)
  }
  
  return students
})

// 计算属性 - 总体统计信息
const totalStats = computed(() => {
  const allApps = applicationsStore.applications
  const totalApplications = allApps.length
  
  // 计算学生总数
  const studentIds = new Set(allApps.map(app => app.studentId))
  const totalStudents = studentIds.size
  
  // 计算平均总分
  const avgTotalScore = filteredStudents.value.length > 0 ? 
    (filteredStudents.value.reduce((sum, student) => sum + student.totalScore, 0) / filteredStudents.value.length) : 0
  
  // 计算最高分数
  const maxScore = filteredStudents.value.length > 0 ? 
    Math.max(...filteredStudents.value.map(student => student.totalScore)) : 0
  
  return {
    totalStudents,
    totalApplications,
    avgTotalScore,
    maxScore
  }
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

const generateReport = () => {
  if (filteredStudents.value.length === 0) {
    alert('当前没有数据可导出');
    return;
  }

  // 准备导出数据
  const exportData = [];
  
  // 添加表头
  const headers = [
    '序号', '系', '所在专业', '学号', '姓名', '性别', 'CET4成绩', 'CET6成绩',
    '推免绩点(满分4分)', '换算后的成绩(满分100分)',
    '学术专长项目', '学术专长获奖时间', '学术专长奖项级别', '学术专长个人或集体',
    '学术专长集体奖项排序', '学术专长自评加分', '学术专长加分依据',
    '学术专长学院核定加分', '学术专长学院核定总分',
    '综合表现项目', '综合表现获奖时间', '综合表现奖项级别', '综合表现个人或集体',
    '综合表现集体奖项排序', '综合表现自评加分', '综合表现加分依据',
    '综合表现学院核定加分', '综合表现学院核定总分',
    '考核综合成绩总分', '综合成绩', '专业成绩排名', '排名人数'
  ];
  exportData.push(headers);

  // 处理学生数据
  const studentMap = new Map();
  
  // 先按学生ID分组，确保每个学生只处理一次
  filteredStudents.value.forEach(row => {
    const studentId = row.studentId;
    if (!studentMap.has(studentId)) {
      studentMap.set(studentId, {
        studentData: row,
        academicItems: [],
        comprehensiveItems: []
      });
    }
    
    const student = studentMap.get(studentId);
    if (row.academicItem && row.academicItem.projectName) {
      student.academicItems.push(row.academicItem);
    }
    if (row.comprehensiveItem && row.comprehensiveItem.projectName) {
      student.comprehensiveItems.push(row.comprehensiveItem);
    }
  });

  // 将分组后的数据转换为Excel行
  studentMap.forEach(student => {
    const { studentData, academicItems, comprehensiveItems } = student;
    const maxItems = Math.max(academicItems.length, comprehensiveItems.length);
    
    for (let i = 0; i < maxItems; i++) {
      const row = [];
      
      // 基本信息（仅第一行显示）
      if (i === 0) {
        row.push(studentData.sequence);
        row.push(getDepartmentText(studentData.department));
        row.push(getMajorText(studentData.major));
        row.push(studentData.studentId);
        row.push(studentData.studentName);
        row.push(studentData.gender);
        row.push(studentData.cet4Score);
        row.push(studentData.cet6Score);
        row.push(studentData.gpa ? studentData.gpa.toFixed(3) : 0);
        row.push(studentData.academicScore ? studentData.academicScore.toFixed(2) : 0);
      } else {
        // 非第一行基本信息留空
        for (let j = 0; j < 10; j++) {
          row.push('');
        }
      }
      
      // 学术专长信息
      const academicItem = academicItems[i] || {};
      row.push(academicItem.projectName || '');
      row.push(academicItem.awardTime || '');
      row.push(academicItem.awardLevel || '');
      row.push(academicItem.individualCollective || '');
      row.push(academicItem.authorOrder || '');
      row.push(academicItem.selfEvalScore ? academicItem.selfEvalScore.toFixed(2) : 0);
      row.push(academicItem.scoreBasis || '');
      row.push(academicItem.collegeApprovedScore ? academicItem.collegeApprovedScore.toFixed(2) : 0);
      row.push(i === 0 ? (studentData.specialtyScore ? studentData.specialtyScore.toFixed(2) : 0) : '');
      
      // 综合表现信息
      const comprehensiveItem = comprehensiveItems[i] || {};
      row.push(comprehensiveItem.projectName || '');
      row.push(comprehensiveItem.awardTime || '');
      row.push(comprehensiveItem.awardLevel || '');
      row.push(comprehensiveItem.individualCollective || '');
      row.push(comprehensiveItem.authorOrder || '');
      row.push(comprehensiveItem.selfEvalScore ? comprehensiveItem.selfEvalScore.toFixed(2) : 0);
      row.push(comprehensiveItem.scoreBasis || '');
      row.push(comprehensiveItem.collegeApprovedScore ? comprehensiveItem.collegeApprovedScore.toFixed(2) : 0);
      row.push(i === 0 ? (studentData.comprehensiveScore ? studentData.comprehensiveScore.toFixed(2) : 0) : '');
      
      // 总分与排名（仅第一行显示）
      if (i === 0) {
        row.push(studentData.totalComprehensiveScore ? studentData.totalComprehensiveScore.toFixed(2) : 0);
        row.push(studentData.finalScore ? studentData.finalScore.toFixed(2) : 0);
        row.push(studentData.majorRanking);
        row.push(studentData.majorTotalStudents);
      } else {
        // 非第一行总分与排名留空
        for (let j = 0; j < 4; j++) {
          row.push('');
        }
      }
      
      exportData.push(row);
    }
  });

  // 创建工作簿
  const wb = XLSX.utils.book_new();
  
  // 创建工作表
  const ws = XLSX.utils.aoa_to_sheet(exportData);
  
  // 设置列宽
  ws['!cols'] = [
    { wch: 6 },  // 序号
    { wch: 12 }, // 系
    { wch: 15 }, // 所在专业
    { wch: 15 }, // 学号
    { wch: 8 },  // 姓名
    { wch: 6 },  // 性别
    { wch: 10 }, // CET4成绩
    { wch: 15 }, // CET6成绩
    { wch: 15 }, // 推免绩点
    { wch: 18 }, // 换算后的成绩
    { wch: 20 }, // 学术专长项目
    { wch: 15 }, // 学术专长获奖时间
    { wch: 15 }, // 学术专长奖项级别
    { wch: 15 }, // 学术专长个人或集体
    { wch: 18 }, // 学术专长集体奖项排序
    { wch: 15 }, // 学术专长自评加分
    { wch: 20 }, // 学术专长加分依据
    { wch: 18 }, // 学术专长学院核定加分
    { wch: 18 }, // 学术专长学院核定总分
    { wch: 20 }, // 综合表现项目
    { wch: 15 }, // 综合表现获奖时间
    { wch: 15 }, // 综合表现奖项级别
    { wch: 15 }, // 综合表现个人或集体
    { wch: 18 }, // 综合表现集体奖项排序
    { wch: 15 }, // 综合表现自评加分
    { wch: 20 }, // 综合表现加分依据
    { wch: 18 }, // 综合表现学院核定加分
    { wch: 18 }, // 综合表现学院核定总分
    { wch: 18 }, // 考核综合成绩总分
    { wch: 10 }, // 综合成绩
    { wch: 12 }, // 专业成绩排名
    { wch: 10 }  // 排名人数
  ];
  
  // 添加工作表到工作簿
  XLSX.utils.book_append_sheet(wb, ws, '学生成绩分布');
  
  // 生成文件名
  const fileName = `统计报表_${filters.academicYear}学年_${getDepartmentText(filters.department)}_${getMajorText(filters.major)}_${new Date().toISOString().split('T')[0]}.xlsx`;
  
  // 导出文件
  XLSX.writeFile(wb, fileName);
  
  alert(`报表已成功生成并下载：${fileName}`);
}



// 重新加载数据
const refreshData = () => {
  fetchStudentsRanking()
  pagination.value.currentPage = 1
}



// 生命周期
onMounted(async () => {
  await fetchStudentsRanking()
})
</script>

<style scoped>
/* 组件特有样式 */
.table-container {
  overflow-x: auto;
  max-width: 100%;
  margin-bottom: 20px;
}

.application-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1200px;
}

.application-table th,
.application-table td {
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
  font-size: 13px;
}

.application-table th {
  background-color: #f8f9fa;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 10;
  white-space: nowrap;
}

.comprehensive-table th {
  min-width: 100px;
}

.comprehensive-table th:nth-child(1),
.comprehensive-table td:nth-child(1) {
  min-width: 60px;
}

.comprehensive-table th:nth-child(4),
.comprehensive-table td:nth-child(4) {
  min-width: 120px;
}

.comprehensive-table th:nth-child(5),
.comprehensive-table td:nth-child(5) {
  min-width: 80px;
}

.comprehensive-table th:nth-child(11),
.comprehensive-table td:nth-child(11) {
  min-width: 150px;
}

.comprehensive-table th:nth-child(17),
.comprehensive-table td:nth-child(17) {
  min-width: 150px;
}

.comprehensive-table th:nth-child(26),
.comprehensive-table td:nth-child(26) {
  min-width: 150px;
}

.no-data {
  text-align: center;
  color: #6c757d;
  padding: 30px;
}

.card-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e9ecef;
}
</style>

<style>
/* 引入共享样式 */
@import '../common/shared-styles.css';
</style>