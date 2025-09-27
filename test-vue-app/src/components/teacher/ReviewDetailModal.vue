<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content large" @click.stop>
      <div class="modal-header">
        <h3>审核详情</h3>
        <button class="close-btn" @click="$emit('close')">
          <font-awesome-icon :icon="['fas', 'times']" />
        </button>
      </div>
      
      <div class="modal-body">
        <!-- 学生基本信息 -->
        <div class="card">
          <div class="card-title">学生基本信息</div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">姓名</label>
              <input type="text" class="form-control" :value="application.studentName" disabled>
            </div>
            <div class="form-group">
              <label class="form-label">学号</label>
              <input type="text" class="form-control" :value="application.studentId" disabled>
            </div>
            <div class="form-group">
              <label class="form-label">性别</label>
              <input type="text" class="form-control" value="男" disabled>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">所在系</label>
              <input type="text" class="form-control" :value="getDepartmentText(application.department)" disabled>
            </div>
            <div class="form-group">
              <label class="form-label">专业</label>
              <input type="text" class="form-control" :value="getMajorText(application.major)" disabled>
            </div>
          </div>
        </div>

        <!-- 申请项目详情 -->
        <div class="card">
          <div class="card-title">申请项目详情</div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">申请类型</label>
              <input type="text" class="form-control" :value="getTypeText(application.applicationType)" disabled>
            </div>
            <div class="form-group">
              <label class="form-label">项目全称</label>
              <input type="text" class="form-control" :value="application.projectName" disabled>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">获奖/成果落款时间</label>
              <input type="text" class="form-control" :value="formatDate(application.awardDate)" disabled>
            </div>
            <div class="form-group">
              <label class="form-label">奖项级别</label>
              <input type="text" class="form-control" :value="getLevelText(application.awardLevel)" disabled>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">奖项类型</label>
              <input type="text" class="form-control" :value="application.awardType === 'individual' ? '个人奖项' : '集体奖项'" disabled>
            </div>
            <div class="form-group">
              <label class="form-label">学生自评加分</label>
              <input type="text" class="form-control" :value="application.selfScore" disabled>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">加分依据说明</label>
            <textarea class="form-control" rows="4" :value="application.description" disabled></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">证明文件</label>
            <div class="file-preview" v-if="application.files && application.files.length > 0">
              <div v-for="(file, index) in application.files" :key="index" class="file-item">
                <div class="file-name">
                  <font-awesome-icon :icon="getFileIcon(file.name)" />
                  <span>{{ file.name }}</span>
                </div>
                <div class="file-actions">
                  <button class="btn-outline btn small-btn" @click="downloadFile(file)">
                    <font-awesome-icon :icon="['fas', 'download']" /> 下载
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="no-files">
              暂无证明文件
            </div>
          </div>
        </div>

        <!-- 审核操作区 -->
        <div class="card">
          <div class="card-title">审核操作</div>
          <div class="form-group">
            <label class="form-label">学院核定加分</label>
            <input type="number" class="form-control small-input" v-model="reviewData.finalScore" 
                   step="0.1" min="0" max="5">
            <div class="help-text">根据学校相关规定核定加分值</div>
          </div>
          <div class="form-group">
            <label class="form-label">核定说明</label>
            <textarea class="form-control" rows="3" v-model="reviewData.approveComment" 
                      placeholder="请填写核定说明（可选）"></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">驳回意见</label>
            <textarea class="form-control" rows="3" v-model="reviewData.rejectComment" 
                      placeholder="如驳回，请填写驳回理由"></textarea>
          </div>
          <div class="form-actions">
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
</template>

<script setup>
import { ref, reactive } from 'vue'

const props = defineProps({
  application: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['approve', 'reject', 'close'])

const reviewData = reactive({
  finalScore: props.application.selfScore || 0,
  approveComment: '',
  rejectComment: ''
})

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

const downloadFile = (file) => {
  // 模拟文件下载
  alert(`开始下载文件: ${file.name}`)
}

const approveApplication = () => {
  if (!reviewData.finalScore || reviewData.finalScore <= 0) {
    alert('请输入有效的核定分数')
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
  max-width: 1000px;
  max-height: 90vh;
  overflow: auto;
}

.modal-content.large {
  max-width: 1200px;
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
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #003366;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.form-row .form-group {
  flex: 1;
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

.form-control:disabled {
  background-color: #f5f5f5;
  color: #666;
}

.small-input {
  width: 120px;
}

textarea.form-control {
  min-height: 80px;
  resize: vertical;
}

.file-preview {
  margin-top: 10px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 8px;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.no-files {
  text-align: center;
  color: #666;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
  gap: 5px;
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

.small-btn {
  padding: 6px 10px;
  font-size: 12px;
}

.help-text {
  font-size: 12px;
  color: #6c757d;
  margin-top: 5px;
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    margin: 20px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>