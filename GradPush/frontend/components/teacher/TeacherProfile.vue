<template>
  <div class="page-content">
    <div class="page-title">
      <span>个人信息</span>
      <button class="btn btn-outline" @click="toggleEdit" :disabled="saving || uploadingAvatar">
        <font-awesome-icon :icon="['fas', 'edit']" />
        {{ isEditing ? '取消编辑' : '编辑信息' }}
      </button>
    </div>

    <div class="card">
      <div class="card-title">基本资料</div>
      <form @submit.prevent="saveProfile">
        <!-- 头像显示与上传 -->
        <div class="form-row avatar-row">
          <div class="form-group avatar-group">
            <div class="avatar-container">
              <img :src="getAvatarUrl" alt="头像" class="avatar-img" />
              <div class="avatar-overlay" @click="triggerAvatarUpload">
                <font-awesome-icon :icon="['fas', 'camera']" class="avatar-icon" />
                <span>更换头像</span>
              </div>
            </div>
            <div class="avatar-tooltip">
              上传图片限制：JPG、PNG格式，大小不超过2MB
            </div>
            <input type="file" ref="avatarInput" @change="handleAvatarChange" accept="image/*" style="display: none;">
          </div>
        </div>

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
            <select class="form-control" v-model="profile.facultyId" :disabled="!isEditing" required>
              <option value="" disabled>请选择学院</option>
              <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.id">
                {{ faculty.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">职称</label>
            <input type="text" class="form-control" v-model="profile.title" :disabled="!isEditing">
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">电子邮箱</label>
            <input type="email" class="form-control" v-model="profile.email" :disabled="!isEditing">
          </div>
          <div class="form-group">
            <label class="form-label">手机号码</label>
            <input type="tel" class="form-control" v-model="profile.phone" :disabled="!isEditing">
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
import api from '../../utils/api'

const authStore = useAuthStore()

const isEditing = ref(false)
const saving = ref(false)
const showChangePassword = ref(false)
const uploadingAvatar = ref(false)
const avatarInput = ref(null)

const originalProfile = ref({})
const profile = reactive({
  name: '',
  teacherId: '',
  facultyId: '',
  facultyName: '',
  title: '',
  email: '',
  phone: '',
  office: '',
  officePhone: '',
  avatar: ''
})

// 学院列表
const faculties = ref([])

// 计算头像URL，确保包含完整的服务器地址前缀
const getAvatarUrl = computed(() => {
  if (!profile.avatar || profile.avatar === '') return '/images/default-avatar.jpg'
  // 检查头像URL是否已经包含完整路径
  if (profile.avatar.startsWith('http://') || profile.avatar.startsWith('https://')) {
    return profile.avatar
  }
  // 检查是否是本地默认头像路径
  if (profile.avatar.startsWith('/images/')) {
    return profile.avatar
  }
  // 添加服务器地址前缀
  return `http://localhost:5001${profile.avatar}`
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})



// 计算属性 - 不再使用本地存储，改为从API获取

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

const triggerAvatarUpload = () => {
  if (avatarInput.value) {
    avatarInput.value.click()
  }
}

const handleAvatarChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 检查文件大小（限制为2MB）
  if (file.size > 2 * 1024 * 1024) {
    alert('头像文件大小不能超过2MB')
    return
  }

  uploadingAvatar.value = true
  try {
    // 调用上传头像API
    const response = await api.uploadAvatar(authStore.user.username, file)
    
    // 更新用户信息
    authStore.updateUserInfo(response.user)
    
    // 更新本地profile中的头像
    profile.avatar = response.user.avatar
    
    alert('头像上传成功')
  } catch (error) {
    console.error('头像上传失败:', error)
    alert(`头像上传失败: ${error.message || '请稍后重试'}`)
  } finally {
    uploadingAvatar.value = false
    // 清空文件输入
    if (avatarInput.value) {
      avatarInput.value.value = ''
    }
  }
}

// 加载学院列表
const loadFaculties = async () => {
  try {
    const response = await api.getFaculties()
    faculties.value = response.faculties
  } catch (error) {
    console.error('加载学院列表失败:', error)
  }
}

const saveProfile = async () => {
  saving.value = true

  try {
    // 准备更新数据
    const updateData = {
      username: profile.teacherId, // 添加用户名参数
      name: profile.name,
      facultyId: profile.facultyId,
      title: profile.title,
      email: profile.email,
      phone: profile.phone,
      office: profile.office,
      officePhone: profile.officePhone
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
onMounted(async () => {
  // 加载学院列表
  await loadFaculties()
  
  // 从auth store获取当前用户信息
  if (authStore.user) {
    Object.assign(profile, {
      name: authStore.user.name || '',
      teacherId: authStore.user.username || '',
      facultyId: authStore.user.facultyId || '',
      facultyName: authStore.user.faculty || '',
      title: authStore.user.title || '',
      email: authStore.user.email || '',
      phone: authStore.user.phone || '',
      office: authStore.user.office || '',
      officePhone: authStore.user.officePhone || '',
      avatar: authStore.user.avatar || ''
    })
  }
  originalProfile.value = { ...profile }
})
</script>

<style scoped>
/* 引入共享样式 */
@import '../common/shared-styles.css';

.teacher-profile {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}



.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  align-items: center;
}

.form-group {
  flex: 1;
}

.label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.input:focus {
  outline: none;
  border-color: #409eff;
}

.button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-right: 10px;
}

.button-primary {
  background-color: #409eff;
  color: white;
}

.button-primary:hover {
  background-color: #66b1ff;
}

.button-success {
  background-color: #67c23a;
  color: white;
}

.button-success:hover {
  background-color: #85ce61;
}

.button-default {
  background-color: #909399;
  color: white;
}

.button-default:hover {
  background-color: #a6a9ad;
}

.button:disabled {
  background-color: #c0c4cc;
  cursor: not-allowed;
}

/* 头像样式 */
.avatar-container {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 20px;
}

.avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.avatar-upload-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s;
  cursor: pointer;
  color: white;
}

.avatar-container:hover .avatar-upload-overlay {
  opacity: 1;
}

.avatar-upload-text {
  font-size: 0.875rem;
  margin-top: 5px;
}



/* 安全设置样式 */
.security-section {
  margin-top: 30px;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.security-item:last-child {
  border-bottom: none;
}

.security-label {
  font-weight: 500;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 500;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #909399;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-close:hover {
  color: #606266;
}

/* 头像样式 */
.avatar-row {
  justify-content: center;
  margin-bottom: 20px;
}

.avatar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  position: relative;
}

.avatar-container {
  position: relative;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #e8e8e8;
  cursor: pointer;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  /* 添加抗锯齿效果 */
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
  /* 添加轻微阴影增强视觉效果 */
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.1);
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.avatar-container:hover .avatar-overlay {
  opacity: 1;
}

.avatar-icon {
  font-size: 24px;
  margin-bottom: 5px;
}

.avatar-tooltip {
  position: absolute;
  top: 160px;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(0, 0, 0, 0.3);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s ease, visibility 0.3s ease;
  z-index: 10;
}

.avatar-container:hover + .avatar-tooltip {
  opacity: 1;
  visibility: visible;
}

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

.form-control:disabled {
  background-color: #f5f5f5;
  color: #666;
  cursor: not-allowed;
}

.help-text {
  font-size: 12px;
  color: #6c757d;
  margin-top: 5px;
}

.error-text {
  font-size: 12px;
  color: #e74c3c;
  margin-top: 5px;
}



/* 模态框尺寸调整 */
.modal-content {
  max-width: 500px;
}

/* 响应式调整 */
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

  .modal-content {
    width: 95%;
    margin: 20px;
  }
}
</style>