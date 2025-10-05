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
        <!-- 左侧：申请信息和审核操作 -->
        <div class="left-column">
          <!-- 学生基本信息 -->
          <div class="card compact-card">
            <div class="card-title">学生信息</div>
            <div class="compact-row">
              <div class="compact-group">
                <label>姓名</label>
                <span>{{ application.studentName }}</span>
              </div>
              <div class="compact-group">
                <label>学号</label>
                <span>{{ application.studentId }}</span>
              </div>
              <div class="compact-group">
                <label>所在系</label>
                <span>{{ getDepartmentText(application.department) }}</span>
              </div>
              <div class="compact-group">
                <label>专业</label>
                <span>{{ getMajorText(application.major) }}</span>
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

          <!-- 审核操作区 -->
          <div class="card compact-card">
            <div class="card-title">审核操作</div>
            <div class="compact-row">
              <div class="compact-group">
                <label>核定加分</label>
                <input type="number" class="form-control small" v-model="reviewData.finalScore" 
                       step="0.1" min="0" max="5" placeholder="0-5分">
              </div>
            </div>
            <div class="compact-row">
              <div class="compact-group half-width">
                <label>核定说明</label>
                <textarea class="form-control small-textarea" v-model="reviewData.approveComment" 
                          rows="2" placeholder="通过说明（可选）"></textarea>
              </div>
              <div class="compact-group half-width">
                <label>驳回意见</label>
                <textarea class="form-control small-textarea" v-model="reviewData.rejectComment" 
                          rows="2" placeholder="驳回理由"></textarea>
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

        <!-- 右侧：文件预览区域 -->
        <div class="right-column" v-if="hasFiles">
          <div class="card preview-card">
            <!-- 图片预览区域（仅在存在图片时显示） -->
            <div v-if="hasImages">
              <div class="card-title">
                证明文件预览
                <span class="image-counter">({{ currentImageIndex + 1 }}/{{ imageFiles.length }})</span>
              </div>
              
              <!-- 主预览区域 -->
              <div class="main-preview">
                <div class="image-container">
                  <img :src="getFileUrl(currentImage)" :alt="currentImage.name" class="preview-image" />
                  <div class="image-overlay">
                    <button class="btn-icon overlay-btn" @click="downloadFile(currentImage)" title="下载">
                      <font-awesome-icon :icon="['fas', 'download']" />
                    </button>
                    <button class="btn-icon overlay-btn" @click="zoomImage" title="放大">
                      <font-awesome-icon :icon="['fas', 'search-plus']" />
                    </button>
                  </div>
                </div>
              </div>

              <!-- 图片导航（多张图片时显示） -->
              <div class="image-navigation" v-if="imageFiles.length > 1">
                <button class="nav-btn" @click="prevImage" :disabled="currentImageIndex === 0">
                  <font-awesome-icon :icon="['fas', 'chevron-left']" />
                </button>
                <div class="thumbnail-list">
                  <div v-for="(file, index) in imageFiles" 
                       :key="index" 
                       class="thumbnail-item"
                       :class="{ active: index === currentImageIndex }"
                       @click="switchImage(index)">
                    <img :src="getFileUrl(file)" :alt="file.name" />
                  </div>
                </div>
                <button class="nav-btn" @click="nextImage" :disabled="currentImageIndex === imageFiles.length - 1">
                  <font-awesome-icon :icon="['fas', 'chevron-right']" />
                </button>
              </div>
            </div>

            <!-- 文件列表区域（始终显示，只要存在文件） -->
            <div class="file-list-section">
              <div class="card-title" v-if="!hasImages">证明文件</div>
              <div class="file-list-compact">
                <div class="file-list-title" v-if="hasImages">所有文件</div>
                <div v-for="(file, index) in application.files" :key="index" class="file-item-compact">
                  <font-awesome-icon :icon="getFileIcon(file.name)" />
                  <span class="file-name">{{ file.name }}</span>
                  <div class="file-actions">
                    <button v-if="isImage(file)" 
                            class="btn-icon" 
                            @click="switchToImage(file)"
                            :class="{ active: isCurrentImage(file) }"
                            title="预览图片">
                      <font-awesome-icon :icon="['fas', 'eye']" />
                    </button>
                    <button class="btn-icon" @click="downloadFile(file)" title="下载">
                      <font-awesome-icon :icon="['fas', 'download']" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 如果没有文件，显示提示 -->
        <div class="right-column" v-else>
          <div class="card preview-card">
            <div class="card-title">证明文件</div>
            <div class="no-files">
              <font-awesome-icon :icon="['fas', 'folder-open']" class="no-files-icon" />
              <p>暂无证明文件</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 增强的放大预览模态框 -->
  <div v-if="zoomedImage" class="modal-overlay zoom-overlay" @click="closeZoom">
    <div class="modal-content zoom-content" @click.stop>
      <div class="modal-header">
        <h3>{{ zoomedImage.name }}</h3>
        <div class="zoom-controls">
          <div class="zoom-buttons">
            <button class="btn-icon" @click="zoomOut" title="缩小">
              <font-awesome-icon :icon="['fas', 'search-minus']" />
            </button>
            <span class="zoom-level">{{ Math.round(zoomLevel * 100) }}%</span>
            <button class="btn-icon" @click="zoomIn" title="放大">
              <font-awesome-icon :icon="['fas', 'search-plus']" />
            </button>
            <button class="btn-icon" @click="resetZoom" title="重置">
              <font-awesome-icon :icon="['fas', 'sync']" />
            </button>
          </div>
        </div>
        <button class="close-btn" @click="closeZoom">
          <font-awesome-icon :icon="['fas', 'times']" />
        </button>
      </div>
      <div class="zoom-body" 
           @mousedown="startDrag"
           @mousemove="onDrag"
           @mouseup="endDrag"
           @mouseleave="endDrag"
           @wheel="onWheel">
        <div class="zoom-container" 
             :style="{
               transform: `translate(${dragOffset.x}px, ${dragOffset.y}px) scale(${zoomLevel})`,
               cursor: isDragging ? 'grabbing' : 'grab'
             }">
          <img :src="getFileUrl(zoomedImage)" 
               :alt="zoomedImage.name" 
               class="zoomed-image"
               @load="onImageLoad" />
        </div>
      </div>
      <div class="zoom-actions">
        <button class="btn" @click="downloadFile(zoomedImage)">
          <font-awesome-icon :icon="['fas', 'download']" /> 下载
        </button>
        <button class="btn btn-outline" @click="closeZoom">
          <font-awesome-icon :icon="['fas', 'times']" /> 关闭
        </button>
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
const zoomedImage = ref(null)

// 计算属性
const imageFiles = computed(() => {
  return props.application.files?.filter(file => isImage(file)) || []
})

const hasImages = computed(() => {
  return imageFiles.value.length > 0
})

// 添加这个缺失的计算属性
const hasFiles = computed(() => {
  return props.application.files && props.application.files.length > 0
})

const currentImage = computed(() => {
  return imageFiles.value[currentImageIndex.value] || null
})

// 放大预览相关状态
const zoomLevel = ref(1)
const dragOffset = reactive({ x: 0, y: 0 })
const isDragging = ref(false)
const lastDragPos = reactive({ x: 0, y: 0 })
const imageDimensions = reactive({ width: 0, height: 0 })

// 方法
const isImage = (file) => {
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg']
  const ext = file.name.split('.').pop().toLowerCase()
  return imageExtensions.includes(ext)
}

const getFileIcon = (fileName) => {
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
  if (file instanceof File) {
    return URL.createObjectURL(file)
  }
  if (file.data) return file.data
  return `/uploads/${file.name}`
}

// 图片导航方法
const switchImage = (index) => {
  currentImageIndex.value = index
}

const prevImage = () => {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--
  }
}

const nextImage = () => {
  if (currentImageIndex.value < imageFiles.value.length - 1) {
    currentImageIndex.value++
  }
}

const switchToImage = (file) => {
  const index = imageFiles.value.findIndex(f => f.name === file.name)
  if (index !== -1) {
    currentImageIndex.value = index
  }
}

const isCurrentImage = (file) => {
  return currentImage.value && currentImage.value.name === file.name
}

// 放大预览功能
const zoomImage = () => {
  if (currentImage.value) {
    zoomedImage.value = currentImage.value
    resetZoom()
  }
}

const closeZoom = () => {
  zoomedImage.value = null
  resetZoom()
}

// 缩放控制
const zoomIn = () => {
  zoomLevel.value = Math.min(zoomLevel.value + 0.25, 5)
}

const zoomOut = () => {
  zoomLevel.value = Math.max(zoomLevel.value - 0.25, 0.25)
}

const resetZoom = () => {
  zoomLevel.value = 1
  dragOffset.x = 0
  dragOffset.y = 0
}

// 拖拽功能
const startDrag = (event) => {
  if (event.button !== 0) return // 只响应左键点击
  isDragging.value = true
  lastDragPos.x = event.clientX
  lastDragPos.y = event.clientY
  event.preventDefault()
}

const onDrag = (event) => {
  if (!isDragging.value) return
  
  const deltaX = event.clientX - lastDragPos.x
  const deltaY = event.clientY - lastDragPos.y
  
  dragOffset.x += deltaX
  dragOffset.y += deltaY
  
  lastDragPos.x = event.clientX
  lastDragPos.y = event.clientY
  event.preventDefault()
}

const endDrag = () => {
  isDragging.value = false
}

// 鼠标滚轮缩放
const onWheel = (event) => {
  event.preventDefault()
  
  const delta = -Math.sign(event.deltaY) * 0.1
  const newZoom = Math.max(0.25, Math.min(5, zoomLevel.value + delta))
  
  // 以鼠标位置为中心进行缩放
  const rect = event.currentTarget.getBoundingClientRect()
  const mouseX = event.clientX - rect.left
  const mouseY = event.clientY - rect.top
  
  // 计算缩放中心点
  const zoomPointX = (mouseX - dragOffset.x) / zoomLevel.value
  const zoomPointY = (mouseY - dragOffset.y) / zoomLevel.value
  
  zoomLevel.value = newZoom
  
  // 调整位置以保持缩放中心
  dragOffset.x = mouseX - zoomPointX * newZoom
  dragOffset.y = mouseY - zoomPointY * newZoom
}

// 图片加载完成时获取尺寸
const onImageLoad = (event) => {
  const img = event.target
  imageDimensions.width = img.naturalWidth
  imageDimensions.height = img.naturalHeight
}

// 下载文件
const downloadFile = (file) => {
  if (file.url) {
    const link = document.createElement('a')
    link.href = file.url
    link.download = file.name
    link.click()
  } else if (file instanceof File) {
    const url = URL.createObjectURL(file)
    const link = document.createElement('a')
    link.href = url
    link.download = file.name
    link.click()
    URL.revokeObjectURL(url)
  } else {
    alert(`开始下载文件: ${file.name}`)
  }
}

// 监听 application 变化，初始化审核数据和图片
watch(() => props.application, (newApp) => {
  if (newApp) {
    reviewData.finalScore = newApp.selfScore || 0
    reviewData.approveComment = ''
    reviewData.rejectComment = ''
    
    // 重置图片索引
    currentImageIndex.value = 0
  }
}, { immediate: true })

// 其他现有方法保持不变...
const getDepartmentText = (department) => {
  const departments = {
    cs: '计算机科学系',
    se: '软件工程系',
    ai: '人工智能系'
  }
  return departments[department] || department
}

const getMajorText = (major) => {
  const majors = {
    cs: '计算机科学与技术',
    se: '软件工程',
    ai: '人工智能'
  }
  return majors[major] || major
}

const getTypeText = (type) => {
  return type === 'academic' ? '学术专长' : '综合表现'
}

const getLevelText = (level) => {
  const levels = {
    national: '国家级',
    provincial: '省级',
    municipal: '市级',
    school: '校级'
  }
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
/* 添加文件列表区域的样式 */
.file-list-section {
  margin-top: 15px;
  border-top: 1px solid #eee;
  padding-top: 15px;
}

/* 双列布局 */
.two-column-layout {
  display: flex;
  flex-direction: column;
  max-width: 1200px;
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

.left-column {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  border-right: 1px solid #eee;
}

.right-column {
  width: 400px;
  min-width: 350px;
  padding: 20px;
  overflow-y: auto;
  background: #f8f9fa;
}

/* 右侧预览区域样式 */
.preview-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.image-counter {
  font-size: 14px;
  color: #666;
  font-weight: normal;
  margin-left: 8px;
}

.main-preview {
  margin-bottom: 15px;
  border: 1px solid #eee;
  border-radius: 6px;
  overflow: hidden;
  background: #fafafa;
}

.image-container {
  position: relative;
  height: 250px;
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
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.image-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 5px;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-container:hover .image-overlay {
  opacity: 1;
}

.overlay-btn {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px;
  cursor: pointer;
  font-size: 14px;
}

.overlay-btn:hover {
  background: rgba(0, 0, 0, 0.9);
}

.no-image, .no-files {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.no-image-icon, .no-files-icon {
  font-size: 48px;
  margin-bottom: 10px;
  color: #ccc;
}

/* 图片导航 */
.image-navigation {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.nav-btn {
  background: #003366;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 12px;
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.thumbnail-list {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  flex: 1;
  padding: 5px 0;
}

.thumbnail-item {
  width: 60px;
  height: 60px;
  border: 2px solid transparent;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
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
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.file-list-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #333;
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

.btn-icon:hover, .btn-icon.active {
  background: #003366;
  color: white;
}

/* 增强的放大预览样式 */
.zoom-overlay {
  background-color: rgba(255, 255, 255, 0.9);
  z-index: 2000;
}

.zoom-content {
  max-width: 95%;
  max-height: 95%;
  width: 95%;
  height: 95%;
  display: flex;
  flex-direction: column;
  background: #ffffff;
}

.zoom-body {
  flex: 1;
  overflow: hidden;
  position: relative;
  background: #ffffff;
  cursor: grab;
  user-select: none;
  -webkit-user-select: none;
  border-bottom: 1px solid #33333324;
}

.zoom-body:active {
  cursor: grabbing;
}

.zoom-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.1s ease-out;
  transform-origin: center center;
}

.zoomed-image {
  max-width: none;
  max-height: none;
  pointer-events: none;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;
  justify-content: center;
}

.zoom-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(0, 0, 0, 0.1);
  padding: 5px 10px;
  border-radius: 20px;
}

.zoom-level {
  color: rgb(0, 0, 0);
  font-size: 14px;
  min-width: 50px;
  text-align: center;
  font-weight: 600;
}

.zoom-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.1);
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
    max-height: 50%;
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
  
  .left-column, .right-column {
    padding: 15px;
  }
  
  .zoom-content {
    width: 98%;
    height: 98%;
  }
  
  .zoom-controls {
    flex-direction: column;
    gap: 8px;
  }
}

/* 原有的其他样式保持不变 */
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

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  background: rgb(255, 255, 255);
  flex-shrink: 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: rgb(0, 0, 0);
}

.zoom-overlay .modal-header {
  background: #ffffff;

}

.zoom-overlay .modal-header h3 {
  color: rgb(0, 0, 0);
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #666;
  padding: 5px;
}

.zoom-overlay .close-btn {
  color: #666;
}

.close-btn:hover {
  color: #333;
}

.zoom-overlay .close-btn:hover {
  color: #333;
}

/* 左侧内容的原有样式保持不变 */
.compact-card {
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 15px;
  margin-bottom: 15px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #003366;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.compact-row {
  display: flex;
  gap: 15px;
  margin-bottom: 12px;
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

.form-control {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-control.small {
  width: 100px;
}

.form-control.small-textarea {
  resize: vertical;
  min-height: 60px;
  font-size: 13px;
}

.form-control:focus {
  outline: none;
  border-color: #003366;
  box-shadow: 0 0 0 2px rgba(0, 51, 102, 0.1);
}

.form-actions-compact {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 15px;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
  gap: 5px;
  min-width: 80px;
  justify-content: center;
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

.btn-outline {
  background-color: transparent;
  color: #003366;
  border: 1px solid #003366;
}

.btn-outline:hover {
  background-color: #003366;
  color: white;
}
</style>