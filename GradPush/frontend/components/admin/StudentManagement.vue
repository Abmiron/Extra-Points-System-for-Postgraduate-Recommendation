<template>
  <div class="page-content">
    <!-- 页面标题 -->
    <div class="page-title">
      <span>学生信息管理</span>
    </div>

    <!-- 学生表格 -->
    <div class="card">
      <div class="card-title">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>学生管理</span>
          <button class="btn btn-outline" @click="openAddModal">
            <font-awesome-icon :icon="['fas', 'plus']" /> 添加学生
          </button>
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
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in paginatedStudents" :key="student.id">
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
              <td>
                <div class="action-buttons">
                  <button class="btn-outline btn small-btn" @click="openEditModal(student)">
                    <font-awesome-icon :icon="['fas', 'edit']" /> 
                  </button>
                  <button class="btn-outline btn small-btn delete-btn" @click="handleDelete(student.id)">
                    <font-awesome-icon :icon="['fas', 'trash']" /> 
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="paginatedStudents.length === 0">
              <td :colspan="11" class="no-data">暂无学生数据</td>
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
          <h3>{{ isEdit ? '编辑学生' : '添加学生' }}</h3>
          <button class="close-btn" @click="dialogVisible = false">
            <font-awesome-icon :icon="['fas', 'times']" />
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">学号</label>
                <input type="text" class="form-control" v-model="formData.student_id" placeholder="请输入学号" :disabled="isEdit" required />
                <div v-if="errors.student_id" class="error-message">{{ errors.student_id }}</div>
              </div>
              <div class="form-group">
                <label class="form-label">姓名</label>
                <input type="text" class="form-control" v-model="formData.student_name" placeholder="请输入姓名" required />
                <div v-if="errors.student_name" class="error-message">{{ errors.student_name }}</div>
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
                <select class="form-control" v-model="formData.facultyId" placeholder="请选择学院" @change="handleFacultyChange" required>
                  <option value="">请选择学院</option>
                  <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.id">
                    {{ faculty.name }}
                  </option>
                </select>
                <div v-if="errors.facultyId" class="error-message">{{ errors.facultyId }}</div>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">系</label>
                <select class="form-control" v-model="formData.department_id" placeholder="请选择系" @change="handleDepartmentChange" required>
                  <option value="">请选择系</option>
                  <option v-for="department in departments" :key="department.id" :value="department.id">
                    {{ department.name }}
                  </option>
                </select>
                <div v-if="errors.department_id" class="error-message">{{ errors.department_id }}</div>
              </div>
              <div class="form-group">
                <label class="form-label">专业</label>
                <select class="form-control" v-model="formData.major_id" placeholder="请选择专业" required>
                  <option value="">请选择专业</option>
                  <option v-for="major in majors" :key="major.id" :value="major.id">
                    {{ major.name }}
                  </option>
                </select>
                <div v-if="errors.major_id" class="error-message">{{ errors.major_id }}</div>
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
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="dialogVisible = false">取消</button>
              <button type="submit" class="btn btn-primary">{{ isEdit ? '更新' : '添加' }}</button>
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
  name: 'StudentManagement',
  components: {
  },
  data() {
    return {
      // 表格数据
      students: [],
      total: 0,
      loading: false,
      // 分页
      currentPage: 1,
      pageSize: 10,
      // 搜索
      searchQuery: '',
      // 模态框
      dialogVisible: false,
      isEdit: false,
      // 表单数据
      formData: {
        id: null,
        student_id: '',
        student_name: '',
        gender: '',
        facultyId: '',
        department_id: '',
        major_id: '',
        cet4_score: null,
        cet6_score: null,
        gpa: null,
        academic_score: null
      },
      // 表单验证错误
      errors: {},
      // 学院、系、专业数据
      faculties: [],
      departments: [],
      majors: []
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
    paginatedStudents() {
      return this.students
    }
  },
  mounted() {
    this.loadStudentsFromAPI()
    this.loadFacultiesFromAPI()
  },
  methods: {
    // 从API加载学生数据
    async loadStudentsFromAPI() {
      this.loading = true
      try {
        // 使用api工具加载学生数据
        const params = new URLSearchParams()
        params.append('page', this.currentPage)
        params.append('per_page', this.pageSize)
        if (this.searchQuery) {
          params.append('search', this.searchQuery)
        }
        const data = await api.getStudentsAdmin(params.toString())
        
        // 更新数据
        this.students = data.students || []
        this.total = Number(data.total) || 0
        this.currentPage = Number(data.current_page) || 1
        this.pageSize = Number(data.per_page) || 10
      } catch (error) {
        alert('加载学生数据失败')
        console.error('Error loading students:', error)
      } finally {
        this.loading = false
      }
    },

    // 从API加载学院数据
    async loadFacultiesFromAPI() {
      try {
        const data = await api.getFacultiesAdmin()
        this.faculties = data.faculties
      } catch (error) {
        console.error('Error loading faculties:', error)
      }
    },

    // 从API加载系数据
    async loadDepartmentsFromAPI(facultyId) {
      try {
        const data = await api.getDepartmentsAdmin(facultyId)
        this.departments = data.departments
      } catch (error) {
        console.error('Error loading departments:', error)
      }
    },

    // 从API加载专业数据
    async loadMajorsFromAPI(departmentId) {
      try {
        const data = await api.getMajorsAdmin(departmentId)
        this.majors = data.majors
      } catch (error) {
        console.error('Error loading majors:', error)
      }
    },

    // 处理学院变化
    handleFacultyChange(facultyId) {
      this.formData.department_id = ''
      this.formData.major_id = ''
      this.departments = []
      this.majors = []
      
      if (facultyId) {
        this.loadDepartmentsFromAPI(facultyId)
      }
    },

    // 处理系变化
    handleDepartmentChange(departmentId) {
      this.formData.major_id = ''
      this.majors = []
      
      if (departmentId) {
        this.loadMajorsFromAPI(departmentId)
      }
    },

    // 搜索
    handleSearch() {
      this.currentPage = 1
      this.loadStudentsFromAPI()
    },

    // 重置筛选条件
    resetFilter() {
      this.searchQuery = ''
      this.currentPage = 1
      this.loadStudentsFromAPI()
    },

    // 分页相关
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
        this.loadStudentsFromAPI()
      }
    },

    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
        this.loadStudentsFromAPI()
      }
    },

    // 打开添加模态框
    openAddModal() {
      this.isEdit = false
      this.formData = {
        id: null,
        student_id: '',
        student_name: '',
        gender: '',
        facultyId: '',
        department_id: '',
        major_id: '',
        cet4_score: null,
        cet6_score: null,
        gpa: null,
        academic_score: null
      }
      this.errors = {}
      this.dialogVisible = true
    },

    // 打开编辑模态框
    openEditModal(row) {
      this.isEdit = true
      this.formData = {
        id: row.id,
        student_id: row.student_id,
        student_name: row.student_name,
        gender: row.gender,
        facultyId: row.facultyId,
        department_id: row.department_id,
        major_id: row.major_id,
        cet4_score: row.cet4_score,
        cet6_score: row.cet6_score,
        gpa: row.gpa,
        academic_score: row.academic_score
      }
      this.errors = {}
      this.dialogVisible = true
      // 加载学院、系、专业数据
      this.loadDepartmentsFromAPI(row.facultyId)
      // 异步设置专业数据
      setTimeout(() => {
        this.loadMajorsFromAPI(row.department_id)
      }, 100)
    },

    // 表单验证
    validateForm() {
      this.errors = {}
      let isValid = true

      if (!this.formData.student_id) {
        this.errors.student_id = '请输入学号'
        isValid = false
      } else if (this.formData.student_id.length < 8 || this.formData.student_id.length > 12) {
        this.errors.student_id = '学号长度在 8 到 12 个字符'
        isValid = false
      }

      if (!this.formData.student_name) {
        this.errors.student_name = '请输入姓名'
        isValid = false
      } else if (this.formData.student_name.length < 2 || this.formData.student_name.length > 20) {
        this.errors.student_name = '姓名长度在 2 到 20 个字符'
        isValid = false
      }

      if (!this.formData.gender) {
        this.errors.gender = '请选择性别'
        isValid = false
      }

      if (!this.formData.facultyId) {
        this.errors.facultyId = '请选择学院'
        isValid = false
      }

      if (!this.formData.department_id) {
        this.errors.department_id = '请选择系'
        isValid = false
      }

      if (!this.formData.major_id) {
        this.errors.major_id = '请选择专业'
        isValid = false
      }

      return isValid
    },

    // 提交表单
    async handleSubmit() {
      if (this.validateForm()) {
        try {
          if (this.isEdit) {
            // 更新学生
            await api.updateStudentAdmin(this.formData.id, this.formData)
          } else {
            // 添加学生
            await api.createStudentAdmin(this.formData)
          }
          
          // 关闭模态框并刷新数据
          this.dialogVisible = false
          this.loadStudentsFromAPI()
          alert(this.isEdit ? '学生信息更新成功' : '学生添加成功')
        } catch (error) {
          alert(this.isEdit ? '更新学生信息失败' : '添加学生失败')
          console.error('Error submitting student form:', error)
        }
      }
    },

    // 删除学生
    async handleDelete(studentId) {
      if (confirm('确定要删除该学生吗？')) {
        try {
          await api.deleteStudentAdmin(studentId)
          alert('学生删除成功')
          this.loadStudentsFromAPI()
        } catch (error) {
          alert('删除学生失败')
          console.error('Error deleting student:', error)
        }
      }
    }
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