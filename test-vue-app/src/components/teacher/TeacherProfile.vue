<template>
  <div class="page-content">
    <div class="page-title">
      <span>个人信息</span>
      <button class="btn btn-outline" @click="toggleEdit" :disabled="saving">
        <font-awesome-icon :icon="['fas', 'edit']" />
        {{ isEditing ? '取消编辑' : '编辑信息' }}
      </button>
    </div>

    <div class="card">
      <div class="card-title">基本资料</div>
      <form @submit.prevent="saveProfile">
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">姓名</label>
            <input type="text" class="form-control" v-model="profile.name" :disabled="!isEditing" required>
          </div>
          <div class="form-group">
            <label class="form-label">工号</label>
            <input type="text" class="form-control" v-model="profile.teacherId" disabled>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">学院</label>
            <input type="text" class="form-control" v-model="profile.faculty" :disabled="!isEditing" required>
          </div>
          <div class="form-group">
            <label class="form-label">职称</label>
            <input type="text" class="form-control" v-model="profile.title" :disabled="!isEditing" required>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">电子邮箱</label>
            <input type="email" class="form-control" v-model="profile.email" :disabled="!isEditing" required>
          </div>
          <div class="form-group">
            <label class="form-label">手机号码</label>
            <input type="tel" class="form-control" v-model="profile.phone" :disabled="!isEditing" required>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">办公室地址</label>
            <input type="text" class="form-control" v-model="profile.office" :disabled="!isEditing">
          </div>
          <div class="form-group">
            <label class="form-label">办公电话</label>
            <input type="tel" class="form-control" v-model="profile.officePhone" :disabled="!isEditing">
          </div>
        </div>

        <div v-if="isEditing" class="form-actions">
          <button type="button" class="btn btn-outline" @click="cancelEdit" :disabled="saving">
            取消
          </button>
          <button type="submit" class="btn" :disabled="saving">
            <font-awesome-icon v-if="saving" :icon="['fas', 'spinner']" spin />
            {{ saving ? '保存中...' : '保存更改' }}
          </button>
        </div>
      </form>
    </div>



    <!-- 审核统计 -->
    <div class="card">
      <div class="card-title">审核统计</div>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">待审核申请</div>
          <div class="stat-value">{{ stats.pendingCount }}</div>
          <div class="stat-note">需要尽快处理</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">本月已审核</div>
          <div class="stat-value">{{ stats.reviewedThisMonth }}</div>
          <div class="stat-note">本月审核数量</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">总审核数量</div>
          <div class="stat-value">{{ stats.totalReviewed }}</div>
          <div class="stat-note">累计审核数量</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">平均审核时间</div>
          <div class="stat-value">{{ stats.avgReviewTime }}</div>
          <div class="stat-note">天</div>
        </div>
      </div>
    </div>

    <!-- 修改密码 -->
    <div class="card">
      <div class="card-title">安全设置</div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">修改密码</label>
          <button class="btn btn-outline" @click="showChangePassword = true">
            <font-awesome-icon :icon="['fas', 'key']" /> 修改密码
          </button>
        </div>
      </div>
    </div>

    <!-- 修改密码模态框 -->
    <div v-if="showChangePassword" class="modal-overlay" @click="closePasswordModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>修改密码</h3>
          <button class="close-btn" @click="closePasswordModal">
            <font-awesome-icon :icon="['fas', 'times']" />
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="changePassword">
            <div class="form-group">
              <label class="form-label">当前密码</label>
              <input type="password" class="form-control" v-model="passwordForm.currentPassword" required>
            </div>
            <div class="form-group">
              <label class="form-label">新密码</label>
              <input type="password" class="form-control" v-model="passwordForm.newPassword" required minlength="6">
              <div class="help-text">密码长度至少6位</div>
            </div>
            <div class="form-group">
              <label class="form-label">确认新密码</label>
              <input type="password" class="form-control" v-model="passwordForm.confirmPassword" required>
              <div v-if="passwordForm.newPassword !== passwordForm.confirmPassword" class="error-text">两次输入的密码不一致</div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <div class="modal-actions">
            <button class="btn btn-outline" @click="closePasswordModal">取消</button>
            <button class="btn" @click="changePassword"
              :disabled="passwordForm.newPassword !== passwordForm.confirmPassword">
              确认修改
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()

const isEditing = ref(false)
const saving = ref(false)
const showChangePassword = ref(false)

const originalProfile = ref({})
const profile = reactive({
  name: '',
  teacherId: '',
  faculty: '',
  title: '',
  email: '',
  phone: '',
  office: '',
  officePhone: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const stats = reactive({
  pendingCount: 0,
  reviewedThisMonth: 0,
  totalReviewed: 0,
  avgReviewTime: '1.5'
})

// 计算属性
const pendingApplications = computed(() => {
  const savedApplications = JSON.parse(localStorage.getItem('studentApplications') || '[]')
  return savedApplications.filter(app => app.status === 'pending')
})

const reviewedApplications = computed(() => {
  const savedApplications = JSON.parse(localStorage.getItem('studentApplications') || '[]')
  return savedApplications.filter(app => app.status === 'approved' || app.status === 'rejected')
})

const toggleEdit = () => {
  if (isEditing.value) {
    // 取消编辑，恢复原始数据
    Object.assign(profile, originalProfile.value)
    isEditing.value = false
  } else {
    // 开始编辑，保存原始数据
    originalProfile.value = { ...profile }
    isEditing.value = true
  }
}

const cancelEdit = () => {
  Object.assign(profile, originalProfile.value)
  isEditing.value = false
}

const saveProfile = async () => {
  saving.value = true

  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 保存到本地存储中的用户数据
    const users = JSON.parse(localStorage.getItem('users') || '{}')
    const currentUser = users[authStore.user.username]
    
    if (currentUser) {
      // 更新用户信息
      currentUser.name = profile.name
      currentUser.teacherId = profile.teacherId
      currentUser.faculty = profile.faculty
      currentUser.title = profile.title
      currentUser.email = profile.email
      currentUser.phone = profile.phone
      currentUser.office = profile.office
      currentUser.officePhone = profile.officePhone
      
      // 保存更新后的用户数据
      localStorage.setItem('users', JSON.stringify(users))
      
      // 更新auth store中的用户信息
      authStore.login({ ...currentUser })
    }

    alert('个人信息已更新')
    isEditing.value = false
  } catch (error) {
    console.error('保存失败:', error)
    alert('保存失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

const changePassword = async () => {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    alert('两次输入的密码不一致')
    return
  }

  if (passwordForm.newPassword.length < 6) {
    alert('密码长度至少6位')
    return
  }

  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 更新密码到localStorage
    const users = JSON.parse(localStorage.getItem('users') || '{}')
    const currentUser = users[authStore.user.username]
    
    if (currentUser && currentUser.password === passwordForm.currentPassword) {
      currentUser.password = passwordForm.newPassword
      localStorage.setItem('users', JSON.stringify(users))
      alert('密码修改成功')
    } else {
      alert('当前密码错误')
      return
    }

    closePasswordModal()

    // 清空表单
    Object.assign(passwordForm, {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
  } catch (error) {
    console.error('密码修改失败:', error)
    alert('密码修改失败，请稍后重试')
  }
}

const closePasswordModal = () => {
  showChangePassword.value = false
  // 清空表单
  Object.assign(passwordForm, {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
}

const calculateStats = () => {
  stats.pendingCount = pendingApplications.value.length
  stats.totalReviewed = reviewedApplications.value.length

  // 计算本月审核数量
  const currentMonth = new Date().getMonth()
  const currentYear = new Date().getFullYear()
  stats.reviewedThisMonth = reviewedApplications.value.filter(app => {
    const reviewDate = new Date(app.reviewedAt)
    return reviewDate.getMonth() === currentMonth && reviewDate.getFullYear() === currentYear
  }).length
}

// 生命周期
onMounted(() => {
  // 从auth store获取当前用户信息
  if (authStore.user) {
    Object.assign(profile, {
      name: authStore.user.name || '',
      teacherId: authStore.user.username || '',
      faculty: authStore.user.faculty || '',
      title: authStore.user.title || '',
      email: authStore.user.email || '',
      phone: authStore.user.phone || '',
      office: authStore.user.office || '',
      officePhone: authStore.user.officePhone || ''
    })
  }
  originalProfile.value = { ...profile }

  // 计算统计信息
  calculateStats()
})
</script>

<style scoped>
/* 组件特有样式 */
/* 模态框底部按钮居中 */
.modal-footer {
  display: flex;
  justify-content: center;
  padding: 15px;
  border-top: 1px solid #e8e8e8;
}

.modal-actions {
  display: flex;
  gap: 15px;
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

.form-control:disabled {
  background-color: #f5f5f5;
  color: #666;
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.error-text {
  font-size: 12px;
  color: #e74c3c;
  margin-top: 5px;
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

/* 模态框样式 */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .form-actions {
    flex-direction: column;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<style>
/* 引入共享样式 */
@import '../common/shared-styles.css';
</style>