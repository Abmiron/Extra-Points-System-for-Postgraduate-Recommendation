<template>
  <div class="page-content">
    <div class="page-title">
      <span>加分申请</span>
    </div>

    <div class="card application-card">
      <form @submit.prevent="submitForm" class="application-form">
        <!-- 申请类型 -->
        <div class="form-section">
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'tag']" />
            <span>申请类型</span>
          </div>
          <div class="radio-cards compact">
            <div class="radio-card" 
                 :class="{ active: formData.applicationType === 'academic' }"
                 @click="formData.applicationType = 'academic'">
              <div class="radio-icon">
                <font-awesome-icon :icon="['fas', 'book']" />
              </div>
              <span>学术专长</span>
            </div>
            <div class="radio-card" 
                 :class="{ active: formData.applicationType === 'comprehensive' }"
                 @click="formData.applicationType = 'comprehensive'">
              <div class="radio-icon">
                <font-awesome-icon :icon="['fas', 'trophy']" />
              </div>
              <span>综合表现</span>
            </div>
          </div>
        </div>

        <!-- 基本信息 -->
        <div class="form-section">
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'info-circle']" />
            <span>基本信息</span>
          </div>
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">项目全称</label>
              <div class="input-with-icon">
                <font-awesome-icon :icon="['fas', 'signature']" />
                <input type="text" class="form-control" v-model="formData.projectName" 
                       placeholder="请输入项目全称" maxlength="100" required>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">获奖时间</label>
              <div class="input-with-icon">
                <font-awesome-icon :icon="['fas', 'calendar']" />
                <input type="date" class="form-control" v-model="formData.awardDate" required>
              </div>
            </div>
          </div>
        </div>

        <!-- 奖项信息 -->
        <div class="form-section">
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'award']" />
            <span>奖项信息</span>
          </div>
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">奖项级别</label>
              <div class="select-with-icon">
                <font-awesome-icon :icon="['fas', 'medal']" />
                <select class="form-control" v-model="formData.awardLevel" required>
                  <option value="">请选择奖项级别</option>
                  <option value="national">国家级</option>
                  <option value="provincial">省级</option>
                  <option value="municipal">市级</option>
                  <option value="school">校级</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">奖项类型</label>
              <div class="radio-cards compact">
                <div class="radio-card small" 
                     :class="{ active: formData.awardType === 'individual' }"
                     @click="formData.awardType = 'individual'">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'user']" />
                  </div>
                  <span>个人</span>
                </div>
                <div class="radio-card small" 
                     :class="{ active: formData.awardType === 'team' }"
                     @click="formData.awardType = 'team'">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'users']" />
                  </div>
                  <span>团队</span>
                </div>
              </div>
            </div>
          </div>
          <div class="form-grid" v-if="formData.awardType === 'team'">
            <div class="form-group">
              <label class="form-label">作者排序</label>
              <div class="input-with-icon">
                <font-awesome-icon :icon="['fas', 'hashtag']" />
                <input type="number" class="form-control" v-model="formData.authorOrder" 
                       min="1" placeholder="请输入作者排序">
              </div>
            </div>
          </div>
        </div>

        <!-- 加分详情 -->
        <div class="form-section">
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'star']" />
            <span>加分详情</span>
          </div>
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">自评加分</label>
              <div class="input-with-icon">
                <font-awesome-icon :icon="['fas', 'calculator']" />
                <input type="number" class="form-control" v-model="formData.selfScore" 
                       step="0.1" min="0" placeholder="请输入自评加分" required>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">加分依据说明</label>
            <textarea class="form-control" v-model="formData.description" 
                      rows="3" maxlength="300" placeholder="请详细说明加分依据..." required></textarea>
            <div class="char-counter">{{ formData.description.length }}/300</div>
          </div>
        </div>

        <!-- 证明材料 -->
        <div class="form-section">
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'paperclip']" />
            <span>证明材料</span>
          </div>
          <div class="file-upload-area" 
               @click="triggerFileInput" 
               @drop="handleDrop" 
               @dragover.prevent 
               @dragenter.prevent>
            <div class="upload-icon">
              <font-awesome-icon :icon="['fas', 'cloud-upload-alt']" />
            </div>
            <div class="upload-text">
              <p>点击或拖拽文件到此处上传</p>
              <p class="help-text">支持 PDF, JPG, PNG 格式，单个文件不超过10MB</p>
            </div>
          </div>
          <input type="file" ref="fileInput" style="display: none;" 
                 accept=".pdf,.jpg,.jpeg,.png" @change="handleFileSelect" multiple>
          
          <div class="file-list" v-if="formData.files.length > 0">
            <div class="file-list-header">
              <span>已上传文件 ({{ formData.files.length }})</span>
            </div>
            <div v-for="(file, index) in formData.files" :key="index" class="file-item">
              <div class="file-icon">
                <font-awesome-icon :icon="getFileIcon(file.name)" />
              </div>
              <div class="file-info">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-meta">{{ formatFileSize(file.size) }}</div>
              </div>
              <div class="file-actions">
                <button class="file-action-btn" @click="previewFile(file)" title="预览">
                  <font-awesome-icon :icon="['fas', 'eye']" />
                </button>
                <button class="file-action-btn" @click="removeFile(index)" title="删除">
                  <font-awesome-icon :icon="['fas', 'times']" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <button type="button" class="btn btn-outline" @click="saveDraft">
            <font-awesome-icon :icon="['fas', 'save']" />
            保存草稿
          </button>
          <button type="submit" class="btn btn-primary">
            <font-awesome-icon :icon="['fas', 'paper-plane']" />
            提交审核
          </button>
        </div>
      </form>
    </div>

    <!-- 文件预览模态框 -->
    <div v-if="previewFileData" class="modal-overlay" @click="closePreview">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>
            <font-awesome-icon :icon="getFileIcon(previewFileData.name)" />
            文件预览
          </h3>
          <button class="close-btn" @click="closePreview">
            <font-awesome-icon :icon="['fas', 'times']" />
          </button>
        </div>
        <div class="modal-body">
          <div v-if="isImageFile(previewFileData.name)" class="image-preview">
            <img :src="previewFileData.url" :alt="previewFileData.name" />
          </div>
          <div v-else class="file-preview">
            <div class="file-preview-icon">
              <font-awesome-icon :icon="getFileIcon(previewFileData.name)" size="4x" />
            </div>
            <h4>{{ previewFileData.name }}</h4>
            <p class="help-text">该文件类型不支持在线预览，请下载后查看</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const fileInput = ref(null)
const previewFileData = ref(null)

const formData = reactive({
  applicationType: 'academic',
  projectName: '',
  awardDate: '',
  awardLevel: '',
  awardType: 'individual',
  authorOrder: '',
  selfScore: '',
  description: '',
  files: []
})

const getFileIcon = (fileName) => {
  const ext = fileName.split('.').pop().toLowerCase()
  if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext)) {
    return ['fas', 'file-image']
  } else if (ext === 'pdf') {
    return ['fas', 'file-pdf']
  } else {
    return ['fas', 'file']
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const isImageFile = (fileName) => {
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
  const ext = fileName.split('.').pop().toLowerCase()
  return imageExtensions.includes(ext)
}

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  files.forEach(file => {
    if (file.size > 10 * 1024 * 1024) {
      alert(`文件 ${file.name} 大小超过10MB限制`)
      return
    }
    formData.files.push(file)
  })
  event.target.value = ''
}

const handleDrop = (event) => {
  event.preventDefault()
  const files = Array.from(event.dataTransfer.files)
  files.forEach(file => {
    if (file.size > 10 * 1024 * 1024) {
      alert(`文件 ${file.name} 大小超过10MB限制`)
      return
    }
    formData.files.push(file)
  })
}

const removeFile = (index) => {
  formData.files.splice(index, 1)
}

const previewFile = (file) => {
  if (isImageFile(file.name)) {
    const url = URL.createObjectURL(file)
    previewFileData.value = {
      name: file.name,
      url: url,
      file: file
    }
  } else {
    previewFileData.value = {
      name: file.name,
      file: file
    }
  }
}

const closePreview = () => {
  if (previewFileData.value && previewFileData.value.url) {
    URL.revokeObjectURL(previewFileData.value.url)
  }
  previewFileData.value = null
}

const downloadFile = (fileData) => {
  const url = URL.createObjectURL(fileData.file)
  const a = document.createElement('a')
  a.href = url
  a.download = fileData.name
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const saveDraft = () => {
  const drafts = JSON.parse(localStorage.getItem('applicationDrafts') || '[]')
  const draft = {
    id: Date.now(),
    ...formData,
    createdAt: new Date().toISOString()
  }
  drafts.push(draft)
  localStorage.setItem('applicationDrafts', JSON.stringify(drafts))
  alert('草稿已保存')
}

const submitForm = () => {
  if (!formData.projectName) {
    alert('请输入项目全称')
    return
  }
  
  if (!formData.awardDate) {
    alert('请选择获奖时间')
    return
  }
  
  if (!formData.awardLevel) {
    alert('请选择奖项级别')
    return
  }
  
  if (!formData.selfScore) {
    alert('请输入自评加分')
    return
  }
  
  if (formData.files.length === 0) {
    alert('请上传证明文件')
    return
  }

  const applications = JSON.parse(localStorage.getItem('studentApplications') || '[]')
  const application = {
    id: 'APP' + Date.now(),
    ...formData,
    status: 'pending',
    appliedAt: new Date().toISOString(),
    finalScore: null,
    reviewedAt: null
  }
  
  applications.push(application)
  localStorage.setItem('studentApplications', JSON.stringify(applications))
  
  alert('申请已提交，等待审核中...')
  
  Object.assign(formData, {
    applicationType: 'academic',
    projectName: '',
    awardDate: '',
    awardLevel: '',
    awardType: 'individual',
    authorOrder: '',
    selfScore: '',
    description: '',
    files: []
  })
}
</script>

<style scoped>
/* 引入共享样式 */
@import '../common/shared-styles.css';

/* 应用表单特有样式 */
.application-form {
  padding: 0;
}

.form-section {
  padding: 10px 15px; /* 减少垂直padding */
  border-bottom: 1px solid #f0f4f8;
}

.form-section:last-child {
  border-bottom: none;
}

.section-title {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px; /* 减少底部间距 */
  font-size: 1rem;
}

.section-title svg {
  margin-right: 8px;
  color: #003366;
  width: 16px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px; /* 减少网格间距 */
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 3px;
}

.form-label {
  font-weight: 500;
  color: #333;
  margin-bottom: 6px; /* 减少标签底部间距 */
  font-size: 0.95rem;
}

/* 输入框图标样式 */
.input-with-icon, .select-with-icon {
  position: relative;
}

.input-with-icon svg, .select-with-icon svg {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
  z-index: 2;
}

.input-with-icon .form-control, .select-with-icon .form-control {
  padding-left: 35px;
}

/* 单选卡片样式 */
.radio-cards {
  display: flex;
  gap: 8px; /* 减少卡片间距 */
}

.radio-cards.compact {
  gap: 6px;
}

.radio-card {
  display: flex;
  align-items: center;
  padding: 8px 12px; /* 减少卡片内边距 */
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.radio-card.small {
  padding: 6px 10px; /* 减少小卡片内边距 */
  font-size: 0.9rem;
}

.radio-card:hover {
  border-color: #003366;
}

.radio-card.active {
  border-color: #003366;
  background-color: #f0f7ff;
  color: #003366;
}

.radio-icon {
  margin-right: 6px; /* 减少图标右边距 */
  color: #666;
}

.radio-card.active .radio-icon {
  color: #003366;
}

/* 文件上传区域 */
.file-upload-area {
  display: flex;
  align-items: center;
  border: 2px dashed #ddd;
  border-radius: 6px;
  padding: 15px; /* 减少内边距 */
  cursor: pointer;
  transition: all 0.2s;
  background: #fafafa;
  margin-bottom: 12px; /* 减少底部间距 */
}

.file-upload-area:hover {
  border-color: #003366;
  background: #f5f9ff;
}

.upload-icon {
  font-size: 1.8rem; /* 稍微减小图标大小 */
  color: #666;
  margin-right: 12px; /* 减少右边距 */
}

.upload-text p {
  margin: 0;
  color: #333;
}

.help-text {
  font-size: 0.85rem;
  color: #666;
  margin-top: 4px; /* 减少顶部间距 */
}

/* 文件列表 */
.file-list {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.file-list-header {
  padding: 8px 12px; /* 减少内边距 */
  background-color: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
  font-weight: 500;
  color: #333;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 10px 12px; /* 减少内边距 */
  background-color: white;
  border-bottom: 1px solid #f0f0f0;
}

.file-item:last-child {
  border-bottom: none;
}

.file-icon {
  font-size: 1.2rem;
  color: #666;
  margin-right: 10px; /* 减少右边距 */
  width: 20px;
}

.file-info {
  flex: 1;
  padding-bottom:10px; ;
}

.file-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 2px;
}

.file-meta {
  font-size: 0.85rem;
  color: #666;
}

.file-actions {
  display: flex;
  gap: 6px; /* 减少操作按钮间距 */
}

.file-action-btn {
  background: none;
  border: none;
  padding: 5px; /* 减少内边距 */
  cursor: pointer;
  color: #666;
  border-radius: 3px;
  transition: all 0.2s;
}

.file-action-btn:hover {
  background-color: #f0f0f0;
  color: #333;
}

/* 字符计数器 */
.char-counter {
  text-align: right;
  font-size: 0.65rem;
  color: #666;
}

/* 操作按钮 */
.form-actions {
  padding: 15px 20px; /* 减少内边距 */
  background: #ffffff;
  border-top: 1px solid #ffffff;
  display: flex;
  justify-content: flex-end;
  gap: 12px; /* 减少按钮间距 */
}

/* 模态框特有样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  width: 90vw;
  height: 90vh;
  max-width: 1200px;
  max-height: 800px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #f0f4f8;
  background-color: #f8f9fa;
}

.modal-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
  padding: 5px;
  border-radius: 3px;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: #f0f0f0;
  color: #333;
}

.modal-body {
  flex: 1;
  padding: 20px;
  overflow: auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 图片预览区域 */
.image-preview {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 4px;
}

/* 文件预览区域 */
.file-preview {
  text-align: center;
  padding: 40px 20px;
  width: 100%;
}

.file-preview-icon {
  margin-bottom: 20px;
  color: #666;
}

.file-preview h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 1.2rem;
}


/* 响应式调整 */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
    gap: 10px; /* 移动端也减少间距 */
  }
  
  .radio-cards {
    flex-direction: column;
  }
  
  .file-upload-area {
    flex-direction: column;
    text-align: center;
    padding: 12px; /* 移动端减少内边距 */
  }
  
  .upload-icon {
    margin-right: 0;
    margin-bottom: 8px; /* 减少底部间距 */
  }
  
  .form-actions {
    flex-direction: column;
    padding: 12px 15px; /* 移动端减少内边距 */
  }
  
  .btn {
    justify-content: center;
  }

  .modal-content {
    width: 95vw;
    height: 95vh;
    max-width: none;
    max-height: none;
  }
  
  .modal-header {
    padding: 12px 15px;
  }
  
  .modal-body {
    padding: 15px;
  }
  
  .file-preview {
    padding: 30px 15px;
  }
  
  .file-preview h4 {
    font-size: 1.1rem;
  }
}
</style>