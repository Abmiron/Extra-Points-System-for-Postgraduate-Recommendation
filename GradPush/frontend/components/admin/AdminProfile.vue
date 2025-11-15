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
            <label class="form-label">账号</label>
            <input type="text" class="form-control" v-model="profile.adminId" disabled>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">学院</label>
            <input type="text" class="form-control" v-model="profile.faculty" :disabled="!isEditing" required>
          </div>
          <div class="form-group">
            <label class="form-label">角色</label>
            <input type="text" class="form-control" v-model="profile.roleName" :disabled="!isEditing" required>
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
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import api from '../../utils/api'

const authStore = useAuthStore()

const isEditing = ref(false)
const saving = ref(false)
const showChangePassword = ref(false)

const originalProfile = ref({})
const profile = reactive({
  name: '',
  adminId: '',
  faculty: '',
  roleName: '',
  email: '',
  phone: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
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
    // 准备更新数据
    const updateData = {
      name: profile.name,
      faculty: profile.faculty,
      roleName: profile.roleName,
      email: profile.email,
      phone: profile.phone
    }
    
    // 调用API更新个人信息
    const response = await api.updateProfile(updateData)
    
    // 更新auth store中的用户信息
    authStore.updateUserInfo(response.user)
    
    alert('个人信息已更新')
    isEditing.value = false
  } catch (error) {
    console.error('保存失败:', error)
    alert(`保存失败: ${error.message || '请稍后重试'}`)
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
    // 准备修改密码数据
    const passwordData = {
      username: authStore.user.username,
      currentPassword: passwordForm.currentPassword,
      newPassword: passwordForm.newPassword
    }
    
    // 调用API修改密码
    await api.changePassword(passwordData)
    
    alert('密码修改成功')
    closePasswordModal()

    // 清空表单
    Object.assign(passwordForm, {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
  } catch (error) {
    console.error('密码修改失败:', error)
    alert(`密码修改失败: ${error.message || '请稍后重试'}`)
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

// 生命周期
onMounted(() => {
  // 从auth store获取当前用户信息
  if (authStore.user) {
    Object.assign(profile, {
      name: authStore.user.name || '',
      adminId: authStore.user.username || '',
      faculty: authStore.user.faculty || '',
      roleName: authStore.user.roleName || '',
      email: authStore.user.email || '',
      phone: authStore.user.phone || ''
    })
  }
  originalProfile.value = { ...profile }
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

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .form-actions {
    flex-direction: column;
  }
}
</style>

<style>
/* 引入共享样式 */
@import '../common/shared-styles.css';
</style>