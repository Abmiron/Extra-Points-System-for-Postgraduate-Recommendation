<template>
  <div class="login-page">
     <!-- 简化背景效果 -->
    <div class="background-container">
      <div class="background-blur"></div>
      <div class="background-overlay"></div>
    </div>

    <div class="login-container">
      <!-- 左侧信息显示区域 - 风格统一 -->
      <div class="info-panel">
        <div class="info-content">
          <div class="info-card">
            <div class="info-header">
              <h3 class="info-title">推免申请开放时间</h3>
              <div class="info-icon">
                <font-awesome-icon :icon="['fas', 'calendar-check']" />
              </div>
            </div>
            <div class="info-item" style="display: flex; justify-content: space-between; min-height: 24px;">
              <template v-if="settingsLoading">
                <span class="info-value">开放: <span class="loading-spinner-small"></span></span>
                <span class="info-value">截止: <span class="loading-spinner-small"></span></span>
              </template>
              <template v-else>
                <span class="info-value">开放: {{ applicationTimeStart }}</span>
                <span class="info-value">截止: {{ applicationTimeEnd }}</span>
              </template>
            </div>
          </div>
          
          <div class="info-features">
            <div class="feature-item">
              <font-awesome-icon :icon="['fas', 'check']" class="feature-icon" />
              <span>在线提交申请材料</span>
            </div>
            <div class="feature-item">
              <font-awesome-icon :icon="['fas', 'check']" class="feature-icon" />
              <span>实时查看审核进度</span>
            </div>
            <div class="feature-item">
              <font-awesome-icon :icon="['fas', 'check']" class="feature-icon" />
              <span>自动计算分数排名</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧登录区域 -->
      <div class="login-box">
        <div class="logo-area">
          <img src="/images/logo.png" alt="厦门大学校徽" class="xmu-logo">
          <div class="logo-text">
            <span class="auth-title">统一身份认证</span>
            <span class="system-name">推免加分系统</span>
          </div>
        </div>

        <div class="login-tabs">
          <button class="tab-btn active">
            {{ activeTab === 'login' ? '账号登录' : activeTab === 'register' ? '账号注册' : '密码重置' }}
          </button>
        </div>

        <div class="form-container">
          <!-- 登录表单 -->
          <form v-if="activeTab === 'login'" class="login-form" @submit.prevent="handleLogin">

            <div class="input-group">
              <font-awesome-icon :icon="['fas', 'user']" class="input-icon" />
              <input type="text" v-model="loginForm.username" placeholder="请输入学号/工号" required>
            </div>
            <div class="input-group">
              <font-awesome-icon :icon="['fas', 'lock']" class="input-icon" />
              <input type="password" v-model="loginForm.password" placeholder="请输入密码" required>
            </div>
            <div class="input-group captcha-group">
              <font-awesome-icon :icon="['fas', 'shield-alt']" class="input-icon" />
              <div style="display: flex; align-items: center; gap: 10px; width: 100%;">
                <input type="text" v-model="loginForm.captcha" placeholder="请输入验证码" required style="flex: 1; height: 50px;">
                <img 
                  :src="captchaImage" 
                  alt="验证码" 
                  style="max-height: 50px; height: auto; cursor: pointer; border-radius: 8px;" 
                  @click="refreshCaptcha"
                  title="点击刷新"
                >
              </div>
            </div>

            <div class="form-actions">
              <div class="links-container">
                <a href="#" class="tab-link" @click.prevent="switchTab('forgot')">
                  忘记密码?
                </a>
                <a href="#" class="tab-link" @click.prevent="switchTab('register')">
                  注册账号
                </a>
              </div>
              <button type="submit" class="login-btn" :class="{ loading }" :disabled="loading">
                <span class="btn-text">登录</span>
                <div class="btn-loading">
                  <font-awesome-icon :icon="['fas', 'spinner']" spin />
                </div>
              </button>
            </div>
          </form>

          <!-- 注册表单 -->
          <form v-else-if="activeTab === 'register'" class="register-form" @submit.prevent="handleRegister">
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
              <select v-model="registerForm.facultyId" required @change="handleFacultyChange">
                <option value="">请选择学院</option>
                <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.id">
                  {{ faculty.name }}
                </option>
              </select>
            </div>

            <!-- 系选择（仅学生显示） -->
            <div class="input-group" v-if="registerForm.role === 'student'">
              <font-awesome-icon :icon="['fas', 'building']" class="input-icon" />
              <select v-model="registerForm.departmentId" required @change="handleDepartmentChange">
                <option value="">请选择系</option>
                <option v-for="department in departments" :key="department.id" :value="department.id">
                  {{ department.name }}
                </option>
              </select>
            </div>

            <!-- 专业选择（仅学生显示） -->
            <div class="input-group" v-if="registerForm.role === 'student'">
              <font-awesome-icon :icon="['fas', 'graduation-cap']" class="input-icon" />
              <select v-model="registerForm.majorId" required>
                <option value="">请选择专业</option>
                <option v-for="major in majors" :key="major.id" :value="major.id">
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
                <a href="#" class="tab-link" @click.prevent="switchTab('login')">
                  已有账号？立即登录
                </a>
              </div>
              <button type="submit" class="login-btn" :class="{ loading }" :disabled="loading">
                <span class="btn-text">注册</span>
                <div class="btn-loading">
                  <font-awesome-icon :icon="['fas', 'spinner']" spin />
                </div>
              </button>
            </div>
          </form>

          <!-- 忘记密码表单 -->
          <form v-else-if="activeTab === 'forgot'" class="login-form" @submit.prevent="handleResetPassword">
            <div class="input-group">
              <font-awesome-icon :icon="['fas', 'user']" class="input-icon" />
              <input type="text" v-model="resetForm.username" placeholder="请输入学号/工号" required>
            </div>

            <div class="input-group">
              <font-awesome-icon :icon="['fas', 'lock']" class="input-icon" />
              <input type="password" v-model="resetForm.newPassword" placeholder="请设置新密码" required minlength="6">
            </div>

            <div class="input-group">
              <font-awesome-icon :icon="['fas', 'lock']" class="input-icon" />
              <input type="password" v-model="resetForm.confirmPassword" placeholder="请确认新密码" required minlength="6">
            </div>

            <div class="form-actions">
              <div class="links-container">
                <a href="#" class="tab-link" @click.prevent="switchTab('login')">
                  返回登录
                </a>
              </div>
              <button type="submit" class="login-btn" :class="{ loading }" :disabled="loading">
                <span class="btn-text">重置</span>
                <div class="btn-loading">
                  <font-awesome-icon :icon="['fas', 'spinner']" spin />
                </div>
              </button>
            </div>
          </form>
        </div>

        <div class="help-area">
          <template v-if="activeTab === 'login'">
            <p class="help-text">首次登录请点击"注册账号"进行设置</p>
            <p class="help-text">学生校友账号禁用可通过"忘记密码"进行重置</p>
          </template>
          <template v-else-if="activeTab === 'register'">
            <p class="help-text">管理员账号请联系系统管理员开通</p>
            <p class="help-text">如有疑问，请联系系统技术支持</p>
          </template>
          <template v-else-if="activeTab === 'forgot'">
            <p class="help-text">首次登录用户请输入学号/工号并设置密码</p>
            <p class="help-text">请妥善保管您的密码信息</p>
          </template>
        </div>
      </div>
    </div>
    <div class="copyright">© 2025 厦门大学软件工程系</div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import api from '../utils/api'

// 添加小型加载动画样式
const style = document.createElement('style')
style.textContent = `
.loading-spinner-small {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #3498db;
  border-radius: 50%;
  animation: spin-small 1s linear infinite;
  vertical-align: middle;
  margin-left: 5px;
}

@keyframes spin-small {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
`
document.head.appendChild(style)

const router = useRouter()
const authStore = useAuthStore()
const toastStore = useToastStore()

// 组件挂载时自动获取验证码
onMounted(() => {
  refreshCaptcha()
})

// 标签页状态管理
const activeTab = ref('login') // 'login', 'register', 'forgot'
const loading = ref(false)
const loadingOptions = ref(false)

// 标签页切换函数
const switchTab = (tab) => {
  activeTab.value = tab
}

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: '',
  captcha: ''
})

// 验证码相关
const captchaImage = ref('')
const captchaToken = ref('')

// 获取验证码
const refreshCaptcha = async () => {
  try {
    // 使用项目已有的api模块获取验证码
    const response = await api.generateCaptcha()
    // 将base64字符串转换为可显示的图片
    captchaImage.value = `data:image/png;base64,${response.image}`
    // 保存验证码token
    captchaToken.value = response.token
  } catch (error) {
    console.error('获取验证码失败:', error)
    toastStore.error('获取验证码失败，请刷新页面重试')
  }
}

// 注册表单数据
const registerForm = reactive({
  username: '',
  name: '',
  password: '',
  confirmPassword: '',
  role: '',
  facultyId: '',
  departmentId: '',
  majorId: ''
})

// 忘记密码表单数据
const resetForm = reactive({
  username: '',
  newPassword: '',
  confirmPassword: ''
})

// 下拉选项数据（注册用）
const faculties = ref([])
const departments = ref([])
const majors = ref([])

// 申请时间相关数据
const applicationTimeStart = ref('2025年9月1日 00:00')
const applicationTimeEnd = ref('2025年9月30日 23:59')
const settingsLoading = ref(false)

// 注册表单验证
const isRegisterFormValid = computed(() => {
  const { username, name, password, confirmPassword, role, facultyId, departmentId, majorId } = registerForm

  // 基本字段验证
  if (!username || !name || !password || !confirmPassword || !role || !facultyId) {
    return false
  }

  // 学生需要验证系和专业
  if (role === 'student' && (!departmentId || !majorId)) {
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

// 组件挂载时加载数据
onMounted(async () => {
  await Promise.all([
    loadFaculties(),
    loadPublicSystemInfo()
  ])
  // 加载验证码
  refreshCaptcha()
})

// 加载公开系统信息，获取申请时间
const loadPublicSystemInfo = async () => {
  try {
    settingsLoading.value = true
    const response = await api.getPublicSystemInfo()
    
    // 格式化申请时间 - 数据在response.data对象中
    if (response.data && response.data.applicationStartTime) {
      applicationTimeStart.value = formatDate(response.data.applicationStartTime)
    }
    if (response.data && response.data.applicationEndTime) {
      applicationTimeEnd.value = formatDate(response.data.applicationEndTime)
    }
  } catch (error) {
    console.error('加载公开系统信息失败:', error)
    console.log('使用默认时间:', applicationTimeStart.value, applicationTimeEnd.value)
  } finally {
    settingsLoading.value = false
  }
}

// 格式化日期时间（参考SystemSettings.vue的方式，正确处理UTC+8时区）
const formatDate = (dateString) => {
  try {
    if (typeof dateString === 'string') {
      // 检查是否是纯日期格式 YYYY-MM-DD
      const dateOnlyRegex = /^(\d{4})-(\d{2})-(\d{2})$/;
      if (dateOnlyRegex.test(dateString)) {
        const dateMatch = dateString.match(dateOnlyRegex);
        const year = dateMatch[1];
        const month = dateMatch[2];
        const day = dateMatch[3];
        
        const result = `${year}年${month}月${day}日`;
        return result;
      }
      
      // 对于带时间的格式，参考SystemSettings.vue中的处理方式
      // 首先确保日期字符串包含有效的时间信息
      let processedDateString = dateString;
      
      // 如果没有时区信息，添加UTC+8时区标记
      if (!dateString.includes('+') && !dateString.includes('Z')) {
        // 如果是空格分隔的格式，转换为T分隔的ISO格式
        if (dateString.includes(' ')) {
          processedDateString = dateString.replace(' ', 'T');
        }
        // 添加UTC+8时区标记
        processedDateString = processedDateString + '+08:00';
      }
      
      // 创建Date对象处理时间，确保正确解析带时区的时间
      const date = new Date(processedDateString);
      
      // 检查是否为有效日期
      if (isNaN(date.getTime())) {
        console.warn('无效的日期格式:', dateString);
        return dateString;
      }
      
      // 格式化显示为本地时间（UTC+8）
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      
      const result = `${year}年${month}月${day}日 ${hours}:${minutes}`;
      return result;
    }
    
    console.error('无法解析的日期:', dateString);
    return String(dateString);
  } catch (error) {
    console.error('日期格式化错误:', error);
    return String(dateString);
  }
}

// 加载学院列表（注册用）
const loadFaculties = async () => {
  try {
    loadingOptions.value = true
    const response = await api.getFaculties()
    faculties.value = response.faculties
  } catch (error) {
    console.error('加载学院列表失败:', error)
    toastStore.error('加载学院列表失败，请刷新页面重试')
  } finally {
    loadingOptions.value = false
  }
}

// 加载系列表（注册用）
const loadDepartments = async (facultyId) => {
  try {
    loadingOptions.value = true
    if (facultyId) {
      const response = await api.getDepartmentsByFaculty(facultyId)
      departments.value = response.departments
      // 重置系和专业选择
      registerForm.departmentId = ''
      registerForm.majorId = ''
      majors.value = []
    }
  } catch (error) {
    console.error('加载系列表失败:', error)
    toastStore.error('加载系列表失败，请重试')
  } finally {
    loadingOptions.value = false
  }
}

// 加载专业列表（注册用）
const loadMajors = async (departmentId) => {
  try {
    loadingOptions.value = true
    if (departmentId) {
      const response = await api.getMajorsByDepartment(departmentId)
      majors.value = response.majors
      // 重置专业选择
      registerForm.majorId = ''
    }
  } catch (error) {
    console.error('加载专业列表失败:', error)
    toastStore.error('加载专业列表失败，请重试')
  } finally {
    loadingOptions.value = false
  }
}

// 角色变化处理（注册用）
const handleRoleChange = () => {
  // 重置学院、系和专业选择
  registerForm.facultyId = ''
  registerForm.departmentId = ''
  registerForm.majorId = ''
  departments.value = []
  majors.value = []
}

// 学院变化处理（注册用）
const handleFacultyChange = () => {
  if (registerForm.facultyId) {
    loadDepartments(registerForm.facultyId)
  } else {
    // 重置系和专业选择
    registerForm.departmentId = ''
    registerForm.majorId = ''
    departments.value = []
    majors.value = []
  }
}

// 系变化处理（注册用）
const handleDepartmentChange = () => {
  if (registerForm.departmentId) {
    loadMajors(registerForm.departmentId)
  } else {
    // 重置专业选择
    registerForm.majorId = ''
    majors.value = []
  }
}

// 登录处理
const handleLogin = async () => {
  // 验证验证码是否输入
  if (!loginForm.captcha.trim()) {
    toastStore.error('请输入验证码')
    return
  }
  
  // 验证验证码token是否存在
  if (!captchaToken.value) {
    toastStore.error('验证码已失效，请刷新页面重新获取验证码')
    return
  }
  
  loading.value = true

  try {
    // 使用auth store的登录方法，包含验证码和验证码token
    await authStore.login(loginForm.username, loginForm.password, loginForm.captcha, captchaToken.value)
    
    // 学生角色登录时间验证
    if (authStore.role === 'student') {
      const now = new Date()
      
      // 尝试重新获取最新的系统信息，确保时间准确
      try {
        const systemInfoResponse = await api.getPublicSystemInfo()
        const startTimeStr = systemInfoResponse.data?.applicationStartTime
        const endTimeStr = systemInfoResponse.data?.applicationEndTime
        
        // 直接使用API返回的原始时间字符串，确保包含时区信息
        if (!startTimeStr || !endTimeStr) {
          throw new Error('系统时间配置不完整')
        }
        
        // 确保时间字符串包含时区信息
        const processTimeString = (timeStr) => {
          if (typeof timeStr === 'string') {
            if (!timeStr.includes('+') && !timeStr.includes('Z')) {
              // 如果没有时区信息，添加UTC+8时区标记
              return timeStr.replace(' ', 'T') + '+08:00'
            }
            return timeStr
          }
          return timeStr
        }
        
        const processedStartTime = processTimeString(startTimeStr)
        const processedEndTime = processTimeString(endTimeStr)
        
        const startTime = new Date(processedStartTime)
        const endTime = new Date(processedEndTime)

        // 检查是否为有效日期
        if (isNaN(startTime.getTime()) || isNaN(endTime.getTime())) {
          throw new Error('系统时间格式错误')
        }
        
        // 检查当前时间是否在申请时间范围内
        if (now < startTime) {
          // 退出登录并提示错误
          await authStore.logout()
          toastStore.error(`申请未开始，开始时间：${formatDate(startTimeStr)}`)
          return
        } else if (now > endTime) {
          await authStore.logout()
          toastStore.error(`申请已结束，结束时间：${formatDate(endTimeStr)}`)
          return
        }
      } catch (systemInfoError) {
        console.error('时间验证失败:', systemInfoError)
        // 获取失败时使用更明确的错误处理
        await authStore.logout()
        toastStore.error(`系统时间验证失败，请联系管理员`)
        return
      }
    }

    // 登录成功，根据角色跳转
    const routeMap = {
      student: '/student',
      teacher: '/teacher',
      admin: '/admin'
    }

    router.push(routeMap[authStore.role])
  } catch (error) {
    console.error('登录错误:', error)
    toastStore.error(error.message || '登录失败，请稍后重试')
    // 登录失败后刷新验证码
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}

// 注册处理
const handleRegister = async () => {
  // 检测输入框是否为空
  if (!registerForm.username.trim()) {
    toastStore.error('请输入学号/工号')
    return
  }
  if (!registerForm.name.trim()) {
    toastStore.error('请输入姓名')
    return
  }
  if (!registerForm.password) {
    toastStore.error('请设置密码')
    return
  }
  if (!registerForm.confirmPassword) {
    toastStore.error('请确认密码')
    return
  }
  if (!registerForm.role) {
    toastStore.error('请选择角色')
    return
  }
  if (!registerForm.facultyId) {
    toastStore.error('请选择学院')
    return
  }
  if (registerForm.role === 'student' && !registerForm.departmentId) {
    toastStore.error('请选择系')
    return
  }
  if (registerForm.role === 'student' && !registerForm.majorId) {
    toastStore.error('请选择专业')
    return
  }

  // 密码一致性和长度验证
  if (registerForm.password !== registerForm.confirmPassword) {
    toastStore.error('两次输入的密码不一致')
    return
  }
  if (registerForm.password.length < 6) {
    toastStore.error('密码长度不能少于6位')
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
      facultyId: registerForm.facultyId,
      departmentId: registerForm.departmentId,
      majorId: registerForm.majorId
    })

    // 注册成功后跳转到登录标签页
    toastStore.success('注册成功！请使用您的账号密码登录')
    switchTab('login')
    // 清空注册表单
    Object.assign(registerForm, {
      username: '',
      name: '',
      password: '',
      confirmPassword: '',
      role: '',
      facultyId: '',
      departmentId: '',
      majorId: ''
    })
  } catch (error) {
    console.error('注册错误:', error)
    toastStore.error(`注册失败: ${error.message || '请稍后重试'}`)
  } finally {
    loading.value = false
  }
}

// 密码重置处理
const handleResetPassword = async () => {
  // 检测输入框是否为空
  if (!resetForm.username.trim()) {
    toastStore.error('请输入学号/工号')
    return
  }
  if (!resetForm.newPassword) {
    toastStore.error('请设置新密码')
    return
  }
  if (!resetForm.confirmPassword) {
    toastStore.error('请确认新密码')
    return
  }

  // 密码一致性和长度验证
  if (resetForm.newPassword !== resetForm.confirmPassword) {
    toastStore.error('两次输入的密码不一致')
    return
  }
  if (resetForm.newPassword.length < 6) {
    toastStore.error('密码长度不能少于6位')
    return
  }

  loading.value = true

  try {
    // 调用密码重置函数
    await authStore.resetPassword(resetForm.username, resetForm.newPassword)

    toastStore.success('密码重置成功！请使用新密码登录')
    switchTab('login')
    // 清空重置表单
    Object.assign(resetForm, {
      username: '',
      newPassword: '',
      confirmPassword: ''
    })
  } catch (error) {
    console.error('密码重置错误:', error)
    toastStore.error(`密码重置失败: ${error.message || '请稍后重试'}`)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 登录页面整体容器样式 - 保持原有风格 */
.login-page {
  font-family: "Microsoft Yahei", "PingFang SC", "Helvetica Neue", sans-serif;
  line-height: 1.6;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  padding-bottom: 40px;
}

/* 简化背景容器 */
.background-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

/* 背景模糊效果样式 - 与原有保持一致 */
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

/* 简化背景叠加层 */
.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 61, 134, 0.1);
  z-index: 1;
}

/* 登录表单容器样式 - 保持原有 */
.login-container {
  width: 100%;
  max-width: 1500px;
  display: flex;
  align-items: center;
  gap: 40px;
  padding: 20px;
  position: relative;
  z-index: 1;
  margin: auto;
}

/* 左侧信息显示面板样式 - 与登录框风格统一 */
.info-panel {
  padding: 30px 25px;
  flex: 1;
  width: 100%;
  max-width: 900px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.info-card {
  padding: 25px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.info-title {
  font-size: 20px;
  font-weight: 600;
  color: #003d86;
  margin: 0;
}

.info-icon {
  font-size: 20px;
  color: #003d86;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 61, 134, 0.1);
  border-radius: 8px;
}

.info-item {
  display: flex;
  flex-direction: row;
  gap: 8px;
}

.info-value {
  font-size: 28px;
  font-weight: 600;
  color: #1e293b;
}

.info-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  font-size: 14px;
  color: #475569;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: #cbd5e1;
}

.feature-icon {
  color: #10b981;
  font-size: 14px;
}

/* 登录框样式 - 完全保持不变 */
.login-box {
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
  margin-left: 0px;
  scrollbar-width: none;
}

.login-box::-webkit-scrollbar {
  display: none;
}

/* 所有登录框内部样式保持不变 */
.logo-area {
  display: flex;
  align-items: center;
  padding-bottom: 25px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  margin-bottom: 25px;
}

.xmu-logo {
  width: 230px;
  margin-right: 15px;
  object-fit: contain;
}

.logo-text {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.logo-text .auth-title {
  font-size: 20px;
  font-weight: bold;
  color: #003d86;
  margin-bottom: 5px;
}

.logo-text .system-name {
  font-size: 16px;
  color: #666;
  font-weight: 500;
}

.form-container {
  margin-bottom: 30px;
}

.form-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.login-form, .register-form {
  width: 80%;
}

.input-group {
  margin-bottom: 18px;
  position: relative;
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
  font-size: 18px;
  transition: color 0.3s ease;
}

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

.captcha-group .input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
}

.captcha-group > div {
  padding-left: 45px;
  width: 100%;
}

.input-group input:focus,
.input-group select:focus {
  border-color: #003d86;
  box-shadow: 0 0 0 1px rgba(0, 61, 134, 0.3);
  background: #fff;
}

.input-group input:focus+.input-icon,
.input-group select:focus+.input-icon {
  color: #003d86;
}

.form-actions {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

.links-container {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  gap: 5px;
}

.tab-link {
  color: #0066cc;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s ease;
  font-weight: 500;
  padding: 0;
}

.tab-link:hover {
  color: #0041a8;
  text-decoration: underline;
}

.login-btn {
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

.login-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #002a5c, #0052a3);
  box-shadow: 0 6px 20px rgba(0, 61, 134, 0.4);
  transform: translateY(-1px);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 4px 15px rgba(0, 61, 134, 0.3);
}

.login-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.btn-text,
.btn-loading {
  transition: opacity 0.3s ease;
}

.btn-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
}

.login-btn.loading .btn-text {
  opacity: 0;
}

.login-btn.loading .btn-loading {
  opacity: 1;
}

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

.help-text {
  margin-bottom: 5px;
}

.help-text:last-child {
  margin-bottom: 0;
}

.login-tabs {
  width: 90%;
  margin: 0 auto 25px;
  text-align: center;
  border-bottom: 2px solid #003d86;
  padding-bottom: 10px;
}

.tab-btn {
  background: none;
  border: none;
  color: #003d86;
  font-size: 18px;
  font-weight: bold;
  cursor: default;
  padding: 0;
}

.login-form, .register-form {
  width: 90%;
}

.help-area {
  width: 85%;
}

/* 版权信息样式 - 与原有保持一致 */
.copyright {
  text-align: center;
  margin-top: 30px;
  margin-bottom: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  position: absolute;
  bottom: 40px;
  left: 0;
  right: 0;
  z-index: 10;
}

/* 响应式设计 - 与原有保持一致 */
@media (max-width: 768px) {
  .login-container {
    max-width: 90%;
    flex-direction: column;
    gap: 20px;
  }
  
  .info-panel {
    max-width: 100%;
    padding: 25px 20px;
  }
  
  .info-content {
    flex-direction: column;
    gap: 20px;
  }
  
  .info-card {
    padding: 20px;
  }
  
  .info-header {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .info-title {
    font-size: 18px;
  }
  
  .info-value {
    font-size: 16px;
    text-align: center;
  }
  
  .info-features {
    grid-template-columns: 1fr;
  }
  
  .feature-item {
    justify-content: center;
  }

  .login-box {
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

  .login-tabs {
    width: 85%;
  }

  .login-form, .register-form {
    width: 90%;
  }

  .help-area {
    width: 85%;
  }
}
</style>