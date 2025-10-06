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
            <input type="text" class="form-control" v-model="profile.name" 
                   :disabled="!isEditing" required>
          </div>
          <div class="form-group">
            <label class="form-label">学号</label>
            <input type="text" class="form-control" v-model="profile.studentId" 
                   disabled>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">学院</label>
            <input type="text" class="form-control" v-model="profile.faculty" 
                   :disabled="!isEditing" required>
          </div>
          <div class="form-group">
            <label class="form-label">专业</label>
            <input type="text" class="form-control" v-model="profile.major" 
                   :disabled="!isEditing" required>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">CET4成绩</label>
            <input type="number" class="form-control" v-model="profile.cet4" 
                   :disabled="!isEditing" min="0" max="710">
          </div>
          <div class="form-group">
            <label class="form-label">CET6成绩</label>
            <input type="number" class="form-control" v-model="profile.cet6" 
                   :disabled="!isEditing" min="0" max="710">
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">推免绩点</label>
            <input type="number" class="form-control" v-model="profile.gpa" 
                   :disabled="!isEditing" step="0.01" min="0" max="4.0" required>
          </div>
          <div class="form-group">
            <label class="form-label">学业综合成绩</label>
            <input type="number" class="form-control" v-model="profile.academicScore" 
                   :disabled="!isEditing" step="0.1" min="0" max="100" required>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">电子邮箱</label>
            <input type="email" class="form-control" v-model="profile.email" 
                   :disabled="!isEditing" required>
          </div>
          <div class="form-group">
            <label class="form-label">手机号码</label>
            <input type="tel" class="form-control" v-model="profile.phone" 
                   :disabled="!isEditing" required>
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
              <input type="password" class="form-control" v-model="passwordForm.currentPassword" 
                     required>
            </div>
            <div class="form-group">
              <label class="form-label">新密码</label>
              <input type="password" class="form-control" v-model="passwordForm.newPassword" 
                     required minlength="6">
              <div class="help-text">密码长度至少6位</div>
            </div>
            <div class="form-group">
              <label class="form-label">确认新密码</label>
              <input type="password" class="form-control" v-model="passwordForm.confirmPassword" 
                     required>
              <div v-if="passwordForm.newPassword !== passwordForm.confirmPassword" 
                   class="error-text">两次输入的密码不一致</div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="closePasswordModal">取消</button>
          <button class="btn" @click="changePassword" 
                  :disabled="passwordForm.newPassword !== passwordForm.confirmPassword">
            确认修改
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const isEditing = ref(false)
const saving = ref(false)
const showChangePassword = ref(false)

const originalProfile = ref({})
const profile = reactive({
  name: '张同学',
  studentId: '12320253211234',
  faculty: '信息学院',
  major: '计算机科学与技术',
  cet4: 580,
  cet6: 520,
  gpa: 3.85,
  academicScore: 92.5,
  email: 'zhang@xmu.edu.cn',
  phone: '13800138000'
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
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 保存到本地存储
    localStorage.setItem('studentProfile', JSON.stringify(profile))
    
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

// 生命周期
onMounted(() => {
  // 从本地存储加载个人信息
  const savedProfile = localStorage.getItem('studentProfile')
  if (savedProfile) {
    Object.assign(profile, JSON.parse(savedProfile))
  }
  originalProfile.value = { ...profile }
})
</script>

<style scoped>
/* 引入共享样式 */
@import '../common/shared-styles.css';

/* 组件特有样式 */
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
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
}
</style>