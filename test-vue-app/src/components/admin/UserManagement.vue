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
        <select class="form-control" v-model="filters.faculty">
          <option value="all">全部</option>
          <option value="cs">计算机科学系</option>
          <option value="se">软件工程系</option>
          <option value="ai">人工智能系</option>
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
            <tr v-for="user in paginatedUsers" :key="user.id">
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
                <div class="action-buttons">
                  <button class="btn-outline btn small-btn" @click="editUser(user)" title="编辑">
                    <font-awesome-icon :icon="['fas', 'edit']" />
                  </button>
                  <button v-if="user.status === 'active'" 
                          class="btn-outline btn small-btn" 
                          @click="toggleUserStatus(user.id, 'disabled')"
                          title="禁用">
                    <font-awesome-icon :icon="['fas', 'ban']" />
                  </button>
                  <button v-else 
                          class="btn-outline btn small-btn" 
                          @click="toggleUserStatus(user.id, 'active')"
                          title="启用">
                    <font-awesome-icon :icon="['fas', 'check']" />
                  </button>
                  <button class="btn-outline btn small-btn" @click="resetPassword(user.id)" title="重置密码">
                    <font-awesome-icon :icon="['fas', 'key']" />
                  </button>
                  <button class="btn-outline btn small-btn" @click="viewUserHistory(user.id)" title="操作历史">
                    <font-awesome-icon :icon="['fas', 'history']" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="paginatedUsers.length === 0">
              <td colspan="8" class="no-data">暂无用户数据</td>
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
  },
  // 添加更多测试数据
  {
    id: 5,
    role: 'student',
    account: '12320253219876',
    name: '王同学',
    faculty: 'ai',
    major: 'ai',
    status: 'active',
    lastLogin: '2023-09-05T11:20:00Z'
  },
  {
    id: 6,
    role: 'teacher',
    account: '2000654321',
    name: '李老师',
    faculty: 'se',
    roleName: '评审员',
    status: 'active',
    lastLogin: '2023-09-08T16:45:00Z'
  },
  {
    id: 7,
    role: 'student',
    account: '12320253214321',
    name: '赵同学',
    faculty: 'cs',
    major: 'cs',
    status: 'disabled',
    lastLogin: '2023-08-20T09:30:00Z'
  },
  {
    id: 8,
    role: 'student',
    account: '12320253218765',
    name: '钱同学',
    faculty: 'se',
    major: 'se',
    status: 'active',
    lastLogin: '2023-09-15T14:10:00Z'
  },
  {
    id: 9,
    role: 'teacher',
    account: '2000789012',
    name: '陈老师',
    faculty: 'ai',
    roleName: '审核员',
    status: 'active',
    lastLogin: '2023-09-14T10:25:00Z'
  },
  {
    id: 10,
    role: 'student',
    account: '12320253215432',
    name: '孙同学',
    faculty: 'ai',
    major: 'ai',
    status: 'active',
    lastLogin: '2023-09-12T13:40:00Z'
  },
  {
    id: 11,
    role: 'student',
    account: '12320253217654',
    name: '周同学',
    faculty: 'cs',
    major: 'cs',
    status: 'disabled',
    lastLogin: '2023-08-18T15:55:00Z'
  },
  {
    id: 12,
    role: 'admin',
    account: 'admin002',
    name: '超级管理员',
    faculty: 'cs',
    roleName: '系统管理员',
    status: 'active',
    lastLogin: '2023-09-16T08:20:00Z'
  }
])

// 计算属性
const filteredUsers = computed(() => {
  return users.value.filter(user => {
    const tabMatch = activeTab.value === user.role
    const keywordMatch = !filters.keyword || 
                         user.name.includes(filters.keyword) || 
                         user.account.includes(filters.keyword)
    const facultyMatch = filters.faculty === 'all' || user.faculty === filters.faculty
    const statusMatch = filters.status === 'all' || user.status === filters.status
    
    return tabMatch && keywordMatch && facultyMatch && statusMatch
  })
})

// 分页相关计算属性
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
    selectedUsers.value = paginatedUsers.value.map(user => user.id)
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

// 分页方法
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

// 生命周期
onMounted(() => {
  // 可以从API加载用户数据
})
</script>

<style scoped>
/* 组件特有样式 */
.tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #ddd;
}

.tab-btn {
  padding: 12px 24px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn.active {
  border-bottom-color: #003366;
  color: #003366;
  font-weight: 500;
}

.batch-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

/* 覆盖或补充共享样式 */
.application-table th:last-child,
.application-table td:last-child {
  width: 180px;
  min-width: 180px;
  text-align: center;
}
</style>

<style>
/* 引入共享样式 */
@import '../common/shared-styles.css';
</style>