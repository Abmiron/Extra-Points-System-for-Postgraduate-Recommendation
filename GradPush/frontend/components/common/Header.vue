<template>
  <header class="header">
    <div class="logo-area">
      <img src="/images/logo(1).png" alt="厦门大学校徽" class="logo">
      <span class="university-name">{{ title }}</span>
    </div>
    <div class="header-right">
      <div class="notification" @click="showFiles" title="查看推免相关文件">
        <font-awesome-icon :icon="['fas', 'file-alt']" />
        <span class="notification-badge" v-if="fileCount > 0">
          {{ fileCount }}
        </span>
      </div>
      <div class="user-menu">
        <div class="user-info" @click="goToProfile">
          <img :src="userAvatar" alt="用户头像" class="user-avatar">
          <span>{{ userName }}</span>
        </div>
        <button class="logout-btn" @click="handleLogout" title="退出登录">
          <font-awesome-icon :icon="['fas', 'sign-out-alt']" />
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useToastStore } from '../../stores/toast'
import { useFilesStore } from '../../stores/files'
const toastStore = useToastStore()

const props = defineProps({
  userName: String,
  userAvatar: String,
  title: {
    type: String,
    default: '推免加分系统'
  }
})

const emit = defineEmits(['go-to-profile'])

const router = useRouter()
const authStore = useAuthStore()
const filesStore = useFilesStore()

// 计算属性，从filesStore获取文件数量
const fileCount = computed(() => filesStore.fileCount)

// 组件挂载时加载文件列表
onMounted(async () => {
  const currentUser = authStore.user;
  const facultyId = currentUser ? currentUser.facultyId : null;
  await filesStore.loadFiles(facultyId)
})

// 显示文件列表
const showFiles = async () => {
  // 如果文件列表为空，尝试重新加载
  if (filesStore.files.length === 0) {
    const currentUser = authStore.user;
    const facultyId = currentUser ? currentUser.facultyId : null;
    await filesStore.loadFiles(facultyId)
  }
  
  if (filesStore.files.length === 0) {
    toastStore.info('暂无推免相关文件')
    return
  }
  
  // 创建文件列表HTML
  let fileListHTML = '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; padding-bottom: 12px; border-bottom: 2px solid #e9ecef;">' +
    '<h4 style="margin: 0; color: #333; font-size: 18px; font-weight: 600;">推免相关文件</h4>' +
    '<button id="modal-close-btn" style="background: none; border: none; color: #333; cursor: pointer; font-size: 20px; padding: 4px; border-radius: 4px; transition: all 0.2s ease;">' +
    '<i class="fas fa-times"></i>' +
    '</button>' +
    '</div>'
  
  // 使用表格样式显示文件列表
  fileListHTML += '<div style="overflow-x: auto;">' +
    '<table style="width: 100%; border-collapse: collapse; font-size: 14px;">' +
      '<tbody>'
  
  filesStore.files.forEach(file => {
    // 确保file和必要的字段存在
    if (!file || !file.filename) return;
    
    fileListHTML += `<tr style="border-bottom: 1px solid #e9ecef; transition: background-color 0.2s ease;">`
    fileListHTML += `<td style="padding: 8px;">`
    fileListHTML += `<div style="display: flex; align-items: center; gap: 8px;">`
    fileListHTML += `<span style="font-size: 18px; color: #003d86;">${getFileIcon(file.filename)}</span>`
    fileListHTML += `<span style="color: #333;">${file.filename}</span>`
    fileListHTML += `</div>`
    fileListHTML += `</td>`
    fileListHTML += `<td style="padding: 12px; color: #6c757d; white-space: nowrap;">${formatFileSize(file.file_size || 0)}</td>`
    fileListHTML += `<td style="padding: 12px; text-align: center;">`
    fileListHTML += `<div class="action-buttons">`
    fileListHTML += `<a href="http://localhost:5001${file.file_url || ''}" class="btn-outline btn small-btn" style="text-decoration: none;" title="下载">`
    fileListHTML += `<i class="fas fa-download"></i>`
    fileListHTML += `</a>`
    fileListHTML += `</div>`
    fileListHTML += `</td>`
    fileListHTML += `</tr>`
  })
  
  fileListHTML += '</tbody>' +
    '</table>' +
  '</div>'
  
  // 定义模态框显示文件列表
  const customAlert = document.createElement('div')
  customAlert.style.cssText = `
    position: fixed;
    top: 7%;
    left: 66%;
    background-color: white;
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
    z-index: 10000;
    max-width: 600px;
    width: 90%;
    max-height: 50vh;
    overflow-y: auto;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  `
  
  customAlert.innerHTML = fileListHTML
  
  // 添加遮罩层
  const overlay = document.createElement('div')
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0);
    z-index: 9999;
  `
  
  // 关闭函数
  const closeModal = () => {
    document.body.removeChild(customAlert)
    document.body.removeChild(overlay)
  }
  
  // 点击关闭图标关闭
  const closeBtn = customAlert.querySelector('#modal-close-btn')
  if (closeBtn) {
    closeBtn.addEventListener('click', closeModal)
    closeBtn.addEventListener('mouseover', () => {
      closeBtn.style.color = '#333'
      closeBtn.style.backgroundColor = '#f0f0f0'
    })
    closeBtn.addEventListener('mouseout', () => {
      closeBtn.style.color = '#6c757d'
      closeBtn.style.backgroundColor = 'transparent'
    })
  }
  
  // 点击遮罩层关闭
  overlay.onclick = closeModal
  
  document.body.appendChild(overlay)
  document.body.appendChild(customAlert)
}

// 获取文件图标（使用Unicode字符确保在动态HTML中正确显示）
const getFileIcon = (fileName) => {
  if (!fileName) return '📄';
  const ext = fileName.split('.').pop().toLowerCase()
  switch (ext) {
    case 'pdf':
      return '📄'
    case 'doc':
    case 'docx':
      return '📝'
    case 'xls':
    case 'xlsx':
      return '📊'
    case 'ppt':
    case 'pptx':
      return '📋'
    default:
      return '📄'
  }
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (size < 1024) {
    return `${size} B`
  } else if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(2)} KB`
  } else {
    return `${(size / (1024 * 1024)).toFixed(2)} MB`
  }
}



const goToProfile = () => {
  emit('go-to-profile')
}

const handleLogout = async () => {
  if (confirm('确定要退出登录吗？')) {
    try {
      // 调用authStore中的logout方法，该方法已包含后端API调用
      await authStore.logout()
      // 跳转到登录页面
      router.push('/login')
      toastStore.success('退出登录成功')
    } catch (error) {
      console.error('退出登录失败:', error)
      // 即使出现错误，也确保跳转到登录页面
      router.push('/login')
      toastStore.error('退出登录失败，请重试')
    }
  }
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #003d86, #0066cc);
  color: #fff;
  padding: 10px 20px;
  height: 60px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.logo-area {
  display: flex;
  align-items: center;
}

.logo {
  width: 150px;
  margin-right: 10px;
  border-radius: 4px;
  object-fit: contain;
}

.university-name {
  font-size: 20px;
  font-weight: bold;
  line-height: 60px;
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
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 5px;
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -1px;
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
  gap: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-bottom: 0px;
  padding: 0px;
  border-bottom: 0px solid transparent;
}

.user-info .user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  margin-right: 8px;
  object-fit: cover;
  /* 添加抗锯齿效果 */
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
  /* 添加轻微阴影增强视觉效果 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logout-btn {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 16px;
  margin-left: 15px;
}

@media (max-width: 768px) {
  .header {
    padding: 10px 15px;
  }

  .logo {
    width: 120px;
  }

  .university-name {
    font-size: 16px;
  }

  .user-menu span {
    display: none;
  }
}
</style>