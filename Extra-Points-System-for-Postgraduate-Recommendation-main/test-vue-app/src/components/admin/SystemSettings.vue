<template>
  <div class="page-content">
    <div class="page-title">
      <span>系统设置</span>
    </div>

    <!-- 学术年度设置 -->
    <div class="card">
      <div class="card-title">学术年度设置</div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">当前学术年度</label>
          <select class="form-control" v-model="settings.academicYear">
            <option value="2023">2023-2024学年</option>
            <option value="2022">2022-2023学年</option>
            <option value="2021">2021-2022学年</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">申请开始时间</label>
          <input type="date" class="form-control" v-model="settings.applicationStart">
        </div>
        <div class="form-group">
          <label class="form-label">申请截止时间</label>
          <input type="date" class="form-control" v-model="settings.applicationEnd">
        </div>
      </div>
      <div class="form-actions">
        <button class="btn" @click="saveAcademicSettings">保存设置</button>
      </div>
    </div>

    <!-- 系统公告管理 -->
    <div class="card">
      <div class="card-title">系统公告管理</div>
      <div class="form-group">
        <label class="form-label">公告标题</label>
        <input type="text" class="form-control" v-model="announcement.title" placeholder="请输入公告标题">
      </div>
      <div class="form-group">
        <label class="form-label">公告内容</label>
        <textarea class="form-control" v-model="announcement.content" rows="4" placeholder="请输入公告内容"></textarea>
      </div>
      <div class="form-group">
        <label class="form-label">发布对象</label>
        <div class="radio-group">
          <label class="radio-label">
            <input type="radio" v-model="announcement.audience" value="all">
            <span>全体用户</span>
          </label>
          <label class="radio-label">
            <input type="radio" v-model="announcement.audience" value="students">
            <span>仅学生</span>
          </label>
          <label class="radio-label">
            <input type="radio" v-model="announcement.audience" value="teachers">
            <span>仅教师</span>
          </label>
        </div>
      </div>
      <div class="form-actions">
        <button class="btn" @click="publishAnnouncement">发布公告</button>
      </div>
    </div>

    <!-- 文件存储设置 -->
    <div class="card">
      <div class="card-title">文件存储设置</div>
      <div class="form-group">
        <label class="form-label">文件大小限制</label>
        <input type="number" class="form-control small-input" v-model="settings.fileSizeLimit"> MB
        <div class="help-text">单个上传文件的最大大小</div>
      </div>
      <div class="form-group">
        <label class="form-label">允许的文件类型</label>
        <input type="text" class="form-control" v-model="settings.allowedFileTypes">
        <div class="help-text">多个扩展名用逗号分隔</div>
      </div>
      <div class="form-actions">
        <button class="btn" @click="saveStorageSettings">保存设置</button>
      </div>
    </div>

    <!-- 系统维护 -->
    <div class="card">
      <div class="card-title">系统维护</div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">数据库备份</label>
          <button class="btn btn-outline" @click="backupDatabase">
            <font-awesome-icon :icon="['fas', 'database']" /> 立即备份
          </button>
          <div class="help-text">上次备份: {{ settings.lastBackup || '从未备份' }}</div>
        </div>
        <div class="form-group">
          <label class="form-label">系统日志</label>
          <button class="btn btn-outline" @click="viewSystemLogs">
            <font-awesome-icon :icon="['fas', 'file-alt']" /> 查看日志
          </button>
          <div class="help-text">系统运行日志和错误记录</div>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">缓存清理</label>
          <button class="btn btn-outline" @click="clearCache">
            <font-awesome-icon :icon="['fas', 'broom']" /> 清理缓存
          </button>
          <div class="help-text">清理系统缓存数据</div>
        </div>
        <div class="form-group">
          <label class="form-label">系统状态</label>
          <div class="system-status">
            <span :class="`status-indicator ${systemStatus}`"></span>
            {{ systemStatus === 'online' ? '运行正常' : '系统维护中' }}
          </div>
          <button class="btn btn-outline" @click="toggleSystemStatus">
            {{ systemStatus === 'online' ? '进入维护模式' : '恢复正常运行' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const systemStatus = ref('online') // online, maintenance

const settings = reactive({
  academicYear: '2023',
  applicationStart: '2023-09-01',
  applicationEnd: '2023-10-15',
  fileSizeLimit: 10,
  allowedFileTypes: '.pdf, .jpg, .jpeg, .png',
  lastBackup: ''
})

const announcement = reactive({
  title: '',
  content: '',
  audience: 'all'
})

// 方法
const saveAcademicSettings = () => {
  // 保存学术年度设置
  localStorage.setItem('systemSettings', JSON.stringify(settings))
  alert('学术年度设置已保存')
}

const saveStorageSettings = () => {
  // 保存文件存储设置
  localStorage.setItem('systemSettings', JSON.stringify(settings))
  alert('文件存储设置已保存')
}

const publishAnnouncement = () => {
  if (!announcement.title || !announcement.content) {
    alert('请填写公告标题和内容')
    return
  }

  // 发布公告
  const announcements = JSON.parse(localStorage.getItem('systemAnnouncements') || '[]')
  const newAnnouncement = {
    id: Date.now(),
    ...announcement,
    publishTime: new Date().toISOString(),
    publisher: '系统管理员'
  }
  announcements.push(newAnnouncement)
  localStorage.setItem('systemAnnouncements', JSON.stringify(announcements))

  // 清空表单
  Object.assign(announcement, {
    title: '',
    content: '',
    audience: 'all'
  })

  alert('公告发布成功')
}

const backupDatabase = () => {
  // 模拟数据库备份
  settings.lastBackup = new Date().toLocaleString('zh-CN')
  localStorage.setItem('systemSettings', JSON.stringify(settings))
  alert('数据库备份完成')
}

const viewSystemLogs = () => {
  alert('系统日志查看功能开发中...')
}

const clearCache = () => {
  if (confirm('确定要清理系统缓存吗？')) {
    // 清理缓存
    localStorage.removeItem('cacheData')
    alert('缓存清理完成')
  }
}

const toggleSystemStatus = () => {
  if (systemStatus.value === 'online') {
    if (confirm('确定要进入系统维护模式吗？在此期间用户将无法访问系统。')) {
      systemStatus.value = 'maintenance'
      alert('系统已进入维护模式')
    }
  } else {
    systemStatus.value = 'online'
    alert('系统已恢复正常运行')
  }
}

// 生命周期
onMounted(() => {
  // 加载系统设置
  const savedSettings = localStorage.getItem('systemSettings')
  if (savedSettings) {
    Object.assign(settings, JSON.parse(savedSettings))
  }
})
</script>

<style scoped>
/* 组件特有样式 */
.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 0 20px;
}

.form-row .form-group {
  flex: 1;
}

.form-group {
  margin-bottom: 20px;
  padding: 0 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.form-control:focus {
  outline: none;
  border-color: #003366;
  box-shadow: 0 0 0 2px rgba(0, 51, 102, 0.2);
}

.small-input {
  width: 100px;
  display: inline-block;
  margin-right: 10px;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 10px;
  border-top: 1px solid #eee;
  background-color: #ffffff;
}

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

.help-text {
  font-size: 12px;
  color: #6c757d;
  margin-top: 5px;
}

.system-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.status-indicator.online {
  background-color: #28a745;
}

.status-indicator.maintenance {
  background-color: #ffc107;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .radio-group {
    flex-direction: column;
    gap: 10px;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions .btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {

  .form-row,
  .form-group {
    padding: 0 15px;
  }

  .form-actions {
    padding: 15px;
  }
}
</style>

<style>
/* 引入共享样式 */
@import '../common/shared-styles.css';
</style>