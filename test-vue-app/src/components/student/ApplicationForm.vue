<template>
  <div class="page-content">
    <div class="page-title">
      <span>加分申请</span>
    </div>

    <div class="card">
      <div class="card-title">填写申请信息</div>
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label class="form-label">申请类型</label>
          <div class="radio-group">
            <label class="radio-label">
              <input type="radio" v-model="formData.applicationType" value="academic" checked>
              <span>学术专长</span>
            </label>
            <label class="radio-label">
              <input type="radio" v-model="formData.applicationType" value="comprehensive">
              <span>综合表现</span>
            </label>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">项目全称</label>
          <input type="text" class="form-control" v-model="formData.projectName" 
                 placeholder="请输入项目全称" maxlength="100" required>
        </div>

        <div class="form-group">
          <label class="form-label">获奖/成果落款时间</label>
          <input type="date" class="form-control" v-model="formData.awardDate" required>
        </div>

        <div class="form-group">
          <label class="form-label">奖项级别</label>
          <select class="form-control" v-model="formData.awardLevel" required>
            <option value="">请选择</option>
            <option value="national">国家级</option>
            <option value="provincial">省级</option>
            <option value="municipal">市级</option>
            <option value="school">校级</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">奖项类型</label>
          <div class="radio-group">
            <label class="radio-label">
              <input type="radio" v-model="formData.awardType" value="individual" checked>
              <span>个人奖项</span>
            </label>
            <label class="radio-label">
              <input type="radio" v-model="formData.awardType" value="team">
              <span>集体奖项</span>
            </label>
          </div>
        </div>

        <div class="form-group" v-if="formData.awardType === 'team'">
          <label class="form-label">作者排序</label>
          <input type="number" class="form-control" v-model="formData.authorOrder" 
                 min="1" placeholder="请输入作者排序">
        </div>

        <div class="form-group">
          <label class="form-label">学生自评加分</label>
          <input type="number" class="form-control" v-model="formData.selfScore" 
                 step="0.1" min="0" placeholder="请输入自评加分" required>
        </div>

        <div class="form-group">
          <label class="form-label">加分依据说明</label>
          <textarea class="form-control" v-model="formData.description" 
                    rows="4" maxlength="300" placeholder="请详细说明加分依据" required></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">证明文件上传</label>
          <div class="file-upload" @click="triggerFileInput" @drop="handleDrop" 
               @dragover.prevent @dragenter.prevent>
            <font-awesome-icon :icon="['fas', 'cloud-upload-alt']" />
            <p>点击或拖拽文件到此处上传</p>
            <p class="help-text">支持格式: PDF, JPG, PNG (最大10MB)</p>
          </div>
          <input type="file" ref="fileInput" style="display: none;" 
                 accept=".pdf,.jpg,.jpeg,.png" @change="handleFileSelect" multiple>
          <div class="file-list">
            <div v-for="(file, index) in formData.files" :key="index" class="file-item">
              <div class="file-name">
                <font-awesome-icon :icon="getFileIcon(file.name)" />
                <span>{{ file.name }}</span>
                <span class="file-size">({{ formatFileSize(file.size) }})</span>
              </div>
              <div class="file-actions">
                <font-awesome-icon :icon="['fas', 'eye']" class="file-action" 
                                 @click="previewFile(file)" title="预览" />
                <font-awesome-icon :icon="['fas', 'times']" class="file-action" 
                                 @click="removeFile(index)" title="删除" />
              </div>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="btn btn-outline" @click="saveDraft">保存草稿</button>
          <button type="submit" class="btn">提交审核</button>
        </div>
      </form>
    </div>

    <!-- 文件预览模态框 -->
    <div v-if="previewFileData" class="modal-overlay" @click="closePreview">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>文件预览</h3>
          <button class="close-btn" @click="closePreview">
            <font-awesome-icon :icon="['fas', 'times']" />
          </button>
        </div>
        <div class="modal-body">
          <div v-if="isImageFile(previewFileData.name)" class="image-preview">
            <img :src="previewFileData.url" :alt="previewFileData.name" />
          </div>
          <div v-else class="file-preview">
            <font-awesome-icon :icon="['fas', 'file']" size="6x" />
            <p>{{ previewFileData.name }}</p>
            <p class="help-text">该文件类型不支持在线预览，请下载后查看</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="closePreview">关闭</button>
          <button class="btn" @click="downloadFile(previewFileData)">下载</button>
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
  // 保存草稿到本地存储
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
  // 验证表单
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

  // 模拟提交到后端
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
  
  // 重置表单
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
.page-content {
  display: block;
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

.file-upload svg {
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

.file-size {
  color: #666;
  font-size: 12px;
}

.file-actions {
  display: flex;
  gap: 10px;
}

.file-action {
  color: #666;
  cursor: pointer;
  transition: color 0.3s;
}

.file-action:hover {
  color: #003366;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  background-color: #003366;
  color: white;
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

.help-text {
  font-size: 12px;
  color: #6c757d;
  margin-top: 5px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.image-preview {
  text-align: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 400px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.file-preview {
  text-align: center;
  padding: 40px 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

@media (max-width: 768px) {
  .radio-group {
    flex-direction: column;
    gap: 10px;
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