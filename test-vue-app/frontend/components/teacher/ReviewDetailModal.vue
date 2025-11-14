<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content two-column-layout" @click.stop>
      <div class="modal-header">
        <h3>审核详情</h3>
        <button class="close-btn" @click="$emit('close')">
          <font-awesome-icon :icon="['fas', 'times']" />
        </button>
      </div>

      <div class="modal-body">
        <!-- 左侧：文件预览区域 -->
        <div class="left-column" v-if="hasFiles">
          <div class="card preview-card">
            <!-- 图片预览区域 -->
            <div v-if="hasImages">
              <div class="card-title">
                证明文件预览
                <span class="image-counter">({{ currentImageIndex + 1 }}/{{ imageFiles.length }})</span>
                <div class="preview-controls">
                  <button class="btn-icon" @click="zoomOut" title="缩小" :disabled="previewZoomLevel <= 0.5">
                    <font-awesome-icon :icon="['fas', 'search-minus']" />
                  </button>
                  <span class="zoom-level">{{ Math.round(previewZoomLevel * 100) }}%</span>
                  <button class="btn-icon" @click="zoomIn" title="放大" :disabled="previewZoomLevel >= 3">
                    <font-awesome-icon :icon="['fas', 'search-plus']" />
                  </button>
                  <button class="btn-icon" @click="resetPreviewZoom" title="重置">
                    <font-awesome-icon :icon="['fas', 'sync']" />
                  </button>
                  <button class="btn-icon" @click="downloadFile(currentImage)" title="下载">
                    <font-awesome-icon :icon="['fas', 'download']" />
                  </button>
                </div>
              </div>

              <!-- 图片导航移动到控制按钮下方、主预览区域上方 -->
              <div class="image-navigation" v-if="imageFiles.length > 1">
                <button class="nav-btn" @click="prevImage" :disabled="currentImageIndex === 0">
                  <font-awesome-icon :icon="['fas', 'chevron-left']" />
                </button>
                <div class="thumbnail-list">
                  <div v-for="(file, index) in imageFiles" :key="index" class="thumbnail-item"
                    :class="{ active: index === currentImageIndex }" @click="switchImage(index)">
                    <img :src="getFileUrl(file)" :alt="file.name" />
                  </div>
                </div>
                <button class="nav-btn" @click="nextImage" :disabled="currentImageIndex === imageFiles.length - 1">
                  <font-awesome-icon :icon="['fas', 'chevron-right']" />
                </button>
              </div>

              <!-- 主预览区域 -->
              <div class="main-preview">
                <div class="image-container" @mousedown="startPreviewDrag" @mousemove="onPreviewDrag"
                  @mouseup="endPreviewDrag" @mouseleave="endPreviewDrag" @wheel="onPreviewWheel">
                  <div class="image-transform-container" :style="{
                    transform: `translate(${previewDragOffset.x}px, ${previewDragOffset.y}px) scale(${previewZoomLevel})`,
                    cursor: isPreviewDragging ? 'grabbing' : 'grab'
                  }">
                    <img :src="getFileUrl(currentImage)" :alt="currentImage.name" class="preview-image"
                      @load="onPreviewImageLoad" />
                  </div>
                </div>
              </div>

            </div>

            <!-- 没有图片但有其他文件时显示提示 -->
            <div v-else>
              <div class="card-title">证明文件预览</div>
              <div class="no-files">
                <font-awesome-icon :icon="['fas', 'file-image']" class="no-files-icon" />
                <p>暂无图片文件可预览</p>
                <p class="no-files-desc">您可以在右侧文件列表中下载其他格式的文件</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 没有文件时显示提示 -->
        <div class="left-column" v-else>
          <div class="card preview-card">
            <div class="card-title">证明文件预览</div>
            <div class="no-files">
              <font-awesome-icon :icon="['fas', 'folder-open']" class="no-files-icon" />
              <p>暂无证明文件</p>
            </div>
          </div>
        </div>

        <!-- 右侧：申请信息和审核操作 -->
        <div class="right-column">
          <!-- 学生基本信息 -->
          <div class="card compact-card">
            <div class="card-title">学生信息</div>
            <div class="compact-row">
              <div class="compact-group">
                <label>姓名</label>
                <span>{{ application.studentName || 'N/A' }}</span>
              </div>
              <div class="compact-group">
                <label>学号</label>
                <span>{{ application.studentId || 'N/A' }}</span>
              </div>
              <div class="compact-group">
                <label>所在系</label>
                <span>{{ application.department ? getDepartmentText(application.department) : 'N/A' }}</span>
              </div>
              <div class="compact-group">
                <label>专业</label>
                <span>{{ application.major ? getMajorText(application.major) : 'N/A' }}</span>
              </div>
            </div>
          </div>

          <!-- 申请项目详情 -->
          <div class="card compact-card">
            <div class="card-title">申请详情</div>
            <div class="compact-grid">
              <div class="compact-group">
                <label>申请类型</label>
                <span>{{ getTypeText(application.applicationType) }}</span>
              </div>
              <div class="compact-group">
                <label>项目名称</label>
                <span class="truncate">{{ application.projectName }}</span>
              </div>
              <div class="compact-group">
                <label>获奖时间</label>
                <span>{{ formatDate(application.awardDate) }}</span>
              </div>
              <div class="compact-group">
                <label>奖项级别</label>
                <span>{{ getLevelText(application.awardLevel) }}</span>
              </div>
              <div class="compact-group">
                <label>奖项类型</label>
                <span>{{ application.awardType === 'individual' ? '个人' : '集体' }}</span>
              </div>
              <div class="compact-group">
                <label>自评分数</label>
                <span>{{ application.selfScore }}</span>
              </div>
            </div>

            <div class="compact-group full-width">
              <label>加分依据</label>
              <div class="description-text">{{ application.description }}</div>
            </div>
          </div>

          <!-- 文件列表区域 -->
          <div class="card compact-card" v-if="hasFiles">
            <div class="card-title">证明文件</div>
            <div class="file-list-compact">
              <div v-for="(file, index) in application.files" :key="index" class="file-item-compact">
                <font-awesome-icon :icon="getFileIcon(file.name)" />
                <span class="file-name">{{ file.name }}</span>
                <div class="file-actions">
                  <button v-if="isImage(file)" class="btn-icon" @click="switchToImage(file)"
                    :class="{ active: isCurrentImage(file) }" title="预览图片">
                    <font-awesome-icon :icon="['fas', 'eye']" />
                  </button>
                  <button class="btn-icon" @click="downloadFile(file)" title="下载">
                    <font-awesome-icon :icon="['fas', 'download']" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 审核操作区 -->
          <div class="card compact-card">
            <div class="card-title">审核操作</div>
            <div class="compact-row">
              <div class="compact-group">
                <label>核定加分</label>
                <input type="number" class="form-control small" v-model="reviewData.finalScore" step="0.1" min="0"
                  max="5" placeholder="0-5分">
              </div>
            </div>
            <div class="compact-row">
              <div class="compact-group half-width">
                <label>核定说明</label>
                <textarea class="form-control small-textarea" v-model="reviewData.approveComment" rows="2"
                  placeholder="通过说明（可选）"></textarea>
              </div>
              <div class="compact-group half-width">
                <label>驳回意见</label>
                <textarea class="form-control small-textarea" v-model="reviewData.rejectComment" rows="2"
                  placeholder="驳回理由"></textarea>
              </div>
            </div>
            <div class="form-actions-compact">
              <button type="button" class="btn btn-reject" @click="rejectApplication">
                <font-awesome-icon :icon="['fas', 'times']" /> 驳回
              </button>
              <button type="button" class="btn btn-approve" @click="approveApplication">
                <font-awesome-icon :icon="['fas', 'check']" /> 通过
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'

const props = defineProps({
  application: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['approve', 'reject', 'close'])

const reviewData = reactive({
  finalScore: 0,
  approveComment: '',
  rejectComment: ''
})

// 图片相关状态
const currentImageIndex = ref(0)
const previewZoomLevel = ref(1)
const previewDragOffset = reactive({ x: 0, y: 0 })
const isPreviewDragging = ref(false)
const previewLastDragPos = reactive({ x: 0, y: 0 })

// 计算属性
const imageFiles = computed(() => {
  // 确保 application.files 是数组（若未定义则转为空数组）
  const files = props.application.files || [];
  return files.filter(file => isImage(file));
})

const hasImages = computed(() => imageFiles.value.length > 0)
const hasFiles = computed(() => props.application.files && props.application.files.length > 0)
const currentImage = computed(() => imageFiles.value[currentImageIndex.value] || null)

// 方法
const isImage = (file) => {
  // 先判断 file 和 file.name 是否存在
  if (!file || !file.name) return false;
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg']
  const ext = file.name.split('.').pop().toLowerCase()
  return imageExtensions.includes(ext)
}

const getFileIcon = (fileName) => {
  if (!fileName) {
    return ['fas', 'file'] // 当fileName为undefined或null时返回默认图标
  }
  const ext = fileName.split('.').pop().toLowerCase()
  if (isImage({ name: fileName })) {
    return ['fas', 'file-image']
  } else if (ext === 'pdf') {
    return ['fas', 'file-pdf']
  } else {
    return ['fas', 'file']
  }
}

const getFileUrl = (file) => {
  if (file.url) return file.url
  if (file instanceof File) return URL.createObjectURL(file)
  if (file.data) return file.data
  return `/uploads/${file.name}`
}

// 图片导航方法
const switchImage = (index) => {
  currentImageIndex.value = index
  resetPreviewZoom()
}

const prevImage = () => {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--
    resetPreviewZoom()
  }
}

const nextImage = () => {
  if (currentImageIndex.value < imageFiles.value.length - 1) {
    currentImageIndex.value++
    resetPreviewZoom()
  }
}

const switchToImage = (file) => {
  const index = imageFiles.value.findIndex(f => f.name === file.name)
  if (index !== -1) switchImage(index)
}

const isCurrentImage = (file) => currentImage.value && currentImage.value.name === file.name

// 预览区域缩放控制
const zoomIn = () => {
  previewZoomLevel.value = Math.min(previewZoomLevel.value + 0.25, 3)
}

const zoomOut = () => {
  previewZoomLevel.value = Math.max(previewZoomLevel.value - 0.25, 0.5)
}

const resetPreviewZoom = () => {
  previewZoomLevel.value = 1
  previewDragOffset.x = 0
  previewDragOffset.y = 0
}

// 预览区域拖拽功能
const startPreviewDrag = (event) => {
  if (event.button !== 0) return
  isPreviewDragging.value = true
  previewLastDragPos.x = event.clientX
  previewLastDragPos.y = event.clientY
  event.preventDefault()
}

const onPreviewDrag = (event) => {
  if (!isPreviewDragging.value) return

  const deltaX = event.clientX - previewLastDragPos.x
  const deltaY = event.clientY - previewLastDragPos.y

  previewDragOffset.x += deltaX
  previewDragOffset.y += deltaY

  previewLastDragPos.x = event.clientX
  previewLastDragPos.y = event.clientY
  event.preventDefault()
}

const endPreviewDrag = () => {
  isPreviewDragging.value = false
}

// 预览区域鼠标滚轮缩放
const onPreviewWheel = (event) => {
  event.preventDefault()

  const delta = -Math.sign(event.deltaY) * 0.1
  const newZoom = Math.max(0.5, Math.min(3, previewZoomLevel.value + delta))

  const rect = event.currentTarget.getBoundingClientRect()
  const mouseX = event.clientX - rect.left
  const mouseY = event.clientY - rect.top

  const zoomPointX = (mouseX - previewDragOffset.x) / previewZoomLevel.value
  const zoomPointY = (mouseY - previewDragOffset.y) / previewZoomLevel.value

  previewZoomLevel.value = newZoom

  previewDragOffset.x = mouseX - zoomPointX * newZoom
  previewDragOffset.y = mouseY - zoomPointY * newZoom
}

// 下载文件
const downloadFile = (file) => {
  let url = ''
  if (file.url) {
    url = file.url
  } else if (file instanceof File) {
    url = URL.createObjectURL(file)
  } else {
    alert(`开始下载文件: ${file.name}`)
    return
  }

  const link = document.createElement('a')
  link.href = url
  link.download = file.name
  link.click()

  if (file instanceof File) {
    URL.revokeObjectURL(url)
  }
}

// 监听 application 变化
watch(() => props.application, (newApp) => {
  if (newApp) {
    reviewData.finalScore = newApp.selfScore || 0
    reviewData.approveComment = ''
    reviewData.rejectComment = ''

    currentImageIndex.value = 0
    resetPreviewZoom()
  }
}, { immediate: true })

// 其他方法
const getDepartmentText = (department) => {
  const departments = { cs: '计算机科学系', se: '软件工程系', ai: '人工智能系' }
  return departments[department] || department
}

const getMajorText = (major) => {
  const majors = { cs: '计算机科学与技术', se: '软件工程', ai: '人工智能' }
  return majors[major] || major
}

const getTypeText = (type) => type === 'academic' ? '学术专长' : '综合表现'

const getLevelText = (level) => {
  const levels = { national: '国家级', provincial: '省级', municipal: '市级', school: '校级' }
  return levels[level] || level
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const approveApplication = () => {
  if (!reviewData.finalScore || reviewData.finalScore <= 0) {
    alert('请输入有效的核定分数')
    return
  }

  if (reviewData.finalScore > 5) {
    alert('核定分数不能超过5分')
    return
  }

  emit('approve', props.application.id, reviewData.finalScore, reviewData.approveComment)
}

const rejectApplication = () => {
  if (!reviewData.rejectComment) {
    alert('请填写驳回理由')
    return
  }

  emit('reject', props.application.id, reviewData.rejectComment)
}
</script>

<style scoped>
/* 组件特有样式 */
.two-column-layout {
  display: flex;
  flex-direction: column;
  max-width: 1400px;
  max-height: 90vh;
  width: 95%;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.modal-body {
  display: flex;
  flex: 1;
  padding: 0;
  overflow: hidden;
  min-height: 0;
}

/* 左侧文件预览区域 */
.left-column {
  flex: 1.5;
  padding: 20px;
  overflow-y: auto;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
}

/* 右侧信息区域 */
.right-column {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
  gap: 15px;
  min-height: 0;
}

/* 预览卡片样式 */
.preview-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-bottom: 0;
}

.image-counter {
  font-size: 14px;
  color: #666;
  font-weight: normal;
  margin-left: 8px;
}

/* 预览控制按钮 */
.preview-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.preview-controls .btn-icon {
  background: rgba(0, 51, 102, 0.1);
  color: #003366;
  border: none;
  border-radius: 4px;
  padding: 6px 8px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.preview-controls .btn-icon:hover:not(:disabled) {
  background: #003366;
  color: white;
}

.preview-controls .btn-icon:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.preview-controls .zoom-level {
  font-size: 12px;
  font-weight: 600;
  color: #003366;
  min-width: 40px;
  text-align: center;
}

.main-preview {
  margin-bottom: 5px;
  border: 1px solid #eee;
  border-radius: 3px;
  overflow: hidden;
  background: #fafafa;
  flex: 1;
}

.image-container {
  position: relative;
  height: 690px;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    linear-gradient(45deg, #f0f0f0 25%, transparent 25%),
    linear-gradient(-45deg, #f0f0f0 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #f0f0f0 75%),
    linear-gradient(-45deg, transparent 75%, #f0f0f0 75%);
  background-size: 20px 20px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
  overflow: hidden;
  cursor: default;
}

.image-transform-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.1s ease-out;
  transform-origin: center center;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transition: transform 0.1s ease-out;
}

.no-files {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.no-files-icon {
  font-size: 48px;
  margin-bottom: 10px;
  color: #ccc;
}

.no-files-desc {
  font-size: 14px;
  margin-top: 10px;
  color: #999;
}

/* 图片导航样式调整 */
.image-navigation {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: -2px;
  padding: 0px 8px;
  background: #f8f9fa;
}

.nav-btn {
  background: #003366;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.nav-btn:hover:not(:disabled) {
  background: #002244;
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.thumbnail-list {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  flex: 1;
  padding: 2px 0;
}

.thumbnail-item {
  width: 60px;
  height: 60px;
  border: 2px solid transparent;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s;
}

.thumbnail-item:hover {
  border-color: #003366;
  opacity: 0.8;
}

.thumbnail-item.active {
  border-color: #003366;
}

.thumbnail-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 文件列表 */
.file-list-compact {
  padding-bottom: 0;
}

.file-item-compact {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 5px;
  font-size: 13px;
}

.file-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-actions {
  display: flex;
  gap: 5px;
}

.btn-icon {
  background: none;
  border: none;
  color: #003366;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 3px;
  font-size: 12px;
}

.btn-icon:hover,
.btn-icon.active {
  background: #003366;
  color: white;
}

/* 右侧内容样式 */
.compact-card {
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 15px;
  margin-bottom: 0;
  flex-shrink: 0;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #003366;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
}

.compact-row {
  display: flex;
  gap: 45px;
  flex-wrap: wrap;
}

.compact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.compact-group {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.compact-group.half-width {
  flex: 1;
}

.compact-group.full-width {
  width: 100%;
}

.compact-group label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
  font-weight: 500;
}

.compact-group span {
  font-size: 14px;
  color: #333;
  padding: 6px 0;
}

.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.description-text {
  font-size: 13px;
  line-height: 1.4;
  color: #555;
  background: #f8f9fa;
  padding: 8px 10px;
  border-radius: 4px;
  border-left: 3px solid #003366;
}

.form-control.small {
  width: 100px;
}

.form-control.small-textarea {
  resize: vertical;
  min-height: 60px;
  font-size: 13px;
}

.form-actions-compact {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 15px;
  padding-top: 12px;
  border-top: 1px solid #eee;
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

/* 滚动条样式 */
.file-list-compact::-webkit-scrollbar {
  display: none;
  /* 隐藏文件列表的滚动条 */
}

/* 确保右侧整体滚动 */
.right-column::-webkit-scrollbar {
  width: 8px;
}

.right-column::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.right-column::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.right-column::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}


/* 响应式设计 */
@media (max-width: 1024px) {
  .two-column-layout {
    max-height: 95vh;
  }

  .modal-body {
    flex-direction: column;
  }

  .left-column {
    border-right: none;
    border-bottom: 1px solid #eee;
    max-height: 50%;
  }

  .right-column {
    width: 100%;
    max-height: 50vh;
  }

  .image-container {
    height: 400px;
  }
}

@media (max-width: 768px) {
  .two-column-layout {
    width: 98%;
    margin: 10px;
    max-height: 95vh;
  }

  .modal-header {
    padding: 12px 15px;
  }

  .modal-header h3 {
    font-size: 16px;
  }

  .left-column {
    padding: 15px;
  }

  .right-column {
    padding: 15px;
    max-height: 40vh;
  }

  .preview-controls {
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 8px;
    margin-left: 0;
  }

  .card-title {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }

  .image-container {
    height: 300px;
  }
}
</style>

<style>
/* 引入共享样式 */
@import '../common/shared-styles.css';
</style>