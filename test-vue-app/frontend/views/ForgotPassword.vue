<template>
  <div class="forgot-password-page">
    <div class="background-blur"></div>
    <div class="login-container">
      <div class="login-box">
        <div class="logo-area">
          <img src="/images/logo.png" alt="厦门大学校徽" class="xmu-logo">
          <div class="logo-text">
            <span class="auth-title">统一身份认证</span>
            <span class="system-name">推免加分系统</span>
          </div>
        </div>

        <div class="login-tabs">
          <button class="tab-btn active">密码重置</button>
        </div>

        <div class="form-container">
          <form class="login-form" @submit.prevent="handleResetPassword">
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
                <a href="#" class="login-link" @click.prevent="goToLogin">
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
          <p class="help-text">首次登录用户请输入学号/工号并设置密码</p>
          <p class="help-text">请妥善保管您的密码信息</p>
        </div>
      </div>
      <div class="copyright">© 2025 厦门大学软件工程系</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const resetForm = reactive({
  username: '',
  newPassword: '',
  confirmPassword: ''
})

const handleResetPassword = async () => {
  // 检测输入框是否为空
  if (!resetForm.username.trim()) {
    alert('请输入学号/工号')
    return
  }
  if (!resetForm.newPassword) {
    alert('请设置新密码')
    return
  }
  if (!resetForm.confirmPassword) {
    alert('请确认新密码')
    return
  }
  
  // 密码一致性和长度验证
  if (resetForm.newPassword !== resetForm.confirmPassword) {
    alert('两次输入的密码不一致')
    return
  }
  if (resetForm.newPassword.length < 6) {
    alert('密码长度不能少于6位')
    return
  }
  
  loading.value = true

  try {
    // 调用密码重置函数
    const message = await authStore.resetPassword(resetForm.username, resetForm.newPassword)
    
    alert('密码重置成功！请使用新密码登录')
    router.push('/login')
  } catch (error) {
    console.error('密码重置错误:', error)
    alert(`密码重置失败: ${error.message || '请稍后重试'}`)
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
/* 忘记密码页面整体容器样式 */
.forgot-password-page {
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
  background: url('../images/loginBackground.jpg') no-repeat center center;
  background-size: cover;
  filter: blur(8px) brightness(0.80);
  transform: scale(1.05);
  z-index: 0;
}

/* 登录表单容器样式 */
.login-container {
  width: 100%;
  max-width: 480px;
  padding: 20px;
  position: relative;
  z-index: 1;
  position: relative;
}

/* 登录框主体样式 */
.login-box {
  background: rgba(255, 255, 255, 0.95);
  padding: 40px 35px;
  border-radius: 16px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  transform: translateZ(0);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.3);
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

/* 登录标签页样式 */
.login-tabs {
  width: 80%;
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

/* 表单容器样式 */
.form-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

/* 登录表单样式 */
.login-form {
  width: 80%;
}

/* 输入框组样式 */
.input-group {
  margin-bottom: 20px;
  position: relative;
}

/* 输入框图标样式 */
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
.input-group input {
  width: 100%;
  height: 52px;
  padding: 10px 20px 10px 45px;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
  font-size: 16px;
  transition: all 0.3s ease;
  background: #f9fafb;
}

/* 输入框聚焦状态样式 */
.input-group input:focus {
  border-color: #003d86;
  box-shadow: 0 0 0 1px rgba(0, 61, 134, 0.3);
  background: #fff;
}

/* 输入框聚焦时图标颜色变化 */
.input-group input:focus+.input-icon {
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
  justify-content: flex-start;
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

/* 登录按钮样式 */
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

/* 登录按钮悬停效果 */
.login-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #002a5c, #0052a3);
  box-shadow: 0 6px 20px rgba(0, 61, 134, 0.4);
  transform: translateY(-1px);
}

/* 登录按钮点击效果 */
.login-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 4px 15px rgba(0, 61, 134, 0.3);
}

/* 登录按钮禁用状态样式 */
.login-btn:disabled {
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
.login-btn.loading .btn-text {
  opacity: 0;
}

/* 加载状态下显示加载动画 */
.login-btn.loading .btn-loading {
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
  .login-container {
    max-width: 90%;
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

  .login-form {
    width: 90%;
  }

  .login-tabs {
    width: 85%;
  }

  .help-area {
    width: 85%;
  }
}
</style>