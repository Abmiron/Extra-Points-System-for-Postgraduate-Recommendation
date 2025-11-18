<template>
  <div class="page-content">
    <!-- 页面标题 -->
    <div class="page-title">
      <span>成绩管理</span>
    </div>

    <!-- 筛选和搜索区域 -->
    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">学号:</span>
        <input type="text" class="form-control small" v-model="filters.studentId" placeholder="输入学生学号">
      </div>
      <div class="filter-group">
        <span class="filter-label">姓名:</span>
        <input type="text" class="form-control small" v-model="filters.studentName" placeholder="输入学生姓名">
      </div>
      <div class="filter-group">
        <span class="filter-label">学院:</span>
        <input type="text" class="form-control small" v-model="filters.faculty" placeholder="输入学院名称">
      </div>
      <div class="filter-group">
        <span class="filter-label">系:</span>
        <input type="text" class="form-control small" v-model="filters.department" placeholder="输入系名称">
      </div>
      <div class="filter-group">
        <span class="filter-label">专业:</span>
        <input type="text" class="form-control small" v-model="filters.major" placeholder="输入专业名称">
      </div>
      <div class="filter-group">
        <button class="btn btn-outline" @click="resetFilter">清空筛选</button>
      </div>
      <div class="filter-group">
        <button class="btn btn-primary" @click="recalculateComprehensiveScores">重新计算综合成绩</button>
      </div>
    </div>

    <!-- 成绩表格 -->
    <div class="card">
      <div class="card-title">
        <span>成绩管理</span>
      </div>
      <!-- 加载状态指示器 -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">加载中...</div>
      </div>
      <div class="table-container">
        <table class="application-table">
          <thead>
            <tr>
              <th>学号</th>
              <th>姓名</th>
              <th>CET4成绩</th>
              <th>CET6成绩</th>
              <th>GPA</th>
              <th>学业成绩</th>
              <th>学术专长</th>
              <th>综合表现</th>
              <th>考核总分</th>
              <th>综合成绩</th>
              <th>专业排名</th>
              <th>排名人数</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in paginatedScores" :key="student.id">
              <td>{{ student.student_id }}</td>
              <td>{{ student.student_name }}</td>
              <td>{{ student.cet4_score || '-' }}</td>
              <td>{{ student.cet6_score || '-' }}</td>
              <td>{{ student.gpa || '-' }}</td>
              <td>{{ student.academic_score || '-' }}</td>
              <td>{{ student.academic_specialty_total || '-' }}</td>
              <td>{{ student.comprehensive_performance_total || '-' }}</td>
              <td>{{ student.total_score || '-' }}</td>
              <td>{{ student.comprehensive_score || '-' }}</td>
              <td>{{ student.major_ranking || '-' }}</td>
              <td>{{ student.total_students || '-' }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn-outline btn small-btn" @click="openEditModal(student)">
                    <font-awesome-icon :icon="['fas', 'edit']" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="paginatedScores.length === 0">
              <td :colspan="14" class="no-data">暂无成绩数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 分页控件 -->
    <div class="pagination">
      <div class="pagination-info">显示 {{ startIndex + 1 }}-{{ endIndex }} 条，共 {{ total }} 条记录</div>
      <div class="pagination-controls">
        <button class="btn-outline btn" :disabled="currentPage === 1" @click="prevPage">
          <font-awesome-icon :icon="['fas', 'chevron-left']" /> 上一页
        </button>
        <button class="btn-outline btn" :disabled="currentPage >= totalPages" @click="nextPage">
          下一页 <font-awesome-icon :icon="['fas', 'chevron-right']" />
        </button>
      </div>
    </div>

    <!-- 添加/编辑学生模态框 -->
    <div v-if="dialogVisible" class="modal-overlay" @click="dialogVisible = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>编辑成绩</h3>
          <button class="close-btn" @click="dialogVisible = false">
            <font-awesome-icon :icon="['fas', 'times']" />
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">学号</label>
                <input type="text" class="form-control" v-model="formData.student_id" disabled />
              </div>
              <div class="form-group">
                <label class="form-label">姓名</label>
                <input type="text" class="form-control" v-model="formData.student_name" disabled />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">性别</label>
                <select class="form-control" v-model="formData.gender" placeholder="请选择性别">
                  <option value="">请选择性别</option>
                  <option value="男">男</option>
                  <option value="女">女</option>
                </select>
                <div v-if="errors.gender" class="error-message">{{ errors.gender }}</div>
              </div>
              <div class="form-group">
                <label class="form-label">学院</label>
                <input type="text" class="form-control" :value="formData.facultyName" disabled />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">系</label>
                <input type="text" class="form-control" :value="formData.departmentName" disabled />
              </div>
              <div class="form-group">
                <label class="form-label">专业</label>
                <input type="text" class="form-control" :value="formData.majorName" disabled />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">CET4成绩</label>
                <input type="number" class="form-control" v-model="formData.cet4_score" placeholder="请输入CET4成绩" min="0" max="710" step="1" />
                <div v-if="errors.cet4_score" class="error-message">{{ errors.cet4_score }}</div>
              </div>
              <div class="form-group">
                <label class="form-label">CET6成绩</label>
                <input type="number" class="form-control" v-model="formData.cet6_score" placeholder="请输入CET6成绩" min="0" max="710" step="1" />
                <div v-if="errors.cet6_score" class="error-message">{{ errors.cet6_score }}</div>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">GPA</label>
                <input type="number" class="form-control" v-model="formData.gpa" placeholder="请输入GPA" min="0" max="4" step="0.01" />
                <div v-if="errors.gpa" class="error-message">{{ errors.gpa }}</div>
              </div>
              <div class="form-group">
                <label class="form-label">学业成绩</label>
                <input type="number" class="form-control" v-model="formData.academic_score" placeholder="请输入学业成绩" min="0" max="100" step="0.01" />
                <div v-if="errors.academic_score" class="error-message">{{ errors.academic_score }}</div>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">学术专长</label>
                <input type="number" class="form-control" v-model="formData.academic_specialty_total" placeholder="系统自动计算" min="0" max="12" step="0.01" readonly />
                <div class="help-text">由系统根据申请记录自动计算，直接计入综合成绩</div>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">综合表现</label>
                <input type="number" class="form-control" v-model="formData.comprehensive_performance_total" placeholder="系统自动计算" min="0" max="8" step="0.01" readonly />
                <div class="help-text">由系统根据申请记录自动计算，直接计入综合成绩</div>
              </div>
              <div class="form-group">
                <label class="form-label">考核总分</label>
                <input type="number" class="form-control" v-model="formData.total_score" placeholder="系统自动计算" min="0" max="100" step="0.01" readonly />
                <div class="help-text">由系统根据申请记录自动计算</div>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">综合成绩</label>
                <input type="number" class="form-control" v-model="formData.comprehensive_score" placeholder="系统自动计算" min="0" max="100" step="0.01" readonly />
                <div class="help-text">计算方式：学业成绩 * 学业成绩权重 / 100 + 学术专长总分 + 综合表现总分</div>
              </div>
              <div class="form-group">
                <label class="form-label">专业排名</label>
                <input type="number" class="form-control" v-model="formData.major_ranking" placeholder="系统自动计算" min="1" step="1" readonly />
                <div class="help-text">由系统根据申请记录自动计算</div>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">排名人数</label>
                <input type="number" class="form-control" v-model="formData.total_students" placeholder="系统自动计算" min="1" step="1" readonly />
                <div class="help-text">由系统根据申请记录自动计算</div>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="dialogVisible = false">取消</button>
              <button type="submit" class="btn btn-primary">更新</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../utils/api'
import { useApplicationsStore } from '../../stores/applications'

export default {
  name: 'ScoreManagement',
  components: {
  },
  data() {
    return {
      // 表格数据
      scores: [],
      total: 0,
      loading: false,
      // 分页
      currentPage: 1,
      pageSize: 10,
      // 筛选条件
      filters: {
        studentId: '',
        studentName: '',
        faculty: '',
        department: '',
        major: ''
      },
      // 模态框
      dialogVisible: false,
      // 表单数据
      formData: {
        id: null,
        student_id: '',
        student_name: '',
        gender: '',
        facultyName: '',
        departmentName: '',
        majorName: '',
        cet4_score: null,
        cet6_score: null,
        gpa: null,
        academic_score: null,
        academic_specialty_total: null,
        comprehensive_performance_total: null,
        total_score: null,
        comprehensive_score: null,
        major_ranking: null,
        total_students: null
      },
      // 表单验证错误
      errors: {}
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.total / this.pageSize)
    },
    startIndex() {
      return (this.currentPage - 1) * this.pageSize
    },
    endIndex() {
      return Math.min(this.startIndex + this.pageSize, this.total)
    },
    filteredScores() {
      let filtered = this.scores.filter(student => {
        const idMatch = !this.filters.studentId || student.student_id.includes(this.filters.studentId)
        const nameMatch = !this.filters.studentName || student.student_name.includes(this.filters.studentName)
        const facultyMatch = !this.filters.faculty || student.faculty.includes(this.filters.faculty)
        const departmentMatch = !this.filters.department || student.department.includes(this.filters.department)
        const majorMatch = !this.filters.major || student.major.includes(this.filters.major)
        
        return idMatch && nameMatch && facultyMatch && departmentMatch && majorMatch
      })
      
      return filtered
    },
    paginatedScores() {
      // 前端实现分页
      return this.filteredScores.slice(this.startIndex, this.endIndex)
    }
  },
  watch: {
    // 实时监听筛选条件变化，自动更新列表
    filters: {
      handler() {
        this.currentPage = 1
        // 这里不需要重新加载API，因为筛选是在前端进行的
      },
      deep: true
    }
  },
  mounted() {
    this.loadScoresFromAPI()
  },
  methods: {
    // 从API加载成绩数据
    async loadScoresFromAPI() {
      this.loading = true
      try {
        // 使用applicationsStore加载学生排名数据
        const applicationsStore = useApplicationsStore()
        const responseData = await applicationsStore.fetchStudentsRanking()
        
        // 获取学生列表并转换字段名称
        let students = responseData.students || []
        students = students.map(student => {
          return {
            // 基本信息
            id: student.id,
            student_id: student.student_id,
            student_name: student.student_name,
            gender: student.gender,
            faculty: student.faculty,
            department: student.department,
            major: student.major,
            cet4_score: student.cet4_score,
            cet6_score: student.cet6_score,
            gpa: student.gpa,
            academic_score: student.academic_score,
            
            // 从排名数据获取的字段
            academic_specialty_total: student.specialty_score || 0,
            comprehensive_performance_total: student.comprehensive_performance_total || 0,
            total_score: student.total_comprehensive_score || student.total_score,
            comprehensive_score: student.comprehensive_score || 0,
            major_ranking: student.major_ranking,
            total_students: student.major_total_students
          }
        })
        
        // 更新数据
        this.scores = students
        this.total = this.filteredScores.length
        this.currentPage = 1
        this.pageSize = 10
      } catch (error) {
        alert('加载成绩数据失败')
        console.error('Error loading scores:', error)
      } finally {
        this.loading = false
      }
    },

    // 重置筛选条件
    resetFilter() {
      Object.assign(this.filters, {
        studentId: '',
        studentName: '',
        faculty: '',
        department: '',
        major: ''
      })
      this.currentPage = 1
    },

    // 分页相关
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
      }
    },

    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
      }
    },

    // 打开编辑模态框
    openEditModal(row) {
      this.formData = {
        id: row.id, // 使用主键ID作为更新API的ID参数
        student_id: row.student_id,
        student_name: row.student_name,
        gender: row.gender,
        facultyName: row.faculty,
        departmentName: row.department,
        majorName: row.major,
        cet4_score: row.cet4_score,
        cet6_score: row.cet6_score,
        gpa: row.gpa,
        academic_score: row.academic_score,
        academic_specialty_total: row.academic_specialty_total,
        comprehensive_performance_total: row.comprehensive_performance_total,
        total_score: row.total_score,
        comprehensive_score: row.comprehensive_score,
        major_ranking: row.major_ranking,
        total_students: row.total_students
      }
      this.errors = {}
      this.dialogVisible = true
    },

    // 表单验证
    validateForm() {
      this.errors = {}
      let isValid = true

      if (!this.formData.gender) {
        this.errors.gender = '请选择性别'
        isValid = false
      }

      return isValid
    },

    // 提交表单
    async handleSubmit() {
      if (this.validateForm()) {
        try {
          // 更新学生
          await api.updateStudentAdmin(this.formData.id, this.formData)
          
          // 关闭模态框并刷新数据
          this.dialogVisible = false
          this.loadScoresFromAPI()
          alert('成绩信息更新成功')
        } catch (error) {
          alert('更新成绩信息失败')
          console.error('Error submitting student form:', error)
        }
      }
    },

    // 重新计算所有学生的综合成绩
    async recalculateComprehensiveScores() {
      try {
        // 显示确认对话框
        if (confirm('确定要重新计算所有学生的综合成绩吗？此操作可能需要一些时间。')) {
          this.loading = true
          
          // 获取当前登录用户信息
          const userInfo = JSON.parse(localStorage.getItem('user'))
          
          // 调用API重新计算综合成绩
          await api.recalculateComprehensiveScores({ username: userInfo?.username })
          
          // 刷新成绩数据
          await this.loadScoresFromAPI()
          
          alert('综合成绩重新计算完成')
        }
      } catch (error) {
        console.error('Error recalculating comprehensive scores:', error)
        alert('重新计算综合成绩失败')
      } finally {
        this.loading = false
      }
    },


  }
}
</script>

<style scoped>
@import '../common/shared-styles.css';

/* 加载状态样式 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}

/* 只读字段样式 */
.form-control[readonly] {
  background-color: #f5f5f5;
  border-color: #ddd;
  cursor: not-allowed;
}

/* 帮助文本样式 */
.help-text {
  margin-top: 5px;
  font-size: 12px;
  color: #666;
  font-style: italic;
}

/* 缩短输入框宽度 */
.form-control.small {
  width: 120px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    margin-bottom: 10px;
  }
}
</style>