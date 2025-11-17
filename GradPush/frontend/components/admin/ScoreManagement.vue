<template>
  <div class="page-content">
    <!-- 页面标题 -->
    <div class="page-title">
      <span>成绩管理</span>
    </div>

    <!-- 成绩表格 -->
    <div class="card">
      <div class="card-title">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>成绩管理</span>
        </div>
      </div>
      
      <!-- 筛选和搜索区域 -->
      <div class="filters" style="padding: 0 20px; padding-top: 20px;">
        <div class="filter-group">
          <input 
            type="text" 
            class="form-control" 
            v-model="searchQuery" 
            placeholder="搜索学生姓名或学号" 
            @keyup.enter="handleSearch"
          />
        </div>
        <div class="filter-group">
          <button class="btn btn-outline" @click="handleSearch">
            <font-awesome-icon :icon="['fas', 'search']" /> 搜索
          </button>
          <button class="btn btn-outline" @click="resetFilter">重置</button>
        </div>
      </div>
      <!-- 加载状态指示器 -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">加载中...</div>
      </div>
      <div class="table-container" style="padding: 0 20px 20px;">
        <table class="application-table">
          <thead>
            <tr>
              <th>学号</th>
              <th>姓名</th>
              <th>性别</th>
              <th>学院</th>
              <th>系</th>
              <th>专业</th>
              <th>CET4成绩</th>
              <th>CET6成绩</th>
              <th>GPA</th>
              <th>学业成绩</th>
              <th>学业加权</th>
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
              <td>
                <span class="status-badge">{{ student.gender || '未设置' }}</span>
              </td>
              <td>{{ student.faculty }}</td>
              <td>{{ student.department }}</td>
              <td>{{ student.major }}</td>
              <td>{{ student.cet4_score || '-' }}</td>
              <td>{{ student.cet6_score || '-' }}</td>
              <td>{{ student.gpa || '-' }}</td>
              <td>{{ student.academic_score || '-' }}</td>
              <td>{{ student.academic_weighted || '-' }}</td>
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
              <td :colspan="18" class="no-data">暂无成绩数据</td>
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
                <label class="form-label">学业加权</label>
                <input type="number" class="form-control" v-model="formData.academic_weighted" placeholder="请输入学业加权成绩" min="0" max="80" step="0.01" />
                <div v-if="errors.academic_weighted" class="error-message">{{ errors.academic_weighted }}</div>
              </div>
              <div class="form-group">
                <label class="form-label">学术专长</label>
                <input type="number" class="form-control" v-model="formData.academic_specialty_total" placeholder="请输入学术专长成绩" min="0" max="12" step="0.01" />
                <div v-if="errors.academic_specialty_total" class="error-message">{{ errors.academic_specialty_total }}</div>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">综合表现</label>
                <input type="number" class="form-control" v-model="formData.comprehensive_performance_total" placeholder="请输入综合表现成绩" min="0" max="8" step="0.01" />
                <div v-if="errors.comprehensive_performance_total" class="error-message">{{ errors.comprehensive_performance_total }}</div>
              </div>
              <div class="form-group">
                <label class="form-label">考核总分</label>
                <input type="number" class="form-control" v-model="formData.total_score" placeholder="请输入考核总分" min="0" max="100" step="0.01" />
                <div v-if="errors.total_score" class="error-message">{{ errors.total_score }}</div>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">综合成绩</label>
                <input type="number" class="form-control" v-model="formData.comprehensive_score" placeholder="请输入综合成绩" min="0" max="100" step="0.01" />
                <div v-if="errors.comprehensive_score" class="error-message">{{ errors.comprehensive_score }}</div>
              </div>
              <div class="form-group">
                <label class="form-label">专业排名</label>
                <input type="number" class="form-control" v-model="formData.major_ranking" placeholder="请输入专业排名" min="1" step="1" />
                <div v-if="errors.major_ranking" class="error-message">{{ errors.major_ranking }}</div>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">排名人数</label>
                <input type="number" class="form-control" v-model="formData.total_students" placeholder="请输入排名人数" min="1" step="1" />
                <div v-if="errors.total_students" class="error-message">{{ errors.total_students }}</div>
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
      // 搜索
      searchQuery: '',
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
        academic_weighted: null,
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
    paginatedScores() {
      return this.scores
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
        // 使用api工具加载成绩数据
        const params = new URLSearchParams()
        params.append('page', this.currentPage)
        params.append('per_page', this.pageSize)
        if (this.searchQuery) {
          params.append('search', this.searchQuery)
        }
        const data = await api.getStudentsAdmin(params.toString())
        
        // 更新数据
        this.scores = data.students || []
        this.total = Number(data.total) || 0
        this.currentPage = Number(data.current_page) || 1
        this.pageSize = Number(data.per_page) || 10
      } catch (error) {
        alert('加载成绩数据失败')
        console.error('Error loading scores:', error)
      } finally {
        this.loading = false
      }
    },



    // 搜索
    handleSearch() {
      this.currentPage = 1
      this.loadScoresFromAPI()
    },

    // 重置筛选条件
    resetFilter() {
      this.searchQuery = ''
      this.currentPage = 1
      this.loadScoresFromAPI()
    },

    // 分页相关
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
        this.loadScoresFromAPI()
      }
    },

    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
        this.loadScoresFromAPI()
      }
    },

    // 打开编辑模态框
    openEditModal(row) {
      this.formData = {
        id: row.id,
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
        academic_weighted: row.academic_weighted,
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
</style>