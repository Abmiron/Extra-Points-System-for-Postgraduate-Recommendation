<template>
  <div>
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
              <input type="radio" v-model="formData.applicationType" value="academic">
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
          <input type="text" v-model="formData.projectName" class="form-control" placeholder="请输入项目全称" maxlength="100" required>
        </div>

        <div class="form-group">
          <label class="form-label">获奖/成果落款时间</label>
          <input type="date" v-model="formData.awardDate" class="form-control" required>
        </div>

        <div class="form-group">
          <label class="form-label">奖项级别</label>
          <select v-model="formData.awardLevel" class="form-control" required>
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
              <input type="radio" v-model="formData.awardType" value="individual">
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
          <input type="number" v-model="formData.authorOrder" class="form-control" min="1" placeholder="请输入作者排序">
        </div>

        <div class="form-group">
          <label class="form-label">学生自评加分</label>
          <input type="number" v-model="formData.selfScore" class="form-control" step="0.1" min="0" placeholder="请输入自评加分" required>
        </div>

        <div class="form-group">
          <label class="form-label">加分依据说明</label>
          <textarea v-model="formData.description" class="form-control" rows="4" maxlength="300" placeholder="请详细说明加分依据" required></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">证明文件上传</label>
          <div class="file-upload" @click="triggerFileInput">
            <i class="fas fa-cloud-upload-alt"></i>
            <p>点击或拖拽文件到此处上传</p>
            <p class="help-text">支持格式: PDF, JPG, PNG (最大10MB)</p>
          </div>
          <input type="file" ref="fileInput" style="display: none;" @change="handleFileUpload" accept=".pdf,.jpg,.jpeg,.png" multiple>
          <div class="file-list">
            <div v-for="(file, index) in uploadedFiles" :key="index" class="file-item">
              <div class="file-name">
                <i class="fas fa-file-pdf"></i>
                <span>{{ file.name }}</span>
              </div>
              <div class="file-actions">
                <i class="fas fa-times file-action" @click="removeFile(index)"></i>
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
  </div>
</template>

<script>
import { ref, reactive } from 'vue'

export default {
  name: 'ApplicationForm',
  setup() {
    const fileInput = ref(null)
    const uploadedFiles = ref([])
    
    const formData = reactive({
      applicationType: 'academic',
      projectName: '',
      awardDate: '',
      awardLevel: '',
      awardType: 'individual',
      authorOrder: 1,
      selfScore: 0,
      description: ''
    })

    const triggerFileInput = () => {
      fileInput.value.click()
    }

    const handleFileUpload = (event) => {
      const files = Array.from(event.target.files)
      uploadedFiles.value.push(...files)
    }

    const removeFile = (index) => {
      uploadedFiles.value.splice(index, 1)
    }

    const saveDraft = () => {
      alert('草稿已保存')
      // 这里可以添加保存草稿的逻辑
    }

    const submitForm = () => {
      alert('申请已提交，等待审核中...')
      // 这里可以添加表单提交逻辑
    }

    return {
      fileInput,
      uploadedFiles,
      formData,
      triggerFileInput,
      handleFileUpload,
      removeFile,
      saveDraft,
      submitForm
    }
  }
}
</script>