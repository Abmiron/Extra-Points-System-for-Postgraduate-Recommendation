<template>
  <div class="page-content">
    <div class="page-title">
      <span>用户管理</span>
      <div>
        <button class="btn btn-outline" @click="importUsers">
          <font-awesome-icon :icon="['fas', 'download']" /> 导入用户
        </button>
        <button class="btn" @click="showAddUserModal = true">
          <font-awesome-icon :icon="['fas', 'plus']" /> 添加用户
        </button>
      </div>
    </div>

    <!-- 选项卡 -->
    <div class="tabs">
      <button class="tab-btn" :class="{ active: activeTab === 'student' }" 
              @click="activeTab = 'student'">学生账户</button>
      <button class="tab-btn" :class="{ active: activeTab === 'teacher' }" 
              @click="activeTab = 'teacher'">教师账户</button>
    </div>

    <!-- 筛选区域 -->
    <div class="filters">
      <div class="filter-group">
        <input type="text" class="form-control" v-model="filters.keyword" 
               placeholder="搜索姓名或学号/工号">
      </div>
      <div class="filter-group">
        <span class="filter-label">学院:</span>
        <select v-model="filters.faculty">
          <option value="all">全部</option>
          <option value="cs">计算机科学系</option>
          <option value="se">软件工程系</option>
          <option value="ai">人工智能系</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">状态:</span>
        <select v-model="filters.status">
          <option value="all">全部</option>
          <option value="active">启用</option>
          <option value="disabled">禁用</option>
        </select>
      </div>
      <button class="btn" @click="searchUsers">搜索</button>
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
      <div class="table-container">
        <table class="application-table">
          <thead>
            <tr>
              <th><input type="checkbox" v-model="selectAll" @change="toggleSelectAll"></th>
              <th>账号</th>
              <th>姓名</th>
              <th>学院</th>
              <th>专业/角色</th>
              <th>状态</th>
              <th>最后登录</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <td><input type="checkbox" v-model="selectedUsers" :value="user.id"></td>
              <td>{{ user.account }}</td>
              <td>{{ user.name }}</td>
              <td>{{ getFacultyText(user.faculty) }}</td>
              <td>{{ user.role === 'student' ? user.major : user.roleName }}</td>
              <td>
                <span :class="`status-badge status-${user.status === 'active' ? 'approved' : 'rejected'}`">
                  {{ user.status === 'active' ? '启用' : '禁用' }}
                </span>
              </td>
              <td>{{ formatDate(user.lastLogin) }}</td>
              <td>
                <button class="btn-outline btn small-btn" @click="editUser(user)">
                  <font-awesome-icon :icon="['fas', 'edit']" />
                </button>
                <button v-if="user.status === 'active'" 
                        class="btn-outline btn small-btn" 
                        @click="toggleUserStatus(user.id, 'disabled')">
                  <font-awesome-icon :icon="['fas', 'ban']" />
                </button>
                <button v-else 
                        class="btn-outline btn small-btn" 
                        @click="toggleUserStatus(user.id, 'active')">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </button>
                <button class="btn-outline btn small-btn" @click="resetPassword(user.id)">
                  <font-awesome-icon :icon="['fas', 'key']" />
                </button>
                <button class="btn-outline btn small-btn" @click="viewUserHistory(user.id)">
                  <font-awesome-icon :icon="['fas', 'history']" />
                </button>
              </td>
            </tr>
            <tr v-if="filteredUsers.length === 0">
              <td colspan="8" class="no-data">暂无用户数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 分页控件 -->
    <div class="pagination">
      <div>显示 {{ startIndex + 1 }}-{{ endIndex }} 条，共 {{ totalUsers }} 条记录</div>
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
                <select class="form-control" v-model="userForm.role" required>
                  <option value="student">学生</option>
                  <option value="teacher">教师</option>
                  <option value="admin">管理员</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">{{ userForm.role === 'student' ? '学号' : '工号' }}</label>
                <input type="text" class="form-control" v-model="userForm.account" required>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">姓名</label>
                <input type="text" class="form-control" v-model="userForm.name" required>
              </div>
              <div class="form-group">
                <label class="form-label">学院</label>
                <select class="form-control" v-model="userForm.faculty" required>
                  <option value="cs">计算机科学系</option>
                  <option value="se">软件工程系</option>
                  <option value="ai">人工智能系</option>
                </select>
              </div>
            </div>
            <div class="form-row" v-if="userForm.role === 'student'">
              <div class="form-group">
                <label class="form-label">专业</label>
                <select class="form-control" v-model="userForm.major" required>
                  <option value="cs">计算机科学与技术</option>
                  <option value="se">软件工程</option>
                  <option value="ai">人工智能</option>
                </select>
              </div>
            </div>
            <div class="form-row" v-else>
              <div class="form-group">
                <label class="form-label">角色</label>
                <input type="text" class="form-control" v-model="userForm.roleName" 
                       :placeholder="userForm.role === 'teacher' ? '如：审核员' : '如：系统管理员'" required>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">初始密码</label>
                <input type="password" class="form-control" v-model="userForm.password" 
                       :required="!editingUser">
                <div class="help-text">若不修改密码请留空</div>
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

const activeTab = ref('student')
const showAddUserModal = ref(false)
const editingUser = ref(null)
const selectAll = ref(false)
const selectedUsers = ref([])
const currentPage = ref(1)
const pageSize = 10

const filters = reactive({
  keyword: '',
  faculty: 'all',
  status: 'all'
})

const userForm = reactive({
  role: 'student',
  account: '',
  name: '',
  faculty: 'cs',
  major: 'cs',
  roleName: '',
  password: '',
  status: 'active'
})

// 模拟用户数据
const users = ref([
  {
    id: 1,
    role: 'student',
    account: '12320253211234',
    name: '张同学',
    faculty: 'cs',
    major: 'cs',
    status: 'active',
    lastLogin: '2023-09-10T15:30:00Z'
  },
  {
    id: 2,
    role: 'teacher',
    account: '2000123456',
    name: '张老师',
    faculty: 'cs',
    roleName: '审核员',
    status: 'active',
    lastLogin: '2023-09-11T09:45:00Z'
  },
  {
    id: 3,
    role: 'student',
    account: '12320253215678',
    name: '李同学',
    faculty: 'se',
    major: 'se',
    status: 'disabled',
    lastLogin: '2023-08-25T14:20:00Z'
  },
  {
    id: 4,
    role: 'admin',
    account: 'admin001',
    name: '管理员',
    faculty: 'cs',
    roleName: '系统管理员',
    status: 'active',
    lastLogin: '2023-09-12T10:15:00Z'
  }
])

// 计算属性
const filteredUsers = computed(() => {
  let filtered = users.value.filter(user => {
    const tabMatch = activeTab.value === user.role
    const keywordMatch = !filters.keyword || 
                         user.name.includes(filters.keyword) || 
                         user.account.includes(filters.keyword)
    const facultyMatch = filters.faculty === 'all' || user.faculty === filters.faculty
    const statusMatch = filters.status === 'all' || user.status === filters.status
    
    return tabMatch && keywordMatch && facultyMatch && statusMatch
  })
  
  return filtered
})

const totalUsers = computed(() => filteredUsers.value.length)
const totalPages = computed(() => Math.ceil(totalUsers.value / pageSize))
const startIndex = computed(() => (currentPage.value - 1) * pageSize)
const endIndex = computed(() => Math.min(startIndex.value + pageSize, totalUsers.value))

const paginatedUsers = computed(() => {
  return filteredUsers.value.slice(startIndex.value, endIndex.value)
})

// 方法
const getFacultyText = (faculty) => {
  const faculties = {
    cs: '计算机科学系',
    se: '软件工程系',
    ai: '人工智能系'
  }
  return faculties[faculty] || faculty
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const searchUsers = () => {
  currentPage.value = 1
}

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedUsers.value = filteredUsers.value.map(user => user.id)
  } else {
    selectedUsers.value = []
  }
}

const importUsers = () => {
  alert('用户导入功能开发中...')
}

const editUser = (user) => {
  editingUser.value = user
  Object.assign(userForm, user)
  userForm.password = '' // 重置密码字段
  showAddUserModal.value = true
}

const saveUser = () => {
  if (editingUser.value) {
    // 更新用户
    const index = users.value.findIndex(u => u.id === editingUser.value.id)
    if (index !== -1) {
      users.value[index] = { ...userForm, id: editingUser.value.id }
    }
  } else {
    // 添加新用户
    const newUser = {
      id: Math.max(...users.value.map(u => u.id)) + 1,
      ...userForm
    }
    users.value.push(newUser)
  }
  
  closeModal()
  alert('用户保存成功')
}

const toggleUserStatus = (userId, status) => {
  const user = users.value.find(u => u.id === userId)
  if (user) {
    user.status = status
    alert(`用户已${status === 'active' ? '启用' : '禁用'}`)
  }
}

const resetPassword = (userId) => {
  if (confirm('确定要重置该用户的密码吗？')) {
    alert('密码已重置为默认密码（123456）')
  }
}

const viewUserHistory = (userId) => {
  alert(`查看用户 ${userId} 的操作历史`)
}

const batchDisable = () => {
  if (confirm(`确定要禁用选中的 ${selectedUsers.value.length} 个用户吗？`)) {
    selectedUsers.value.forEach(userId => {
      const user = users.value.find(u => u.id === userId)
      if (user) user.status = 'disabled'
    })
    selectedUsers.value = []
    selectAll.value = false
  }
}

const batchEnable = () => {
  if (confirm(`确定要启用选中的 ${selectedUsers.value.length} 个用户吗？`)) {
    selectedUsers.value.forEach(userId => {
      const user = users.value.find(u => u.id === userId)
      if (user) user.status = 'active'
    })
    selectedUsers.value = []
    selectAll.value = false
  }
}

const batchResetPassword = () => {
  if (confirm(`确定要重置选中 ${selectedUsers.value.length} 个用户的密码吗？`)) {
    alert('选中用户的密码已重置为默认密码（123456）')
    selectedUsers.value = []
    selectAll.value = false
  }
}

const batchDelete = () => {
  if (confirm(`确定要删除选中的 ${selectedUsers.value.length} 个用户吗？此操作不可恢复！`)) {
    users.value = users.value.filter(user => !selectedUsers.value.includes(user.id))
    selectedUsers.value = []
    selectAll.value = false
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const closeModal = () => {
  showAddUserModal.value = false
  editingUser.value = null
  Object.assign(userForm, {
    role: 'student',
    account: '',
    name: '',
    faculty: 'cs',
    major: 'cs',
    roleName: '',
    password: '',
    status: 'active'
  })
}

// 生命周期
onMounted(() => {
  // 可以从API加载用户数据
})
</script>

<style scoped>
.tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #ddd;
}

.tab-btn {
  padding: 10px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  border-bottom: 2px solid transparent;
}

.tab-btn.active {
  color: #003366;
  border-bottom-color: #003366;
  font-weight: 500;
}

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

.batch-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
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

.status-rejected {
  background-color: #fdedec;
  color: #e74c3c;
}

.no-data {
  text-align: center;
  color: #666;
  padding: 40px;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.pagination-controls {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  background-color: #003366;
  color: white;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn:hover {
  background-color: #002244;
}

.btn-outline {
  background-color: transparent;
  color: #003366;
  border: 1px solid #003366;
}

.btn-outline:hover {
  background-color: #003366;
  color: white;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn:disabled:hover {
  background-color: #003366;
}

.small-btn {
  padding: 5px 8px;
  font-size: 12px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.form-row .form-group {
  flex: 1;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-control:focus {
  outline: none;
  border-color: #003366;
  box-shadow: 0 0 0 2px rgba(0, 51, 102, 0.2);
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.help-text {
  font-size: 12px;
  color: #6c757d;
  margin-top: 5px;
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .batch-actions {
    flex-wrap: wrap;
  }
  
  .pagination {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .application-table {
    font-size: 14px;
  }
  
  .application-table th,
  .application-table td {
    padding: 8px 10px;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
}
</style>