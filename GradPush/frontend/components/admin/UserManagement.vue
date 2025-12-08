<template>
  <div class="page-content">
    <div class="page-title">
      <span>用户管理</span>
      <div class="page-title-actions">
        <button class="btn btn-outline" @click="importUsers">
          <font-awesome-icon :icon="['fas', 'download']" /> 导入用户
        </button>
        <button class="btn btn-outline" @click="showAddUserModal = true">
          <font-awesome-icon :icon="['fas', 'plus']" /> 添加用户
        </button>
      </div>
    </div>

    <!-- 选项卡 -->
    <div class="tabs">
      <button class="tab-btn" :class="{ active: activeTab === 'student' }" @click="activeTab = 'student'">学生账户</button>
      <button class="tab-btn" :class="{ active: activeTab === 'teacher' }" @click="activeTab = 'teacher'">教师账户</button>
      <button class="tab-btn" :class="{ active: activeTab === 'admin' }" @click="activeTab = 'admin'">管理员账户</button>
    </div>

    <!-- 筛选区域 -->
    <div class="filters">
      <div class="filter-group">
        <input type="text" class="form-control" v-model="filters.keyword" placeholder="搜索姓名或学号/工号"
          @keyup.enter="searchUsers">
      </div>
      <div class="filter-group">
        <span class="filter-label">学院:</span>
        <select class="form-control" v-model="filters.faculty">
          <option value="all">全部</option>
          <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.id">
            {{ faculty.name }}
          </option>
        </select>
      </div>
      <!-- 系筛选（仅学生显示） -->
      <div class="filter-group" v-if="activeTab === 'student'">
        <span class="filter-label">系:</span>
        <select class="form-control" v-model="filters.department">
          <option value="all">全部</option>
          <option v-for="department in departments" :key="department.id" :value="department.id">
            {{ department.name }}
          </option>
        </select>
      </div>
      <!-- 专业筛选（仅学生显示） -->
      <div class="filter-group" v-if="activeTab === 'student'">
        <span class="filter-label">专业:</span>
        <select class="form-control" v-model="filters.major">
          <option value="all">全部</option>
          <option v-for="major in majors" :key="major.id" :value="major.id">
            {{ major.name }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">状态:</span>
        <select class="form-control" v-model="filters.status">
          <option value="all">全部</option>
          <option value="active">启用</option>
          <option value="disabled">禁用</option>
        </select>
      </div>
      <button class="btn btn-outline" @click="resetFilters">清空筛选</button>
    </div>

    <!-- 批量操作工具栏 -->
    <div class="batch-actions">
      <button class="btn btn-outline" @click="batchDisable" :disabled="selectedUsers.length === 0">
        <font-awesome-icon :icon="['fas', 'ban']" /> 禁用选中
      </button>
      <button class="btn btn-outline" @click="batchEnable" :disabled="selectedUsers.length === 0">
        <font-awesome-icon :icon="['fas', 'check']" /> 启用选中
      </button>
      <button class="btn btn-outline" @click="batchResetPassword" :disabled="selectedUsers.length === 0">
        <font-awesome-icon :icon="['fas', 'key']" /> 重置密码
      </button>
      <button class="btn btn-outline" @click="batchDelete" :disabled="selectedUsers.length === 0">
        <font-awesome-icon :icon="['fas', 'trash']" /> 删除选中
      </button>
    </div>

    <!-- 用户表格 -->
    <div class="card">
      <!-- 加载状态指示器 -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">加载中...</div>
      </div>
      <div class="table-container">
        <table class="application-table">
          <thead>
            <tr>
              <th><input type="checkbox" v-model="selectAll" @change="toggleSelectAll"></th>
              <th>账号</th>
              <th>姓名</th>
              <th>学院</th>
              <th v-if="activeTab === 'student'">系</th>
              <th>专业/角色</th>
              <th>状态</th>
              <th>最后登录</th>
              <th v-if="activeTab === 'admin'">登录状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedUsers" :key="user.id">
              <td><input type="checkbox" v-model="selectedUsers" :value="user.id"
                  :disabled="user.id === authStore.user?.id"
                  :class="{ 'checkbox-disabled': user.id === authStore.user?.id }"></td>
              <td>{{ user.username }}</td>
              <td>{{ user.name }}</td>
              <td>{{ user.faculty?.name || getFacultyText(user.faculty) }}</td>
              <td v-if="activeTab === 'student'">
                {{ user.department?.name || user.department || '-' }}
              </td>
              <td>{{ user.role === 'student' ? (user.major?.name || user.major) : (user.role === 'teacher' ?
                user.roleName : user.roleName || '管理员') }}</td>
              <td>
                <span :class="`status-badge status-${user.status === 'active' ? 'approved' : 'rejected'}`">
                  {{ user.status === 'active' ? '启用' : '禁用' }}
                </span>
              </td>
              <td>{{ formatDate(user.lastLogin) }}</td>
              <td v-if="activeTab === 'admin'">
                <span v-if="user.id === authStore.user?.id" class="current-login-badge">当前登录</span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="btn-outline btn small-btn" @click="editUser(user)" title="编辑"
                    :disabled="user.id === authStore.user?.id"
                    :class="{ 'btn-disabled': user.id === authStore.user?.id }">
                    <font-awesome-icon :icon="['fas', 'edit']" />
                  </button>
                  <button v-if="user.status === 'active'" class="btn-outline btn small-btn"
                    @click="toggleUserStatus(user.id, 'disabled')" title="禁用" :disabled="user.id === authStore.user?.id"
                    :class="{ 'btn-disabled': user.id === authStore.user?.id }">
                    <font-awesome-icon :icon="['fas', 'ban']" />
                  </button>
                  <button v-else class="btn-outline btn small-btn" @click="toggleUserStatus(user.id, 'active')"
                    title="启用" :disabled="user.id === authStore.user?.id"
                    :class="{ 'btn-disabled': user.id === authStore.user?.id }">
                    <font-awesome-icon :icon="['fas', 'check']" />
                  </button>
                  <button class="btn-outline btn small-btn" @click="resetPassword(user.id)" title="重置密码"
                    :disabled="user.id === authStore.user?.id"
                    :class="{ 'btn-disabled': user.id === authStore.user?.id }">
                    <font-awesome-icon :icon="['fas', 'key']" />
                  </button>
                  <button class="btn-outline btn small-btn" @click="deleteUser(user.id)" title="删除"
                    :disabled="user.id === authStore.user?.id"
                    :class="{ 'btn-disabled': user.id === authStore.user?.id }">
                    <font-awesome-icon :icon="['fas', 'trash']" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="paginatedUsers.length === 0">
              <td :colspan="activeTab === 'admin' ? 8 : (activeTab === 'student' ? 8 : 7)" class="no-data">暂无用户数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 分页控件 -->
    <div class="pagination">
      <div class="pagination-info">显示 {{ startIndex + 1 }}-{{ endIndex }} 条，共 {{ totalUsers }} 条记录</div>
      <div class="pagination-controls">
        <button class="btn-outline btn" :disabled="currentPage === 1" @click="prevPage">
          <font-awesome-icon :icon="['fas', 'chevron-left']" /> 上一页
        </button>
        <button class="btn-outline btn" :disabled="currentPage >= totalPages" @click="nextPage">
          下一页 <font-awesome-icon :icon="['fas', 'chevron-right']" />
        </button>
      </div>
    </div>

    <!-- 添加/编辑用户模态框 -->
    <div v-if="showAddUserModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingUser ? '编辑用户' : '添加用户' }}</h3>
          <button class="close-btn" @click="closeModal">
            <font-awesome-icon :icon="['fas', 'times']" />
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveUser">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">用户类型</label>
                <select class="form-control" v-model="userForm.role" required @change="handleRoleChange">
                  <option value="">请选择角色</option>
                  <option value="student">学生</option>
                  <option value="teacher">教师</option>
                  <option value="admin">管理员</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">{{ userForm.role === 'student' ? '学号' : (userForm.role === 'teacher' ? '工号' :
                  '管理员账号') }}</label>
                <input type="text" class="form-control" v-model="userForm.username" required>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">姓名</label>
                <input type="text" class="form-control" v-model="userForm.name" required>
              </div>
              <div class="form-group">
                <label class="form-label">学院</label>
                <select class="form-control" v-model="userForm.facultyId" :required="userForm.role !== 'admin'"
                  @change="handleFacultyChange">
                  <option value="">请选择学院</option>
                  <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.id">
                    {{ faculty.name }}
                  </option>
                </select>
              </div>
            </div>
            <!-- 系选择（仅学生显示） -->
            <div class="form-row" v-if="userForm.role === 'student'">
              <div class="form-group">
                <label class="form-label">系</label>
                <select class="form-control" v-model="userForm.departmentId" required @change="handleDepartmentChange">
                  <option value="">请选择系</option>
                  <option v-for="department in departments" :key="department.id" :value="department.id">
                    {{ department.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">专业</label>
                <select class="form-control" v-model="userForm.majorId" required>
                  <option value="">请选择专业</option>
                  <option v-for="major in majors" :key="major.id" :value="major.id">
                    {{ major.name }}
                  </option>
                </select>
              </div>
            </div>
            <div class="form-row" v-else-if="userForm.role === 'teacher'">
              <div class="form-group">
                <label class="form-label">角色</label>
                <input type="text" class="form-control" v-model="userForm.roleName" placeholder="如：审核员">
                <div class="help-text">默认为审核员</div>
              </div>
            </div>
            <div class="form-row" v-else-if="userForm.role === 'admin'">
              <div class="form-group">
                <label class="form-label">管理员类型</label>
                <input type="text" class="form-control" v-model="userForm.roleName" placeholder="如：系统管理员">
                <div class="help-text">默认为系统管理员</div>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">初始密码</label>
                <input type="password" class="form-control" v-model="userForm.password">
                <div class="help-text">若不修改密码请留空，默认为123456</div>
              </div>
              <div class="form-group">
                <label class="form-label">状态</label>
                <select class="form-control" v-model="userForm.status" required>
                  <option value="active">启用</option>
                  <option value="disabled">禁用</option>
                </select>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="closeModal">取消</button>
              <button type="submit" class="btn">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 导入用户对话框 -->
    <div v-if="importDialogVisible" class="modal-overlay" @click.self="closeImportDialog">
      <div class="modal-content">
        <div class="modal-header">
          <h3>导入用户</h3>
          <button class="close-btn" @click="closeImportDialog">
            <font-awesome-icon icon="fa-times" />
          </button>
        </div>

        <div class="modal-body">
          <div class="form-group" v-if="!importResult">
            <!-- 文件上传区域 -->
            <div class="upload-demo">
              <input type="file" ref="fileUploadRef" accept=".xlsx, .xls" @change="handleFileChange"
                style="display: none;">
              <div class="file-upload-area" @click="openFileSelect" @dragover.prevent @dragenter.prevent
                @drop="handleFileDrop">
                <font-awesome-icon icon="fa-upload" class="upload-icon" />
                <div>
                  <div>点击或拖拽文件到此处上传</div>
                  <div style="font-size: 0.8em; color: #999; margin-top: 5px;">支持.xlsx, .xls格式文件</div>
                </div>
              </div>
            </div>
            <!-- 已上传文件 -->
            <div class="file-list" v-if="importFile">
              <div class="file-list-header">
                <span>已上传文件：</span>
              </div>
              <div class="file-info" style="padding: 10px;margin-top: 0px;">
                <div class="file-name">{{ importFile.name }}</div>
                <button type="button" class="file-action-btn" @click="closeFileSelect" title="移除文件">
                  <font-awesome-icon :icon="['fas', 'times']" />
                </button>
              </div>
            </div>
            <!-- 导入注意事项 -->
            <div style="margin-left: 10px;">
              <div style="color: #999;">
                <font-awesome-icon icon="fa-exclamation-triangle" /> 注意事项
              </div>
              <div style="color: #999;">
                <strong>1. 格式要求：</strong><br>
                必填表头：用户名,姓名,角色,状态<br>
                可选表头：学院,系,专业,邮箱,电话,性别,CET4成绩,CET6成绩,绩点,转换分数（顺序不限）<br>
                -角色只能是：admin/teacher/student<br>
                -状态只能是：active(启用)/disabled(禁用)<br>
                -性别只能是：男/女<br>
                默认密码为：123456<br>
                <br>
                <strong>2. 学生相关：</strong><br>
                学生用户必须填写学院、系和专业<br>
                学生用户可选填写：性别, CET4成绩, CET6成绩, 绩点, 转换分数<br>
                <br>
                <strong>3. excel结构示例</strong>
              </div>
              <!-- 导入示例图片 -->
              <div>
                <img src="/images/导入用户示例.png" alt="导入用户示例" style="max-width: 100%; border: 1px solid #eee; border-radius: 4px;">
              </div>
            </div>
          </div>

          <!-- 导入结果区域 -->
          <div class="import-result" v-if="importResult">
            <div class="card">
              <div class="card-title">
                <span>导入结果</span>
              </div>
              <div class="card-body">
                <div class="form-group" style="display: flex; justify-content: space-around; flex-direction: row;">
                  <div class="stat-card" style="padding: 20px 60px;">
                    <div class="stat-label">成功导入</div>
                    <div class="stat-value">{{ importResult.success_count }}人</div>
                  </div>
                  <div class="stat-card" style="padding: 20px 60px;">
                    <div class="stat-label">导入失败</div>
                    <div class="stat-value">{{ importResult.error_count }}人</div>
                  </div>
                  <div class="stat-card" style="padding: 20px 60px;">
                    <div class="stat-label">总记录数</div>
                    <div class="stat-value">{{ importResult.success_count + importResult.error_count }}人</div>
                  </div>
                </div>

                <!-- 错误信息列表 -->
                <div v-if="importErrors.length > 0" class="error-list">
                  <h4>错误信息：</h4>
                  <div class="scrollbar" style="height: 200px; overflow-y: auto;">
                    <ul class="timeline">
                      <li v-for="(error, index) in importErrors" :key="index" class="timeline-item">
                        <font-awesome-icon icon="fa-exclamation-circle" class="timeline-icon danger" />
                        <span class="timeline-content">{{ error }}</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button class="btn btn-outline" @click="closeImportDialog">关闭</button>
            <button class="btn btn-primary" @click="confirmImport" :loading="importLoading"
              :disabled="!importFile || importResult">
              确认导入
            </button>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useToastStore } from '../../stores/toast'
import api from '../../utils/api'

const activeTab = ref('student')
const fileUploadRef = ref(null)
const showAddUserModal = ref(false)
const editingUser = ref(null)
const selectAll = ref(false)
const selectedUsers = ref([])
const currentPage = ref(1)
const pageSize = 10
const isLoading = ref(false)
const authStore = useAuthStore()
const toastStore = useToastStore()

const filters = reactive({
  keyword: '',
  faculty: 'all',
  department: 'all',
  major: 'all',
  status: 'all'
})

const userForm = reactive({
  role: 'student',
  username: '',
  name: '',
  facultyId: '',
  departmentId: '',
  majorId: '',
  roleName: '',
  password: '',
  status: 'active'
})

// 下拉选项数据
const faculties = ref([])
const departments = ref([])
const majors = ref([])
const loadingOptions = ref(false)

// 从后端API获取用户数据
const users = ref([])
const totalUsers = ref(0)
const totalPages = ref(0)

// 组件挂载时加载学院列表
onMounted(async () => {
  await loadFaculties()
  // 如果当前选中的是学生选项卡，并且已经选择了学院，加载对应的系列表
  if (activeTab.value === 'student' && filters.faculty && filters.faculty !== 'all') {
    await loadDepartments(filters.faculty)
    // 如果已经选择了系，加载对应的专业列表
    if (filters.department && filters.department !== 'all') {
      const department = departments.value.find(d => d.name === filters.department)
      if (department) {
        await loadMajors(department.id)
      }
    }
  }
  // 加载用户数据
  loadUsersFromAPI()
})

// 加载学院列表
const loadFaculties = async () => {
  try {
    loadingOptions.value = true
    // 使用管理员API端点获取学院数据
    const response = await api.getFacultiesAdmin()
    faculties.value = response.faculties
  } catch (error) {
    console.error('加载学院列表失败:', error)
    toastStore.error('加载学院列表失败，请刷新页面重试')
  } finally {
    loadingOptions.value = false
  }
}

// 加载系列表
const loadDepartments = async (facultyId = null) => {
  try {
    loadingOptions.value = true
    if (facultyId) {
      // 使用管理员API端点获取指定学院的系数据
      const response = await api.getDepartmentsAdmin(facultyId)
      departments.value = response.departments
      // 保留当前的系和专业选择
      // 如果当前选择的系不在新加载的列表中，则重置
      const departmentExists = departments.value.some(dept => dept.name === filters.department)
      if (!departmentExists) {
        filters.department = 'all'
        filters.major = 'all'
        majors.value = []
      }
    } else {
      // 加载所有系（类似审核记录组件的实现）
      try {
        const response = await api.getDepartmentsAdmin()
        departments.value = response.departments || []
      } catch (error) {
        console.error('获取所有系列表失败:', error)
        // 尝试使用默认学院的系
        const defaultFaculty = faculties.value[0]
        if (defaultFaculty) {
          const response = await api.getDepartmentsAdmin(defaultFaculty.id)
          departments.value = response.departments || []
        }
      }
    }
  } catch (error) {
    console.error('加载系列表失败:', error)
    toastStore.error('加载系列表失败，请重试')
  } finally {
    loadingOptions.value = false
  }
}

// 加载专业列表
const loadMajors = async (departmentId = null) => {
  try {
    loadingOptions.value = true
    if (departmentId) {
      // 使用管理员API端点获取指定系的专业数据
      const response = await api.getMajorsAdmin(departmentId)
      majors.value = response.majors
      // 保留当前的专业选择
      // 如果当前选择的专业不在新加载的列表中，则重置
      const majorExists = majors.value.some(major => major.name === filters.major)
      if (!majorExists) {
        filters.major = 'all'
      }
    } else {
      // 优化：使用并行请求加载所有专业
      try {
        if (departments.value.length > 0) {
          // 并行获取所有系的专业数据
          const promises = departments.value.map(dept =>
            api.getMajorsAdmin(dept.id).catch(error => {
              console.warn(`获取系 ${dept.name} 的专业数据失败:`, error)
              return { majors: [] }
            })
          )

          const results = await Promise.all(promises)
          // 合并所有专业数据
          const allMajors = results.flatMap(result => result.majors || [])
          majors.value = allMajors
        } else {
          majors.value = []
        }
      } catch (error) {
        console.error('获取所有专业列表失败:', error)
        // 如果都失败，使用空数组
        majors.value = []
      }
    }
  } catch (error) {
    console.error('加载专业列表失败:', error)
    toastStore.error('加载专业列表失败，请重试')
  } finally {
    loadingOptions.value = false
  }
}

// 角色变化处理
const handleRoleChange = () => {
  // 重置学院、系和专业选择
  userForm.facultyId = ''
  userForm.departmentId = ''
  userForm.majorId = ''
  departments.value = []
  majors.value = []
}

// 学院变化处理
const handleFacultyChange = () => {
  // 只有当角色不是管理员时才加载系和专业
  if (userForm.role !== 'admin' && userForm.facultyId) {
    loadDepartments(userForm.facultyId)
  } else if (userForm.role !== 'admin') {
    // 重置系和专业选择（仅非管理员角色）
    userForm.departmentId = ''
    userForm.majorId = ''
    departments.value = []
    majors.value = []
  }
}

// 系变化处理
const handleDepartmentChange = () => {
  if (userForm.departmentId) {
    loadMajors(userForm.departmentId)
  } else {
    // 重置专业选择
    userForm.majorId = ''
    majors.value = []
  }
}

// 从后端API加载用户数据的函数
const loadUsersFromAPI = async () => {
  // 检查用户是否已登录
  if (!authStore.isAuthenticated) {
    return
  }

  try {
    isLoading.value = true
    const role = activeTab.value
    const status = filters.status === 'all' ? '' : filters.status
    const search = filters.keyword || ''

    // 构建API请求URL
    const params = new URLSearchParams({
      currentUserId: authStore.user?.id || '',
      page: currentPage.value,
      per_page: pageSize,
      role: role,
      status: status,
      search: search
    })

    // 添加学院筛选条件（排除'all'）
    if (filters.faculty && filters.faculty !== 'all') {
      params.append('faculty', filters.faculty)
    }

    // 仅当学生选项卡时添加系和专业筛选条件
    if (role === 'student') {
      if (filters.department !== 'all') {
        params.append('department', filters.department)
      }
      if (filters.major !== 'all') {
        params.append('major', filters.major)
      }
    }

    const response = await fetch(`/api/admin/users?${params}`)

    if (!response.ok) {
      throw new Error('获取用户数据失败')
    }

    const data = await response.json()
    users.value = data.users
    totalUsers.value = data.total
    totalPages.value = data.pages
  } catch (error) {
    console.error('加载用户数据失败:', error)
    toastStore.error('加载用户数据失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

// 计算属性
const startIndex = computed(() => (currentPage.value - 1) * pageSize)
const endIndex = computed(() => Math.min(startIndex.value + pageSize, totalUsers.value))

const paginatedUsers = computed(() => {
  return users.value
})

// 方法
const getFacultyText = (faculty) => {
  if (!faculty) return ''
  const faculties = {
    '信息学院': '信息学院',
    '计算机科学系': '计算机科学系',
    '软件工程系': '软件工程系',
    '人工智能系': '人工智能系'
  }
  return faculties[faculty] || faculty
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const searchUsers = () => {
  currentPage.value = 1
  loadUsersFromAPI()
}

const resetFilters = () => {
  // 重置筛选条件
  filters.keyword = ''
  filters.faculty = 'all'
  filters.department = 'all'
  filters.major = 'all'
  filters.status = 'all'
  // 重置系和专业下拉列表
  departments.value = []
  majors.value = []
  // 重新加载用户数据
  searchUsers()
}

const toggleSelectAll = () => {
  if (selectAll.value) {
    // 全选时排除当前登录用户
    selectedUsers.value = paginatedUsers.value
      .filter(user => user.id !== authStore.user?.id)
      .map(user => user.id)
  } else {
    selectedUsers.value = []
  }
}

// 导入用户相关状态
const importDialogVisible = ref(false);
const importFile = ref(null);
const importLoading = ref(false);
const importResult = ref(null);
const importErrors = ref([]);

// 打开导入对话框
const importUsers = () => {
  importDialogVisible.value = true;
  importFile.value = null;
  importResult.value = null;
  importErrors.value = [];
};

// 打开文件选择对话框
const openFileSelect = () => {
  if (fileUploadRef.value && typeof fileUploadRef.value.click === 'function') {
    fileUploadRef.value.click();
  }
};

// 文件选择处理
const handleFileChange = (event) => {
  if (event.target.files.length > 0) {
    importFile.value = event.target.files[0];
  }
};

// 文件拖拽处理
const handleFileDrop = (event) => {
  event.preventDefault();
  if (event.dataTransfer.files.length > 0) {
    const file = event.dataTransfer.files[0];
    // 验证文件类型
    const allowedExtensions = ['.xlsx', '.xls'];
    const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
    if (allowedExtensions.includes(fileExtension)) {
      importFile.value = file;
    } else {
      toastStore.warning('只支持.xlsx, .xls格式文件');
    }
  }
};

// 关闭文件选择
const closeFileSelect = () => {
  importFile.value = null;
};

// 确认导入
const confirmImport = async () => {
  if (!importFile.value) {
    toastStore.warning('请选择要导入的Excel文件');
    return;
  }

  importLoading.value = true;

  try {
    const formData = new FormData();
    formData.append('file', importFile.value);

    const response = await fetch('/api/admin/import-users', {
      method: 'POST',
      body: formData,
      credentials: 'include'
    });

    const data = await response.json();

    if (response.ok) {
      importResult.value = data;
      importErrors.value = data.errors || [];

      toastStore.success('用户导入完成');

      // 刷新用户列表
      await loadUsersFromAPI();
    } else {
      toastStore.error(data.message || '导入失败');
    }
  } catch (error) {
    console.error('导入用户失败:', error);
    toastStore.error('导入失败，请检查网络连接');
  } finally {
    importLoading.value = false;
  }
};

// 关闭导入对话框
const closeImportDialog = () => {
  importDialogVisible.value = false;
  importFile.value = null;
  importResult.value = null;
  importErrors.value = [];
};

const editUser = (user) => {
  editingUser.value = user

  // 初始化表单，直接使用用户对象中的ID字段
  Object.assign(userForm, {
    id: user.id,
    role: user.role,
    username: user.username,
    name: user.name,
    facultyId: user.facultyId || '',
    departmentId: user.departmentId || '',
    majorId: user.majorId || '',
    roleName: user.roleName,
    status: user.status,
    password: '' // 重置密码字段
  })

  // 立即显示模态框，提升用户体验
  showAddUserModal.value = true

  // 如果是学生用户，异步加载对应的系和专业列表
  if (userForm.role === 'student' && userForm.facultyId) {
    // 使用异步函数加载数据，不阻塞模态框显示
    const loadUserRelatedData = async () => {
      try {
        await loadDepartments(userForm.facultyId)
        if (userForm.departmentId) {
          await loadMajors(userForm.departmentId)
        }
      } catch (error) {
        console.error('加载用户相关数据失败:', error)
      }
    }
    loadUserRelatedData()
  }
}

const saveUser = async () => {
  try {
    isLoading.value = true
    const username = userForm.username

    // 准备请求数据
    const userData = {
      role: userForm.role,
      username: username,
      name: userForm.name,
      status: userForm.status,
      // 仅当角色不是管理员时包含学院ID
      ...(userForm.role !== 'admin' ? { facultyId: userForm.facultyId } : {}),
      ...(userForm.role === 'student' ? {
        departmentId: userForm.departmentId,
        majorId: userForm.majorId
      } : {
        roleName: userForm.roleName || (userForm.role === 'teacher' ? '审核员' : '系统管理员')
      })
    }

    // 如果提供了密码，则包含密码字段；如果是新用户且未提供密码，则使用默认密码
    if (userForm.password) {
      userData.password = userForm.password
    } else if (!editingUser.value) {
      userData.password = '123456'
    }

    let response
    if (editingUser.value) {
      // 更新用户 - 调用PUT API
      response = await fetch(`/api/admin/users/${editingUser.value.id}?currentUserId=${authStore.user?.id || ''}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      })
    } else {
      // 添加新用户 - 调用管理员专用接口
      response = await fetch(`/api/admin/create-users?currentUserId=${authStore.user?.id || ''}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      })
    }

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || '操作失败')
    }

    toastStore.success(editingUser.value ? '用户信息更新成功' : '用户添加成功')
    closeModal()
    loadUsersFromAPI() // 重新加载用户列表
  } catch (error) {
    console.error('保存用户失败:', error)
    toastStore.error(error.message || '保存失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

const toggleUserStatus = async (userId, status) => {
  try {
    isLoading.value = true

    const response = await fetch(`/api/admin/users/${userId}?currentUserId=${authStore.user?.id || ''}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: status })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || '操作失败')
    }

    toastStore.success(`用户已${status === 'active' ? '启用' : '禁用'}`)
    loadUsersFromAPI() // 重新加载用户列表
  } catch (error) {
    console.error('更新用户状态失败:', error)
    toastStore.error(error.message || '操作失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

const resetPassword = async (userId) => {
  if (confirm('确定要重置该用户的密码吗？')) {
    try {
      isLoading.value = true
      const newPassword = prompt('请输入新密码（留空则使用默认密码123456）:', '') || '123456'

      const response = await fetch(`/api/admin/users/${userId}/reset-password?currentUserId=${authStore.user?.id || ''}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ newPassword: newPassword })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || '操作失败')
      }

      toastStore.success('密码重置成功')
    } catch (error) {
      console.error('重置密码失败:', error)
      toastStore.error(error.message || '重置密码失败，请稍后重试')
    } finally {
      isLoading.value = false
    }
  }
}

const deleteUser = async (userId) => {
  if (confirm(`确定要删除该用户吗？此操作不可恢复！`)) {
    try {
      isLoading.value = true

      const response = await fetch(`/api/admin/users/${userId}?currentUserId=${authStore.user?.id || ''}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error('删除用户失败')
      }

      toastStore.success('用户已删除')
      loadUsersFromAPI() // 重新加载用户列表
    } catch (error) {
      console.error('删除用户失败:', error)
      toastStore.error('操作失败，请稍后重试')
    } finally {
      isLoading.value = false
    }
  }
}

const batchDisable = async () => {
  if (confirm(`确定要禁用选中的 ${selectedUsers.value.length} 个用户吗？`)) {
    try {
      isLoading.value = true

      // 批量禁用用户（逐个调用API）
      const promises = selectedUsers.value.map(userId =>
        fetch(`/api/admin/users/${userId}?currentUserId=${authStore.user?.id || ''}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ status: 'disabled' })
        })
      )

      const responses = await Promise.all(promises)

      // 检查是否所有请求都成功
      for (const response of responses) {
        if (!response.ok) {
          throw new Error('批量禁用失败')
        }
      }

      selectedUsers.value = []
      selectAll.value = false
      toastStore.success('选中用户已禁用')
      loadUsersFromAPI() // 重新加载用户列表
    } catch (error) {
      console.error('批量禁用失败:', error)
      toastStore.error('操作失败，请稍后重试')
    } finally {
      isLoading.value = false
    }
  }
}

const batchEnable = async () => {
  if (confirm(`确定要启用选中的 ${selectedUsers.value.length} 个用户吗？`)) {
    try {
      isLoading.value = true

      // 批量启用用户（逐个调用API）
      const promises = selectedUsers.value.map(userId =>
        fetch(`/api/admin/users/${userId}?currentUserId=${authStore.user?.id || ''}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ status: 'active' })
        })
      )

      const responses = await Promise.all(promises)

      // 检查是否所有请求都成功
      for (const response of responses) {
        if (!response.ok) {
          throw new Error('批量启用失败')
        }
      }

      selectedUsers.value = []
      selectAll.value = false
      toastStore.success('选中用户已启用')
      loadUsersFromAPI() // 重新加载用户列表
    } catch (error) {
      console.error('批量启用失败:', error)
      toastStore.error('操作失败，请稍后重试')
    } finally {
      isLoading.value = false
    }
  }
}

const batchResetPassword = async () => {
  if (confirm(`确定要重置选中 ${selectedUsers.value.length} 个用户的密码吗？`)) {
    try {
      isLoading.value = true
      const newPassword = prompt('请输入新密码（留空则使用默认密码123456）:', '') || '123456'

      // 批量重置密码（逐个调用API）
      const promises = selectedUsers.value.map(userId =>
        fetch(`/api/admin/users/${userId}/reset-password?currentUserId=${authStore.user?.id || ''}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ newPassword: newPassword })
        })
      )

      const responses = await Promise.all(promises)

      // 检查是否所有请求都成功
      for (const response of responses) {
        if (!response.ok) {
          throw new Error('批量重置密码失败')
        }
      }

      selectedUsers.value = []
      selectAll.value = false
      toastStore.success('选中用户的密码已重置')
    } catch (error) {
      console.error('批量重置密码失败:', error)
      toastStore.error('操作失败，请稍后重试')
    } finally {
      isLoading.value = false
    }
  }
}

const batchDelete = async () => {
  if (confirm(`确定要删除选中的 ${selectedUsers.value.length} 个用户吗？此操作不可恢复！`)) {
    try {
      isLoading.value = true

      // 批量删除用户（逐个调用API）
      const promises = selectedUsers.value.map(userId =>
        fetch(`/api/admin/users/${userId}?currentUserId=${authStore.user?.id || ''}`, {
          method: 'DELETE'
        })
      )

      const responses = await Promise.all(promises)

      // 检查是否所有请求都成功
      for (const response of responses) {
        if (!response.ok) {
          throw new Error('批量删除失败')
        }
      }

      selectedUsers.value = []
      selectAll.value = false
      toastStore.success('选中用户已删除')
      loadUsersFromAPI() // 重新加载用户列表
    } catch (error) {
      console.error('批量删除失败:', error)
      toastStore.error('操作失败，请稍后重试')
    } finally {
      isLoading.value = false
    }
  }
}

const closeModal = () => {
  showAddUserModal.value = false
  editingUser.value = null
  Object.assign(userForm, {
    role: 'student',
    username: '',
    name: '',
    faculty: 'cs',
    major: 'cs',
    roleName: '',
    password: '',
    status: 'active'
  })
}

// 分页方法
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadUsersFromAPI()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadUsersFromAPI()
  }
}

// 切换选项卡
const activeTabChanged = async () => {
  filters.faculty = 'all'
  filters.department = 'all'
  filters.major = 'all'
  filters.keyword = ''
  filters.status = 'all'
  currentPage.value = 1

  // 如果是学生选项卡，并行加载系和专业数据，然后立即开始加载用户数据
  if (activeTab.value === 'student') {
    // 并行加载系和专业数据
    Promise.all([
      loadDepartments().catch(error => {
        console.error('加载系列表失败:', error)
      })
    ]).then(() => {
      // 系加载完成后再加载专业数据
      loadMajors().catch(error => {
        console.error('加载专业列表失败:', error)
      })
    })
  } else {
    departments.value = []
    majors.value = []
  }

  // 立即开始加载用户数据，不需要等待系和专业数据加载完成
  loadUsersFromAPI()
}

// 监听学院筛选条件变化，加载对应的系列表
watch(
  () => filters.faculty,
  async (newFacultyId) => {
    if (activeTab.value === 'student' && newFacultyId && newFacultyId !== 'all') {
      await loadDepartments(newFacultyId)
    } else {
      // 重置系和专业筛选
      filters.department = 'all'
      filters.major = 'all'
      departments.value = []
      majors.value = []
    }
    // 重新加载用户数据
    currentPage.value = 1
    loadUsersFromAPI()
  }
)

// 监听系筛选条件变化，加载对应的专业列表
watch(
  () => filters.department,
  async (newDepartmentId) => {
    if (activeTab.value === 'student' && newDepartmentId && newDepartmentId !== 'all') {
      await loadMajors(newDepartmentId)
    } else {
      // 重置专业筛选
      filters.major = 'all'
      majors.value = []
    }
    // 重新加载用户数据
    currentPage.value = 1
    loadUsersFromAPI()
  }
)

// 监听其他筛选条件变化
watch(
  [() => filters.keyword, () => filters.status, () => filters.major],
  () => {
    currentPage.value = 1
    loadUsersFromAPI()
  }
)

// 生命周期
onMounted(async () => {
  try {
    // 并行加载数据
    await Promise.all([
      loadFaculties(),
      loadUsersFromAPI()
    ])

    // 如果当前是学生选项卡，加载系和专业数据
    if (activeTab.value === 'student') {
      await loadDepartments()
      await loadMajors()
    }
  } catch (error) {
    console.error('初始化数据加载失败:', error)
  }
})

// 监听activeTab变化
watch(activeTab, (newTab, oldTab) => {
  activeTabChanged()
  // 移除重复的逻辑处理，避免多次加载数据
})
</script>

<style scoped>
/* 引入共享样式 */
@import '../common/shared-styles.css';

/* 当前登录徽章样式 */
.current-login-badge {
  background-color: #007bff;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}
</style>