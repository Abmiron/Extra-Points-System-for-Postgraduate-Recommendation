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
        <input type="text" class="form-control" v-model="filters.keyword" placeholder="搜索姓名或学号/工号" @keyup.enter="searchUsers">
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
              <th>专业/角色</th>
              <th>状态</th>
              <th>最后登录</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedUsers" :key="user.id">
              <td><input type="checkbox" v-model="selectedUsers" :value="user.id"></td>
              <td>{{ user.username }}</td>
              <td>{{ user.name }}</td>
              <td>{{ getFacultyText(user.faculty) }}</td>
              <td>{{ user.role === 'student' ? user.major : (user.role === 'teacher' ? user.roleName : user.roleName || '管理员') }}</td>
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
                  <button v-if="user.status === 'active'" class="btn-outline btn small-btn"
                    @click="toggleUserStatus(user.id, 'disabled')" title="禁用">
                    <font-awesome-icon :icon="['fas', 'ban']" />
                  </button>
                  <button v-else class="btn-outline btn small-btn" @click="toggleUserStatus(user.id, 'active')"
                    title="启用">
                    <font-awesome-icon :icon="['fas', 'check']" />
                  </button>
                  <button class="btn-outline btn small-btn" @click="resetPassword(user.id)" title="重置密码">
                    <font-awesome-icon :icon="['fas', 'key']" />
                  </button>
                  <button class="btn-outline btn small-btn" @click="deleteUser(user.id)" title="删除">
                    <font-awesome-icon :icon="['fas', 'trash']" />
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
                <label class="form-label">{{ userForm.role === 'student' ? '学号' : (userForm.role === 'teacher' ? '工号' : '管理员账号') }}</label>
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
            <div class="form-row" v-else-if="userForm.role === 'teacher'">
              <div class="form-group">
                <label class="form-label">角色</label>
                <input type="text" class="form-control" v-model="userForm.roleName"
                  placeholder="如：审核员" required>
              </div>
            </div>
            <div class="form-row" v-else-if="userForm.role === 'admin'">
              <div class="form-group">
                <label class="form-label">管理员类型</label>
                <input type="text" class="form-control" v-model="userForm.roleName"
                  placeholder="如：系统管理员" required>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">初始密码</label>
                <input type="password" class="form-control" v-model="userForm.password" :required="!editingUser">
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

<style scoped>
/* 卡片相对定位，确保加载状态只在卡片内显示 */
.card {
  position: relative;
}

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

<script setup>
import { ref, reactive, computed, onMounted, watchEffect } from 'vue'
import { useAuthStore } from '../../stores/auth'

const activeTab = ref('student')
const showAddUserModal = ref(false)
const editingUser = ref(null)
const selectAll = ref(false)
const selectedUsers = ref([])
const currentPage = ref(1)
const pageSize = 10
const isLoading = ref(false)
const authStore = useAuthStore()

const filters = reactive({
  keyword: '',
  faculty: 'all',
  status: 'all'
})

const userForm = reactive({
  role: 'student',
  username: '',
  name: '',
  faculty: 'cs',
  major: 'cs',
  roleName: '',
  password: '',
  status: 'active'
})

// 从后端API获取用户数据
const users = ref([])
const totalUsers = ref(0)
const totalPages = ref(0)

// 从后端API加载用户数据的函数
const loadUsersFromAPI = async () => {
  try {
    isLoading.value = true
    const role = activeTab.value
    const status = filters.status === 'all' ? '' : filters.status
    const search = filters.keyword || ''
    
    // 构建API请求URL
    const params = new URLSearchParams({
      currentUserId: authStore.user.id,
      page: currentPage.value,
      per_page: pageSize,
      role: role,
      status: status,
      search: search
    })
    
    const response = await fetch(`http://localhost:5001/api/admin/users?${params}`)
    
    if (!response.ok) {
      throw new Error('获取用户数据失败')
    }
    
    const data = await response.json()
    users.value = data.users
    totalUsers.value = data.total
    totalPages.value = data.pages
  } catch (error) {
    console.error('加载用户数据失败:', error)
    alert('加载用户数据失败，请稍后重试')
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
  Object.assign(userForm, {
    id: user.id,
    role: user.role,
    username: user.username,
    name: user.name,
    faculty: user.faculty,
    major: user.major,
    roleName: user.roleName,
    status: user.status,
    password: '' // 重置密码字段
  })
  showAddUserModal.value = true
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
      faculty: userForm.faculty,
      status: userForm.status,
      ...(userForm.role === 'student' ? {
        major: userForm.major
      } : {
        roleName: userForm.roleName
      })
    }
    
    // 如果提供了密码，则包含密码字段
    if (userForm.password) {
      userData.password = userForm.password
    }
    
    let response
    if (editingUser.value) {
      // 更新用户 - 调用PUT API
      response = await fetch(`http://localhost:5001/api/admin/users/${editingUser.value.id}?currentUserId=${authStore.user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      })
    } else {
      // 添加新用户 - 调用POST API
      response = await fetch(`http://localhost:5001/api/register`, {
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
    
    closeModal()
    alert(editingUser.value ? '用户信息更新成功' : '用户添加成功')
    loadUsersFromAPI() // 重新加载用户列表
  } catch (error) {
    console.error('保存用户失败:', error)
    alert(error.message || '保存失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

const toggleUserStatus = async (userId, status) => {
  try {
    isLoading.value = true
    
    const response = await fetch(`http://localhost:5001/api/admin/users/${userId}?currentUserId=${authStore.user.id}`, {
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
    
    alert(`用户已${status === 'active' ? '启用' : '禁用'}`)
    loadUsersFromAPI() // 重新加载用户列表
  } catch (error) {
    console.error('更新用户状态失败:', error)
    alert(error.message || '操作失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

const resetPassword = async (userId) => {
  if (confirm('确定要重置该用户的密码吗？')) {
    try {
      isLoading.value = true
      const newPassword = prompt('请输入新密码（留空则使用默认密码123456）:', '') || '123456'
      
      const response = await fetch(`http://localhost:5001/api/admin/users/${userId}/reset-password?currentUserId=${authStore.user.id}`, {
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
      
      alert('密码重置成功')
    } catch (error) {
      console.error('重置密码失败:', error)
      alert(error.message || '重置密码失败，请稍后重试')
    } finally {
      isLoading.value = false
    }
  }
}

const deleteUser = async (userId) => {
  if (confirm(`确定要删除该用户吗？此操作不可恢复！`)) {
    try {
      isLoading.value = true
      
      const response = await fetch(`http://localhost:5001/api/admin/users/${userId}?currentUserId=${authStore.user.id}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error('删除用户失败')
      }
      
      alert('用户已删除')
      loadUsersFromAPI() // 重新加载用户列表
    } catch (error) {
      console.error('删除用户失败:', error)
      alert('操作失败，请稍后重试')
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
        fetch(`http://localhost:5001/api/admin/users/${userId}?currentUserId=${authStore.user.id}`, {
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
      alert('选中用户已禁用')
      loadUsersFromAPI() // 重新加载用户列表
    } catch (error) {
      console.error('批量禁用失败:', error)
      alert('操作失败，请稍后重试')
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
          fetch(`http://localhost:5001/api/admin/users/${userId}?currentUserId=${authStore.user.id}`, {
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
      alert('选中用户已启用')
      loadUsersFromAPI() // 重新加载用户列表
    } catch (error) {
      console.error('批量启用失败:', error)
      alert('操作失败，请稍后重试')
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
          fetch(`http://localhost:5001/api/admin/users/${userId}/reset-password?currentUserId=${authStore.user.id}`, {
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
      alert('选中用户的密码已重置')
    } catch (error) {
      console.error('批量重置密码失败:', error)
      alert('操作失败，请稍后重试')
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
          fetch(`http://localhost:5001/api/admin/users/${userId}?currentUserId=${authStore.user.id}`, {
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
      alert('选中用户已删除')
      loadUsersFromAPI() // 重新加载用户列表
    } catch (error) {
      console.error('批量删除失败:', error)
      alert('操作失败，请稍后重试')
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

// 监听选项卡变化
const activeTabChanged = () => {
  currentPage.value = 1
  loadUsersFromAPI()
}

// 生命周期
onMounted(() => {
  // 从后端API加载用户数据
  loadUsersFromAPI()
})

// 监听activeTab变化
watchEffect(() => {
  activeTabChanged()
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