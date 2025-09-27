<template>
  <div class="login-page">
    <div class="background-blur"></div>
    <div class="login-container">
      <div class="lang-switch">
        <button class="lang-btn" :class="{ active: currentLang === 'en' }" @click="switchLang('en')">English</button>
        <button class="lang-btn" :class="{ active: currentLang === 'zh' }" @click="switchLang('zh')">中文</button>
      </div>

      <div class="login-box">
        <div class="logo-area">
          <img src="/images/logo.png" alt="厦门大学校徽" class="xmu-logo">
          <div class="logo-text">
            <span class="auth-title">统一身份认证</span>
            <span class="system-name">推免加分系统</span>
          </div>
        </div>

        <div class="login-tabs">
          <button class="tab-btn active">账号登录</button>
        </div>

        <div class="form-container">
          <form class="login-form" @submit.prevent="handleLogin">
            <div class="input-group">
              <i class="fas fa-user input-icon"></i>
              <input type="text" v-model="form.username" placeholder="请输入学号/工号" required>
            </div>
            <div class="input-group">
              <i class="fas fa-lock input-icon"></i>
              <input type="password" v-model="form.password" placeholder="请输入密码" required>
            </div>

            <div class="form-actions">
              <a href="#" class="forgot-password">忘记密码?</a>
              <button type="submit" class="login-btn" :class="{ loading: isLoading }">
                <span class="btn-text">登录</span>
                <div class="btn-loading">
                  <i class="fas fa-spinner fa-spin"></i>
                </div>
              </button>
            </div>
          </form>
        </div>

        <div class="help-area">
          <p class="help-text">首次登录请点击"忘记密码"进行设置</p>
          <p class="help-text">学生校友账号禁用可通过"忘记密码"进行重置</p>
        </div>
      </div>
      <div class="copyright">© 2025 厦门大学软件工程系</div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const currentLang = ref('zh')
    const isLoading = ref(false)
    const form = ref({
      username: '',
      password: ''
    })

    const switchLang = (lang) => {
      currentLang.value = lang
    }

    const handleLogin = async () => {
      isLoading.value = true
      
      // 模拟登录过程
      setTimeout(() => {
        isLoading.value = false
        
        // 根据用户名判断角色并跳转
        if (form.value.username.includes('admin')) {
          router.push('/admin')
        } else if (form.value.username.includes('teacher')) {
          router.push('/teacher')
        } else {
          router.push('/student')
        }
      }, 1500)
    }

    return {
      currentLang,
      isLoading,
      form,
      switchLang,
      handleLogin
    }
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Microsoft Yahei", "PingFang SC", "Helvetica Neue", sans-serif;
  background-color: #f5f7fa;
  color: #333;
  line-height: 1.6;
  height: 100vh;
  overflow: hidden;
}

.container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 顶部导航栏样式 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #003d86, #0066cc);
  color: #fff;
  padding: 10px 20px;
  height: 60px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.logo-area {
  display: flex;
  align-items: center;
}

.logo {
  width: 150px;
  margin-right: 10px;
  border-radius: 4px;
}

.university-name {
  font-size: 20px;
  font-weight: bold;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.notification {
  font-size: 18px;
  cursor: pointer;
  position: relative;
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: #e74c3c;
  color: white;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  font-size: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-menu {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  margin-right: 8px;
  object-fit: cover;
}

.logout-btn {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 16px;
  margin-left: 15px;
}

.content-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 左侧边栏样式 */
.sidebar {
  width: 240px;
  background-color: #ffffff;
  border-right: 1px solid #e1e4e8;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.05);
}

.user-info {
  display: flex;
  align-items: center;
  padding: 0 20px 20px;
  border-bottom: 1px solid #e1e4e8;
  margin-bottom: 20px;
}

.user-info .user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  margin-right: 12px;
  object-fit: cover;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-name {
  font-weight: bold;
  font-size: 16px;
  color: #333;
}

.user-faculty,
.user-major,
.user-role {
  font-size: 13px;
  color: #666;
  line-height: 1.3;
}

.sidebar-nav ul {
  list-style: none;
}

.sidebar-nav li {
  margin-bottom: 4px;
}

.sidebar-nav li a {
  text-decoration: none;
  color: #333;
  display: flex;
  align-items: center;
  padding: 12px 20px;
  border-radius: 0 4px 4px 0;
  transition: all 0.3s;
  font-size: 15px;
}

.sidebar-nav li a i {
  margin-right: 10px;
  width: 20px;
  text-align: center;
}

.sidebar-nav li a:hover {
  background-color: #f0f2f5;
}

.sidebar-nav li.active a {
  background-color: #0057b1;
  color: #ffffff;
  font-weight: 500;
}

/* 主内容区样式 */
.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f5f7fa;
}

/* 页面内容容器 */
.page-content {
  display: block;
}

.page-content.hidden {
  display: none;
}

.page-title {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin-bottom: 20px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #003366;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

/* 表单行布局 */
.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.form-row .form-group {
  flex: 1;
}

/* 单选按钮组 */
.radio-group {
  display: flex;
  gap: 20px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

/* 申请记录表格样式 */
.table-container {
  overflow-x: auto;
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

.status-draft {
  background-color: #fef5e7;
  color: #e67e22;
}

.status-pending {
  background-color: #ebf5fb;
  color: #3498db;
}

.status-approved {
  background-color: #eafaf1;
  color: #27ae60;
}

.status-rejected {
  background-color: #fdedec;
  color: #e74c3c;
}

/* 筛选和排序控件 */
.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #666;
}

select,
.btn {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  font-size: 14px;
}

.btn {
  cursor: pointer;
  background-color: #003366;
  color: white;
  border: none;
  transition: background-color 0.3s;
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

/* 表单样式 */
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

/* 表单操作按钮 */
.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

textarea.form-control {
  min-height: 100px;
  resize: vertical;
}

.file-upload {
  border: 2px dashed #ddd;
  padding: 20px;
  text-align: center;
  border-radius: 4px;
  margin-bottom: 15px;
  cursor: pointer;
  transition: border-color 0.3s;
}

.file-upload:hover {
  border-color: #003366;
}

.file-upload i {
  font-size: 24px;
  color: #003366;
  margin-bottom: 10px;
}

.file-list {
  margin-top: 15px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 8px;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-actions {
  display: flex;
  gap: 10px;
}

.file-action {
  color: #666;
  cursor: pointer;
}

.file-action:hover {
  color: #003366;
}

/* 统计卡片 */
.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  text-align: center;
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
}

.stat-note {
  color: #888;
  font-size: 12px;
  margin-top: 5px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

/* 教师端特有样式 */
.small-input {
  max-width: 100px;
}

.btn-approve {
  background-color: #28a745;
}

.btn-approve:hover {
  background-color: #218838;
}

.btn-reject {
  background-color: #dc3545;
}

.btn-reject:hover {
  background-color: #c82333;
}

.help-text {
  font-size: 12px;
  color: #6c757d;
  margin-top: 5px;
}

.back-button {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-bottom: 15px;
}

.back-button:hover {
  background-color: #5a6268;
}

.back-button i {
  margin-right: 5px;
}

/* 文件预览样式 */
.file-preview {
  margin-top: 15px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f8f9fa;
}

.file-preview img {
  max-width: 100%;
  max-height: 300px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.file-info {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-download {
  color: #003366;
  text-decoration: none;
  display: flex;
  align-items: center;
}

.file-download i {
  margin-right: 5px;
}

/* 管理员端特有样式 */
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

.batch-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.small-btn {
  padding: 5px 8px;
  font-size: 12px;
}

.small-input {
  width: 80px;
  display: inline-block;
  margin-right: 5px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters {
    flex-direction: column;
    align-items: flex-start;
  }

  .filter-group {
    width: 100%;
  }
}
</style>