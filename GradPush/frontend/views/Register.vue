<template>
  <div class="register-page">
    <div class="background-blur"></div>
    <div class="register-container">
      <div class="register-box">
        <div class="logo-area">
          <img src="/images/logo.png" alt="厦门大学校徽" class="xmu-logo">
          <div class="logo-text">
            <span class="auth-title">统一身份认证</span>
            <span class="system-name">推免加分系统</span>
          </div>
        </div>

        <div class="register-tabs">
          <button class="tab-btn active">账号注册</button>
        </div>

        <div class="form-container">
          <form class="register-form" @submit.prevent="handleRegister">
            <div class="input-group">
              <font-awesome-icon :icon="['fas', 'user']" class="input-icon" />
              <input type="text" v-model="registerForm.username" placeholder="请输入学号/工号" required>
            </div>
            
            <div class="input-group">
              <font-awesome-icon :icon="['fas', 'user-tag']" class="input-icon" />
              <input type="text" v-model="registerForm.name" placeholder="请输入姓名" required>
            </div>
            
            <div class="input-group">
              <font-awesome-icon :icon="['fas', 'user-shield']" class="input-icon" />
              <select v-model="registerForm.role" required @change="handleRoleChange">
                <option value="">请选择角色</option>
                <option value="student">学生</option>
                <option value="teacher">教师</option>
              </select>
            </div>
            
            <!-- 学院选择 -->
            <div class="input-group">
              <font-awesome-icon :icon="['fas', 'university']" class="input-icon" />
              <select v-model="registerForm.faculty" required @change="handleFacultyChange">
                <option value="">请选择学院</option>
                <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.name">
                  {{ faculty.name }}
                </option>
              </select>
            </div>
            
            <!-- 系选择（仅学生显示） -->
            <div class="input-group" v-if="registerForm.role === 'student'">
              <font-awesome-icon :icon="['fas', 'building']" class="input-icon" />
              <select v-model="registerForm.department" required @change="handleDepartmentChange">
                <option value="">请选择系</option>
                <option v-for="department in departments" :key="department.id" :value="department.name">
                  {{ department.name }}
                </option>
              </select>
            </div>
            
            <!-- 专业选择（仅学生显示） -->
            <div class="input-group" v-if="registerForm.role === 'student'">
              <font-awesome-icon :icon="['fas', 'graduation-cap']" class="input-icon" />
              <select v-model="registerForm.major" required>
                <option value="">请选择专业</option>
                <option v-for="major in majors" :key="major.id" :value="major.name">
                  {{ major.name }}
                </option>
              </select>
            </div>
            
            <div class="input-group">
              <font-awesome-icon :icon="['fas', 'lock']" class="input-icon" />
              <input type="password" v-model="registerForm.password" placeholder="请设置密码" required minlength="6">
            </div>
            
            <div class="input-group">
              <font-awesome-icon :icon="['fas', 'lock']" class="input-icon" />
              <input type="password" v-model="registerForm.confirmPassword" placeholder="请确认密码" required minlength="6">
            </div>

            <div class="form-actions">
              <div class="links-container">
                <a href="#" class="login-link" @click.prevent="goToLogin">
                  已有账号？立即登录
                </a>
              </div>
              <button type="submit" class="register-btn" :class="{ loading }" :disabled="loading">
                <span class="btn-text">注册</span>
                <div class="btn-loading">
                  <font-awesome-icon :icon="['fas', 'spinner']" spin />
                </div>
              </button>
            </div>
          </form>
        </div>

        <div class="help-area">
          <p class="help-text">管理员账号请联系系统管理员开通</p>
          <p class="help-text">如有疑问，请联系系统技术支持</p>
        </div>
      </div>
      <div class="copyright">© 2025 厦门大学软件工程系</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../utils/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const loadingOptions = ref(false)

// 表单数据
const registerForm = reactive({
  username: '',
  name: '',
  password: '',
  confirmPassword: '',
  role: '',
  faculty: '',
  department: '',
  major: ''
})

// 下拉选项数据
const faculties = ref([])
const departments = ref([])
const majors = ref([])

// 表单验证
const isFormValid = computed(() => {
  const { username, name, password, confirmPassword, role, faculty, department, major } = registerForm
  
  // 基本字段验证
  if (!username || !name || !password || !confirmPassword || !role || !faculty) {
    return false
  }
  
  // 学生需要验证系和专业
  if (role === 'student' && (!department || !major)) {
    return false
  }
  
  // 密码一致性验证
  if (password !== confirmPassword) {
    return false
  }
  
  // 密码长度验证
  if (password.length < 6) {
    return false
  }
  
  return true
})

// 组件挂载时加载学院列表
onMounted(() => {
  loadFaculties()
})

// 加载学院列表
const loadFaculties = async () => {
  try {
    loadingOptions.value = true
    const response = await api.getFaculties()
    faculties.value = response.faculties
  } catch (error) {
    console.error('加载学院列表失败:', error)
    alert('加载学院列表失败，请刷新页面重试')
  } finally {
    loadingOptions.value = false
  }
}

// 加载系列表
const loadDepartments = async (facultyName) => {
  try {
    loadingOptions.value = true
    // 找到选中的学院ID
    const selectedFaculty = faculties.value.find(f => f.name === facultyName)
    if (selectedFaculty) {
      const response = await api.getDepartmentsByFaculty(selectedFaculty.id)
      departments.value = response.departments
      // 重置系和专业选择
      registerForm.department = ''
      registerForm.major = ''
      majors.value = []
    }
  } catch (error) {
    console.error('加载系列表失败:', error)
    alert('加载系列表失败，请重试')
  } finally {
    loadingOptions.value = false
  }
}

// 加载专业列表
const loadMajors = async (departmentName) => {
  try {
    loadingOptions.value = true
    // 找到选中的系ID
    const selectedDepartment = departments.value.find(d => d.name === departmentName)
    if (selectedDepartment) {
      const response = await api.getMajorsByDepartment(selectedDepartment.id)
      majors.value = response.majors
      // 重置专业选择
      registerForm.major = ''
    }
  } catch (error) {
    console.error('加载专业列表失败:', error)
    alert('加载专业列表失败，请重试')
  } finally {
    loadingOptions.value = false
  }
}

// 角色变化处理
const handleRoleChange = () => {
  // 重置学院、系和专业选择
  registerForm.faculty = ''
  registerForm.department = ''
  registerForm.major = ''
  departments.value = []
  majors.value = []
}

// 学院变化处理
const handleFacultyChange = () => {
  if (registerForm.faculty) {
    loadDepartments(registerForm.faculty)
  } else {
    // 重置系和专业选择
    registerForm.department = ''
    registerForm.major = ''
    departments.value = []
    majors.value = []
  }
}

// 系变化处理
const handleDepartmentChange = () => {
  if (registerForm.department) {
    loadMajors(registerForm.department)
  } else {
    // 重置专业选择
    registerForm.major = ''
    majors.value = []
  }
}

const handleRegister = async () => {
  // 检测输入框是否为空
  if (!registerForm.username.trim()) {
    alert('请输入学号/工号')
    return
  }
  if (!registerForm.name.trim()) {
    alert('请输入姓名')
    return
  }
  if (!registerForm.password) {
    alert('请设置密码')
    return
  }
  if (!registerForm.confirmPassword) {
    alert('请确认密码')
    return
  }
  if (!registerForm.role) {
    alert('请选择角色')
    return
  }
  if (!registerForm.faculty) {
    alert('请选择学院')
    return
  }
  if (registerForm.role === 'student' && !registerForm.department) {
    alert('请选择系')
    return
  }
  if (registerForm.role === 'student' && !registerForm.major) {
    alert('请选择专业')
    return
  }
  
  // 密码一致性和长度验证
  if (registerForm.password !== registerForm.confirmPassword) {
    alert('两次输入的密码不一致')
    return
  }
  if (registerForm.password.length < 6) {
    alert('密码长度不能少于6位')
    return
  }
  
  loading.value = true

  try {
    // 使用auth store的注册方法
    await authStore.register({
      username: registerForm.username,
      name: registerForm.name,
      password: registerForm.password,
      role: registerForm.role,
      faculty: registerForm.faculty,
      department: registerForm.department,
      major: registerForm.major
    })
    
    // 注册成功后跳转到登录页面
    alert('注册成功！请使用您的账号密码登录')
    router.push('/login')
  } catch (error) {
    console.error('注册错误:', error)
    alert(`注册失败: ${error.message || '请稍后重试'}`)
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
/* 注册页面整体容器样式 */
.register-page {
  font-family: "Microsoft Yahei", "PingFang SC", "Helvetica Neue", sans-serif;
  line-height: 1.6;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

/* 背景模糊效果样式 */
.background-blur {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('/images/loginBackground.jpg') no-repeat center center;
  background-size: cover;
  filter: blur(8px) brightness(0.80);
  transform: scale(1.05);
  z-index: 0;
}

/* 注册表单容器样式 */
.register-container {
  width: 100%;
  max-width: 480px;
  padding: 20px;
  position: relative;
  z-index: 1;
}

/* 注册框主体样式 */
.register-box {
  background: rgba(255, 255, 255, 0.95);
  padding: 40px 35px;
  border-radius: 16px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  transform: translateZ(0);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.3);
  max-height: 80vh;
  overflow-y: auto;
  width: 100%;
  max-width: 480px;
  /* 隐藏滚动条 */
  scrollbar-width: none; /* Firefox */
}

/* WebKit浏览器隐藏滚动条 */
.register-box::-webkit-scrollbar {
  display: none;
}

/* 徽标区域样式 */
.logo-area {
  display: flex;
  align-items: center;
  padding-bottom: 25px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  margin-bottom: 25px;
}

/* 厦门大学校徽样式 */
.xmu-logo {
  width: 230px;
  margin-right: 15px;
  object-fit: contain;
}

/* 徽标文字区域样式 */
.logo-text {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* 认证标题文字样式 */
.logo-text .auth-title {
  font-size: 20px;
  font-weight: bold;
  color: #003d86;
  margin-bottom: 5px;
}

/* 系统名称文字样式 */
.logo-text .system-name {
  font-size: 16px;
  color: #666;
  font-weight: 500;
}

/* 注册标签页样式 */
.register-tabs {
  width: 80%;
  margin: 0 auto 25px;
  text-align: center;
  border-bottom: 2px solid #003d86;
  padding-bottom: 10px;
}

/* 标签按钮样式 */
.tab-btn {
  background: none;
  border: none;
  color: #003d86;
  font-size: 18px;
  font-weight: bold;
  cursor: default;
  padding: 0;
}

/* 表单容器样式 */
.form-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

/* 注册表单样式 */
.register-form {
  width: 80%;
}

/* 输入组样式 */
.input-group {
  margin-bottom: 18px;
  position: relative;
}

/* 输入图标样式 */
.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
  font-size: 18px;
  transition: color 0.3s ease;
}

/* 输入框样式 */
.input-group input,
.input-group select {
  width: 100%;
  height: 50px;
  padding: 10px 20px 10px 45px;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
  font-size: 16px;
  transition: all 0.3s ease;
  background: #f9fafb;
  box-sizing: border-box;
}

/* 输入框聚焦状态样式 */
.input-group input:focus,
.input-group select:focus {
  border-color: #003d86;
  box-shadow: 0 0 0 1px rgba(0, 61, 134, 0.3);
  background: #fff;
}

/* 输入框聚焦时图标颜色变化 */
.input-group input:focus+.input-icon,
.input-group select:focus+.input-icon {
  color: #003d86;
}

/* 表单操作区域样式 */
.form-actions {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

/* 链接容器样式 */
.links-container {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 5px;
  gap: 5px;
}

/* 登录链接样式 */
.login-link {
  color: #0066cc;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s ease;
  font-weight: 500;
  padding: 0;
}

/* 登录链接悬停效果 */
.login-link:hover {
  color: #0041a8;
  text-decoration: underline;
}

/* 注册按钮样式 */
.register-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #003d86, #0066cc);
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 61, 134, 0.3);
}

/* 注册按钮悬停效果 */
.register-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #002a5c, #0052a3);
  box-shadow: 0 6px 20px rgba(0, 61, 134, 0.4);
  transform: translateY(-1px);
}

/* 注册按钮点击效果 */
.register-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 4px 15px rgba(0, 61, 134, 0.3);
}

/* 注册按钮禁用状态样式 */
.register-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

/* 按钮文字和加载动画的过渡效果 */
.btn-text,
.btn-loading {
  transition: opacity 0.3s ease;
}

/* 加载动画样式 */
.btn-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
}

/* 加载状态下隐藏按钮文字 */
.register-btn.loading .btn-text {
  opacity: 0;
}

/* 加载状态下显示加载动画 */
.register-btn.loading .btn-loading {
  opacity: 1;
}

/* 帮助信息区域样式 */
.help-area {
  margin: 20px auto 0;
  width: 80%;
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  text-align: center;
  padding: 15px;
  background: #f0f4f9;
  border-radius: 8px;
}

/* 帮助文字样式 */
.help-text {
  margin-bottom: 5px;
}

/* 最后一个帮助文字去掉底部边距 */
.help-text:last-child {
  margin-bottom: 0;
}

/* 版权信息样式 */
.copyright {
  text-align: center;
  margin-top: 25px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* 响应式设计 - 移动端适配 */
@media (max-width: 768px) {
  .register-container {
    max-width: 90%;
  }

  .register-box {
    padding: 30px 25px;
  }

  .logo-area {
    flex-direction: column;
    text-align: center;
  }

  .xmu-logo {
    width: 180px;
    margin-right: 0;
    margin-bottom: 15px;
  }

  .register-form {
    width: 90%;
  }

  .register-tabs {
    width: 85%;
  }

  .help-area {
    width: 85%;
  }
}
</style>