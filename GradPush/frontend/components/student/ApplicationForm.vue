<template>
  <div class="page-content">
    <div class="page-title">
      <span>加分申请</span>
    </div>

    <div class="card application-card">
      <form @submit.prevent="submitForm" class="application-form">
        <!-- 基本信息（通用） -->
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
                <input type="text" class="form-control" v-model="formData.projectName" placeholder="请输入项目全称"
                  maxlength="100" required>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">获得时间</label>
              <div class="input-with-icon">
                <font-awesome-icon :icon="['fas', 'calendar']" />
                <input type="date" class="form-control" v-model="formData.awardDate" required>
              </div>
            </div>
          </div>
        </div>

        <!-- 规则选择 -->
        <div class="form-section">
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'scroll']" />
            <span>规则选择</span>
          </div>
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">选择适用规则 <span class="required">*</span></label>
              <div class="select-with-button">
                <div class="select-with-icon">
                  <font-awesome-icon :icon="['fas', 'list-check']" />
                  <select class="form-control" v-model="formData.ruleId" required @change="calculateEstimatedScore">
                    <option value="">请选择规则</option>
                    <option v-for="rule in availableRules" :key="rule.id" :value="rule.id">
                      {{ rule.name }} (基础分数: {{ rule.score }})
                    </option>
                  </select>
                </div>
                <button type="button" class="btn btn-outline btn-small" @click="refreshRules">
                  <font-awesome-icon :icon="['fas', 'sync-alt']" />
                  刷新
                </button>
              </div>

              <!-- 规则说明显示区域 -->
              <div v-if="formData.ruleId" class="rule-description">
                <label class="form-label">规则说明</label>
                <div class="description-content">
                  {{availableRules.find(rule => rule.id === formData.ruleId)?.description || '暂无规则说明'}}
                </div>

              </div>
            </div>

          </div>
        </div>

        <!-- 规则系数填写区域 -->
        <div class="form-section" v-if="formData.ruleId">
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'calculator']" />
            <span>规则系数填写</span>
          </div>
          <div class="form-grid">
            <!-- 动态生成的表单字段 -->
            <div v-for="field in dynamicFormFields" :key="field.name" class="form-group">
              <label class="form-label">{{ field.label }}</label>

              <!-- 数字输入类型 -->
              <div v-if="field.type === 'number'" class="input-with-icon">
                <font-awesome-icon :icon="['fas', 'hashtag']" />
                <input type="number" class="form-control" v-model="formData.dynamicCoefficients[field.name]"
                  :min="field.min" :step="field.step || '1'" :placeholder="'请输入' + field.label">
              </div>

              <!-- 文本输入类型 -->
              <div v-else-if="field.type === 'text'" class="input-with-icon">
                <font-awesome-icon :icon="['fas', 'font']" />
                <input type="text" class="form-control" v-model="formData.dynamicCoefficients[field.name]"
                  :placeholder="'请输入' + field.label">
              </div>

              <!-- 单选按钮类型 -->
              <div v-else-if="field.type === 'radio'" class="radio-cards">
                <div v-for="option in field.options" :key="option.value" class="radio-card horizontal"
                  :class="{ active: formData.dynamicCoefficients[field.name] === option.value }"
                  @click.stop="formData.dynamicCoefficients[field.name] = option.value; calculateEstimatedScore()">
                  <div class="radio-icon">
                    <font-awesome-icon
                      :icon="['fas', option.value === 'top' || option.value === '1' ? 'star' : 'circle']" />
                  </div>
                  <span>{{ option.label }} ({{ option.value }}x)</span>
                </div>
              </div>

              <!-- 下拉选择类型 -->
              <div v-else-if="field.type === 'select'" class="input-with-icon">
                <font-awesome-icon :icon="['fas', 'list']" />
                <select class="form-control" v-model="formData.dynamicCoefficients[field.name]"
                  @change="calculateEstimatedScore()">
                  <option value="" disabled>请选择{{ field.label }}</option>
                  <option v-for="option in field.options" :key="option.value" :value="option.value">
                    {{ option.label }} (x{{ option.value }})
                  </option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- 没有选择规则时的提示 -->
        <div class="form-section" v-else>
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'info-circle']" />
            <span>请选择规则</span>
          </div>
          <div class="info-message">
            <p>请先选择适用的规则，系统将根据规则显示需要填写的系数字段。</p>
          </div>
        </div>

        <!-- 加分详情（通用） -->
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
                <input type="number" class="form-control" v-model="formData.selfScore" step="0.1" min="0"
                  placeholder="请输入自评加分" required>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">预估分数</label>
              <div class="input-with-icon">
                <font-awesome-icon :icon="['fas', 'chart-line']" />
                <input type="number" class="form-control" v-model="estimatedScore" step="0.1" min="0" readonly>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">加分依据说明</label>
            <textarea class="form-control" v-model="formData.description" rows="3" maxlength="300"
              placeholder="请详细说明加分依据..." required></textarea>
            <div class="char-counter">{{ formData.description.length }}/300</div>
          </div>
        </div>

        <!-- 证明材料（通用） -->
        <div class="form-section">
          <div class="section-title">
            <font-awesome-icon :icon="['fas', 'paperclip']" />
            <span>证明材料</span>
          </div>
          <div class="file-upload-area" @click="triggerFileInput" @drop="handleDrop" @dragover.prevent
            @dragenter.prevent>
            <div class="upload-icon">
              <font-awesome-icon :icon="['fas', 'cloud-upload-alt']" />
            </div>
            <div class="upload-text">
              <p>点击或拖拽文件到此处上传</p>
              <p class="help-text">支持 {{ fileUploadSettings.allowedFileTypesString }} 格式，单个文件不超过{{
                fileUploadSettings.singleFileSizeLimit }}MB，总文件大小不超过{{ fileUploadSettings.totalFileSizeLimit }}MB</p>

            </div>
          </div>
          <input type="file" ref="fileInput" style="display: none;"
            :accept="fileUploadSettings.allowedFileTypes.join(',')" @change="handleFileSelect" multiple>

          <div class="file-list" v-if="formData.files.length > 0">
            <div class="file-list-header">
              <span>已上传文件 ({{ formData.files.length }})</span>
            </div>
            <div v-for="(file, index) in formData.files" :key="file.name + index" class="file-item">
              <div class="file-icon">
                <font-awesome-icon :icon="getFileIcon(file.name)" />
              </div>
              <div class="file-info">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-meta">{{ formatFileSize(file.size) }}</div>
              </div>
              <div class="file-actions">
                <button type="button" class="file-action-btn" @click.stop="previewFile(file)" title="预览">
                  <font-awesome-icon :icon="['fas', 'eye']" />
                </button>
                <button type="button" class="file-action-btn" @click.stop="removeFile(index)" title="删除">
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
import { ref, reactive, watch, onMounted, computed } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useApplicationsStore } from '../../stores/applications'
import { useToastStore } from '../../stores/toast'

// 接收编辑申请ID
const props = defineProps(['editApplicationId'])

const authStore = useAuthStore()
const applicationsStore = useApplicationsStore()
const toastStore = useToastStore()
const fileInput = ref(null)
const previewFileData = ref(null)

// 表单数据
const formData = reactive({
  // 添加用户信息
  id: null, // 用于存储申请ID，编辑时使用
  studentId: authStore.user?.studentId || '',
  name: authStore.userName,
  departmentId: authStore.user?.departmentId || '',
  majorId: authStore.user?.majorId || '',
  facultyId: authStore.user?.facultyId || authStore.user?.faculty_id || '',

  // 基本信息
  projectName: '',
  awardDate: '',
  ruleId: '', // 选择的规则ID
  // 动态系数字段，根据规则配置自动生成
  dynamicCoefficients: {},
  // 通用字段
  selfScore: '',
  description: '',
  files: [],
  // 申请类型，将从规则中获取
  applicationType: ''
})

// 重置表单的通用函数
const resetForm = () => {
  Object.assign(formData, {
    id: null,
    studentId: authStore.user?.studentId || '',
    name: authStore.userName,
    departmentId: authStore.user?.departmentId || '',
    majorId: authStore.user?.majorId || '',
    projectName: '',
    awardDate: '',
    ruleId: '',
    selfScore: '',
    description: '',
    files: [],
    dynamicCoefficients: {},
    applicationType: '',
    facultyId: authStore.user?.facultyId || authStore.user?.faculty_id || ''
  })
}

// 规则选择和预估分数计算相关
import api from '../../utils/api'

const availableRules = ref([])
const estimatedScore = ref(0)

// 系统设置
const systemSettings = ref({
  singleFileSizeLimit: 10, // 默认10MB
  totalFileSizeLimit: 50, // 默认50MB
  allowedFileTypes: ['.pdf', '.jpg', '.jpeg', '.png'], // 数组格式，用于文件输入框的accept属性
  allowedFileTypesString: '.pdf, .jpg, .jpeg, .png' // 字符串格式，直接用于显示
})

// 计算属性，确保模板始终能获取到正确的值
const fileUploadSettings = computed(() => ({
  allowedFileTypesString: systemSettings.value?.allowedFileTypesString || '.pdf, .jpg, .jpeg, .png, .webp',
  singleFileSizeLimit: systemSettings.value?.singleFileSizeLimit || 10,
  totalFileSizeLimit: systemSettings.value?.totalFileSizeLimit || 50,
  allowedFileTypes: systemSettings.value?.allowedFileTypes || ['.pdf', '.jpg', '.jpeg', '.png', '.webp']
}))

// 加载编辑数据
const loadEditData = async (applicationId) => {
  // 如果没有ID或ID为空，重置为新表单
  if (!applicationId) {
    // 清空表单
    resetForm()
    return
  }
  try {
    const application = await applicationsStore.fetchApplicationById(applicationId)
    // 清空表单
    resetForm()
    // 先获取转换后的前端数据
    const frontendData = toFrontendFields(application)
    // 先设置ruleId，确保selectedRule能够正确计算
    if (frontendData.ruleId) {
      formData.ruleId = frontendData.ruleId
    }
    // 这将确保系数选择字段能够正确显示
    await fetchMatchingRules()
    // 填充表单基本数据（排除动态系数字段和ruleId，单独处理）
    for (const [key, value] of Object.entries(frontendData)) {
      if (key in formData && key !== 'dynamicCoefficients' && key !== 'ruleId') {
        formData[key] = value
      }
    }
    // 填充动态系数字段
    let dynamicCoefficients = {}
    // 从后端返回的数据中获取动态系数，处理不同的字段名和可能的JSON字符串
    if (application.dynamic_coefficients) {
      if (typeof application.dynamic_coefficients === 'string') {
        try {
          dynamicCoefficients = JSON.parse(application.dynamic_coefficients)
        } catch (error) {
          dynamicCoefficients = {}
        }
      } else {
        dynamicCoefficients = application.dynamic_coefficients
      }
    } else if (application.dynamicCoefficients) {
      if (typeof application.dynamicCoefficients === 'string') {
        try {
          dynamicCoefficients = JSON.parse(application.dynamicCoefficients)
        } catch (error) {
          dynamicCoefficients = {}
        }
      } else {
        dynamicCoefficients = application.dynamicCoefficients
      }
    }
    // 确保dynamicCoefficients是对象
    if (typeof dynamicCoefficients !== 'object' || dynamicCoefficients === null) {
      dynamicCoefficients = {}
    }
    // 将所有值转换为字符串类型，以匹配select选项的值类型
    const stringifiedCoefficients = {}
    for (const [key, value] of Object.entries(dynamicCoefficients)) {
      stringifiedCoefficients[key] = value !== null && value !== undefined ? String(value) : ''
    }
    // 清空现有的dynamicCoefficients
    Object.keys(formData.dynamicCoefficients).forEach(key => delete formData.dynamicCoefficients[key])
    // 使用Object.assign来更新dynamicCoefficients对象的属性，确保Vue的响应式系统能够正确跟踪变化
    Object.assign(formData.dynamicCoefficients, stringifiedCoefficients)
    // 处理文件（如果有）
    if (application.files && Array.isArray(application.files)) {
      // 将后端返回的文件数据转换为前端可用的格式
      formData.files = application.files.map(file => {
        // 后端返回的文件通常包含id、name、path等字段
        // 直接使用这些字段创建一个文件对象表示
        return {
          id: file.id,
          name: file.name,
          path: file.path,
          size: file.size || 0,
          // 标记这是后端返回的文件，不是浏览器File对象
          isBackendFile: true
        }
      })
    } else {
      formData.files = []
    }
  } catch (error) {
    console.error('加载编辑数据失败:', error)
    // 当加载失败（如404），重置为新表单
    resetForm()
  }
}

// 监听编辑申请ID变化
watch(() => props.editApplicationId, (newId) => {
  if (newId) {
    loadEditData(newId)
  }
}, { immediate: true })

// 监听表单关键字段变化，自动匹配规则
watch([
  () => formData.projectName,
  () => formData.ruleId
], () => {
  fetchMatchingRules()
}, { deep: true })

// 获取匹配的规则
const fetchMatchingRules = async () => {
  try {
    // 获取学生所在学院ID
    const studentFacultyId = authStore.user?.faculty_id || authStore.user?.facultyId
    // 使用正确的API方法获取规则
    const rulesResponse = await api.getRules({ faculty_id: studentFacultyId })
    // 过滤掉禁用的规则，只显示状态为'active'的规则
    availableRules.value = rulesResponse.rules.filter(rule => rule.status === 'active')
    // 为每个规则获取完整的计算配置信息
    for (let i = 0; i < availableRules.value.length; i++) {
      const rule = availableRules.value[i]
      try {
        const calculationResponse = await api.getRuleCalculation(rule.id)
        if (calculationResponse.data) {
          availableRules.value[i].calculation = calculationResponse.data
        }
      } catch (error) {
        console.error(`获取规则${rule.id}的计算配置失败:`, error)
      }
    }
    // 重新计算预估分数
    calculateEstimatedScore()
  } catch (error) {
    console.error('获取规则失败:', error)
  }
}

// 获取当前选中的规则
const selectedRule = computed(() => {
  if (!formData.ruleId) return null
  return availableRules.value.find(rule => rule.id === formData.ruleId)
})

// 动态生成的表单字段配置
const dynamicFormFields = computed(() => {
  if (!selectedRule.value?.calculation) return []
  const calculationType = selectedRule.value.calculation.calculation_type
  let parameters = selectedRule.value.calculation.parameters || {}
  // 解析参数（可能是JSON字符串）
  if (typeof parameters === 'string') {
    try {
      parameters = JSON.parse(parameters)
    } catch (error) {
      console.error('解析规则参数失败:', error)
      return []
    }
  }
  const fields = []
  // 根据计算类型生成不同的表单字段
  if (calculationType === 'multiplicative' || parameters.type === 'multiplicative') {
    // 为每个系数生成选择框
    const coefficients = parameters.coefficients || []
    coefficients.forEach(coefficient => {
      // 检查是否有items字段，如果有则生成下拉选择框
      if (coefficient.items && Array.isArray(coefficient.items)) {
        fields.push({
          name: coefficient.key,
          label: coefficient.name,
          type: 'select',
          options: coefficient.items.map(item => ({
            value: item.multiplier,
            label: item.name
          })),
          required: true
        })
      } else {
        // 否则生成数字输入框
        fields.push({
          name: coefficient.key,
          label: coefficient.name,
          type: 'number',
          min: 0,
          step: '0.1',
          required: true
        })
      }
    })
  } else if (calculationType === 'cumulative' || parameters.type === 'cumulative') {
    // 累积式计算：累积字段 + 乘数
    if (parameters.cumulative_field) {
      fields.push({
        name: parameters.cumulative_field,
        label: parameters.cumulative_field,
        type: 'number',
        min: 0,
        step: '1',
        required: true
      })
    }
    if (parameters.cumulative_multiplier !== undefined) {
      fields.push({
        name: 'cumulative_multiplier',
        label: '累积乘数',
        type: 'number',
        min: 0,
        step: '0.1',
        required: true
      })
    }
  }
  return fields
})

// 计算预估分数
const calculateEstimatedScore = async () => {
  if (!formData.ruleId) {
    estimatedScore.value = 0
    return
  }
  const selectedRule = availableRules.value.find(rule => rule.id === formData.ruleId)
  if (!selectedRule) {
    estimatedScore.value = 0
    return
  }
  // 从规则中获取applicationType并设置到表单数据中
  if (selectedRule.type) {
    formData.applicationType = selectedRule.type
  }
  try {
    // 准备学生数据
    const studentData = {
      faculty_id: authStore.user?.faculty_id || authStore.user?.facultyId,
      // 动态系数字段
      ...formData.dynamicCoefficients
    }
    // 调用后端API计算分数
    const scoreResponse = await api.calculateRuleScore(selectedRule.id, { student_data: studentData })
    estimatedScore.value = parseFloat(scoreResponse.data.score.toFixed(4))
  } catch (error) {
    console.error('计算预估分数失败:', error)
    console.error('错误详情:', error.response?.data || error.message)
    // 如果API调用失败，回退到前端计算
    let score = calculateScoreFrontend(selectedRule)
    console.log('前端计算的分数:', score)

    // 应用最大分数限制
    if (selectedRule.max_score && score > selectedRule.max_score) {
      score = selectedRule.max_score
      console.log('应用最大分数限制后:', score)
    }

    estimatedScore.value = parseFloat(score.toFixed(4))
  }
}

// 前端分数计算函数（与后端RuleEngine保持一致）
const calculateScoreFrontend = (rule) => {
  if (!rule || !rule.calculation) {
    // 如果没有计算配置，使用基础分数
    return rule.score || 0
  }

  let totalScore = 0

  // 根据计算类型执行不同的计算逻辑
  switch (rule.calculation.calculation_type) {
    case 'multiplicative':
      // 乘积式计算
      totalScore = calculateMultiplicativeScore(rule)
      break
    case 'cumulative':
      // 累积式计算
      totalScore = calculateCumulativeScore(rule)
      break
    default:
      // 默认使用基础分数
      totalScore = rule.score || 0
  }

  return totalScore
}

// 计算乘积式分数
const calculateMultiplicativeScore = (rule) => {
  let parameters = rule.calculation.parameters || {}

  // 解析参数（可能是JSON字符串）
  if (typeof parameters === 'string') {
    try {
      parameters = JSON.parse(parameters)
    } catch (error) {
      console.error('解析乘积式参数失败:', error)
      return rule.score || 0
    }
  }

  // 获取基础分值（使用规则或参数中定义的基础分值，不需要学生输入）
  const baseScore = parseFloat(parameters.base_score) || parseFloat(rule.score) || 0
  const coefficients = parameters.coefficients || []

  let totalMultiplier = 1.0

  // 计算所有系数的乘积
  coefficients.forEach(coefficient => {
    // 获取系数的值
    const fieldValue = parseFloat(getFieldValue(coefficient.key))
    if (!isNaN(fieldValue)) {
      totalMultiplier *= fieldValue
    }
  })

  return parseFloat((baseScore * totalMultiplier).toFixed(4))
}

// 计算累积式分数
const calculateCumulativeScore = (rule) => {
  let parameters = rule.calculation.parameters || {}

  // 解析参数（可能是JSON字符串）
  if (typeof parameters === 'string') {
    try {
      parameters = JSON.parse(parameters)
    } catch (error) {
      console.error('解析累积式参数失败:', error)
      return rule.score || 0
    }
  }

  const baseScore = parseFloat(rule.score) || parseFloat(parameters.base_score) || 0
  const cumulativeField = parameters.cumulative_field
  const cumulativeMultiplier = parseFloat(getFieldValue('cumulative_multiplier')) || parseFloat(parameters.cumulative_multiplier) || 0.1

  // 获取累积字段的值
  const cumulativeValue = parseFloat(getFieldValue(cumulativeField)) || 0

  // 计算累积分数
  return parseFloat((baseScore * cumulativeValue * cumulativeMultiplier).toFixed(4))
}

// 获取表单字段值
const getFieldValue = (fieldName) => {
  // 从动态系数中获取字段值
  if (formData.dynamicCoefficients[fieldName] !== undefined && formData.dynamicCoefficients[fieldName] !== null) {
    return formData.dynamicCoefficients[fieldName]
  }
  return undefined
}

// 刷新规则列表
const refreshRules = () => {
  fetchMatchingRules()
}

// 在组件挂载时自动刷新规则选择栏并加载系统设置
onMounted(() => {
  refreshRules()
  loadSystemSettings()
})

// 加载系统设置
const loadSystemSettings = async () => {
  try {
    const response = await api.getPublicSystemInfo()

    // 检查response是否存在
    if (response && response.data) {
      const settings = response.data

      // 将allowedFileTypes转换为数组，并保存原始字符串
      let allowedFileTypesArray = ['.pdf', '.jpg', '.jpeg', '.png']
      let allowedFileTypesString = '.pdf, .jpg, .jpeg, .png'

      if (settings.allowedFileTypes !== undefined && settings.allowedFileTypes !== null) {
        if (typeof settings.allowedFileTypes === 'string') {
          allowedFileTypesArray = settings.allowedFileTypes.split(',').map(ext => ext.trim())
          allowedFileTypesString = settings.allowedFileTypes
        } else if (Array.isArray(settings.allowedFileTypes)) {
          allowedFileTypesArray = settings.allowedFileTypes
          allowedFileTypesString = settings.allowedFileTypes.join(', ')
        }
      }

      // 更新systemSettings
      systemSettings.value = {
        singleFileSizeLimit: settings.singleFileSizeLimit || 10,
        totalFileSizeLimit: settings.totalFileSizeLimit || 50,
        allowedFileTypes: allowedFileTypesArray,
        allowedFileTypesString: allowedFileTypesString
      }
    }
  } catch (error) {
    console.error('获取系统设置失败:', error)
    // 确保systemSettings始终有默认值
    systemSettings.value = {
      singleFileSizeLimit: 10,
      totalFileSizeLimit: 50,
      allowedFileTypes: ['.pdf', '.jpg', '.jpeg', '.png'],
      allowedFileTypesString: '.pdf, .jpg, .jpeg, .png'
    }
  }
}

// 原有方法保持不变...
const getFileIcon = (fileName) => {
  if (!fileName) {
    return ['fas', 'file-question']
  }
  const ext = fileName.split('.').pop().toLowerCase()
  if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)) {
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
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
  const ext = fileName.split('.').pop().toLowerCase()
  return imageExtensions.includes(ext)
}

const triggerFileInput = () => {
  fileInput.value.click()
}

// 验证并添加文件的通用函数
const validateAndAddFiles = (files) => {
  // 检查总文件大小
  const currentTotalSize = formData.files.reduce((total, file) => total + file.size, 0)
  let totalSizeWithNewFiles = currentTotalSize

  for (const file of files) {
    totalSizeWithNewFiles += file.size
  }

  const totalLimit = systemSettings.value?.totalFileSizeLimit || 50
  const singleLimit = systemSettings.value?.singleFileSizeLimit || 10
  const allowedTypes = systemSettings.value?.allowedFileTypes || ['.pdf', '.jpg', '.jpeg', '.png']

  if (totalSizeWithNewFiles > totalLimit * 1024 * 1024) {
    toastStore.error(`总文件大小超过${totalLimit}MB限制`)
    return false
  }

  // 检查单个文件大小和类型
  for (const file of files) {
    if (file.size > singleLimit * 1024 * 1024) {
      toastStore.error(`文件 ${file.name} 大小超过${singleLimit}MB限制`)
      continue
    }

    const fileExt = `.${file.name.split('.').pop().toLowerCase()}`
    if (!allowedTypes.includes(fileExt)) {
      toastStore.error(`文件 ${file.name} 类型不支持，仅支持${allowedTypes.join(', ')}格式`)
      continue
    }

    // 使用展开运算符创建新数组，确保响应式更新
    formData.files = [...formData.files, file]
  }

  return true
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  validateAndAddFiles(files)
  event.target.value = ''
}

const handleDrop = (event) => {
  event.preventDefault()
  const files = Array.from(event.dataTransfer.files)
  validateAndAddFiles(files)
}

const removeFile = (index) => {
  // 使用展开运算符创建新数组，确保响应式更新
  formData.files = formData.files.filter((_, i) => i !== index)
}

const previewFile = (file) => {
  // 检查是否是浏览器File对象（用于新上传的文件）
  if (file instanceof File) {
    if (isImageFile(file.name)) {
      const url = URL.createObjectURL(file)
      previewFileData.value = {
        name: file.name,
        url: url,
        file: file,
        size: file.size
      }
    } else {
      previewFileData.value = {
        name: file.name,
        file: file,
        size: file.size
      }
    }
  } else {
    // 从后端获取的文件对象，通常包含id、name、path等字段
    // 对于后端图片文件，构建正确的预览URL
    let url = null
    if (isImageFile(file.name)) {
      if (file.path) {
        // 检查path是否已经是完整URL
        if (file.path.startsWith('http://') || file.path.startsWith('https://')) {
          url = file.path
        } else {
          // 添加服务器地址前缀
          url = `http://localhost:5001${file.path}`
        }
      } else if (file.id) {
        // 如果没有path字段，使用文件ID构建URL
        url = `http://localhost:5001/uploads/files/${file.id}`
      }
    }
    previewFileData.value = {
      name: file.name,
      url: url,
      file: file,
      size: file.size || 0
    }
  }
}

const closePreview = () => {
  if (previewFileData.value && previewFileData.value.url) {
    URL.revokeObjectURL(previewFileData.value.url)
  }
  previewFileData.value = null
}

// 获取applicationType的通用函数
const getApplicationType = () => {
  let applicationType = formData.applicationType
  if (!applicationType && formData.ruleId) {
    const selectedRule = availableRules.value.find(rule => rule.id === formData.ruleId)
    if (selectedRule && selectedRule.type) {
      applicationType = selectedRule.type
      // 将获取到的applicationType保存回formData，确保提交时包含该字段
      formData.applicationType = applicationType
    }
  }
  return applicationType
}

// 获取学生信息的通用函数
const getStudentInfo = () => {
  return {
    studentName: authStore.user?.name || authStore.userName || '未知学生',
    studentId: authStore.user?.studentId || '未知学号',
    facultyId: authStore.user?.facultyId || authStore.user?.faculty_id || '',
    departmentId: authStore.user?.departmentId || authStore.user?.department_id || '',
    majorId: authStore.user?.majorId || authStore.user?.major_id || ''
  }
}

// 定义后端到前端的字段映射
const backToFrontMappings = {
  student_id: 'studentId',
  faculty_id: 'facultyId',
  department_id: 'departmentId',
  major_id: 'majorId',
  project_name: 'projectName',
  award_date: 'awardDate',
  rule_id: 'ruleId',
  self_score: 'selfScore',
  final_score: 'finalScore',
  applied_at: 'appliedAt',
  created_at: 'createdAt',
  updated_at: 'updatedAt',
  application_type: 'applicationType'
}

// 将后端字段名转换为前端字段名
const toFrontendFields = (data) => {
  const result = { ...data }
  Object.keys(backToFrontMappings).forEach(backKey => {
    const frontKey = backToFrontMappings[backKey]
    if (result.hasOwnProperty(backKey)) {
      result[frontKey] = result[backKey]
      delete result[backKey]
    }
  })
  return result
}

// 准备申请数据的通用函数
const prepareApplicationData = (status) => {
  const { studentName, studentId, facultyId, departmentId, majorId } = getStudentInfo()
  const applicationType = getApplicationType()

  return {
    ...formData,
    // 确保使用正确的字段名，与显示组件保持一致
    studentName,
    studentId,
    facultyId,
    departmentId,
    majorId,
    status,
    appliedAt: new Date().toISOString(),
    applicationType
  }
}

// 修改保存草稿和提交表单的验证逻辑
const saveDraft = async () => {
  try {
    // 获取学生信息和applicationType
    const { studentName, studentId, facultyId, departmentId, majorId } = getStudentInfo()
    const applicationType = getApplicationType()

    // 准备草稿数据
    const draftData = prepareApplicationData('draft')

    let success
    if (formData.id) {
      // 更新现有申请
      success = await applicationsStore.updateApplication(formData.id, draftData)
    } else {
      // 创建新申请
      success = await applicationsStore.addApplication(draftData)
    }

    if (success) {
      toastStore.success('草稿已保存')
      // 保存成功后继续留在当前页面
    } else {
      toastStore.error('保存草稿失败，请稍后重试')
    }
  } catch (error) {
    console.error('保存草稿失败:', error)
    toastStore.error('保存草稿失败，请稍后重试')
  }
}

const submitForm = async () => {
  // 通用验证
  if (!formData.projectName) {
    toastStore.error('请输入项目全称')
    return
  }

  if (!formData.awardDate) {
    toastStore.error('请输入获得时间')
    return
  }

  if (!formData.description) {
    toastStore.error('请输入项目描述')
    return
  }

  if (!formData.ruleId) {
    toastStore.error('请选择适用规则')
    return
  }

  // 根据当前规则需要的动态字段进行验证
  for (const field of dynamicFormFields.value) {
    if (field.required && !formData.dynamicCoefficients[field.name]) {
      toastStore.error(`请输入${field.label}`)
      return
    }

    // 数字字段验证
    if (field.type === 'number' && formData.dynamicCoefficients[field.name]) {
      const value = parseFloat(formData.dynamicCoefficients[field.name])
      if (isNaN(value)) {
        toastStore.error(`${field.label}必须是数字`)
        return
      }
      if (field.min !== undefined && value < field.min) {
        toastStore.error(`${field.label}不能小于${field.min}`)
        return
      }
      if (field.max !== undefined && value > field.max) {
        toastStore.error(`${field.label}不能大于${field.max}`)
        return
      }
    }
  }

  // 通用字段验证
  if (!formData.selfScore) {
    toastStore.error('请输入自评加分')
    return
  }

  if (formData.files.length === 0) {
    toastStore.error('请上传证明文件')
    return
  }

  // 获取学生信息和applicationType
  const { studentName, studentId, facultyId, departmentId, majorId } = getStudentInfo()
  const applicationType = getApplicationType()

  // 确保studentName字段存在（兼容后端期望）
  formData.studentName = formData.name || authStore.userName

  // 准备申请数据
  const applicationData = prepareApplicationData('pending')

  try {
    let success
    if (formData.id) {
      // 更新现有申请
      success = await applicationsStore.updateApplication(formData.id, applicationData)
    } else {
      // 创建新申请
      success = await applicationsStore.addApplication(applicationData)
    }

    if (success) {
      toastStore.success('申请已提交，等待审核中...')

      // 重置表单
      resetForm()

      // 重置规则列表和预估分数
      availableRules.value = []
      estimatedScore.value = 0

      // 不再自动切换到申请历史页面，保持在加分申请页面
    } else {
      toastStore.error('提交失败，请稍后重试')
    }
  } catch (error) {
    console.error('提交申请失败:', error)
    toastStore.error('提交失败，请稍后重试')
  }
}
</script>

<style scoped>
/* 引入共享样式 */
@import '../common/shared-styles.css';

/* 必填项红色星号 */
.required {
  color: #ff4d4f;
}

/* 应用表单特有样式 */
.application-form {
  padding: 0;
}

/* 表单部分样式 */
.form-section {
  padding: 10px 15px;
  border-bottom: 1px solid #f0f4f8;
}

.form-section:last-child {
  border-bottom: none;
}

/* 表单组微调 */
.form-group {
  margin-bottom: 3px;
}

/* 表单标签微调 */
.form-label {
  margin-bottom: 6px;
  font-size: 0.95rem;
}

/* 激活状态的单选卡片样式 */

/* 激活状态的单选卡片样式 */
.radio-card.active {
  border-color: #003366;
  background-color: #f0f7ff;
  color: #003366;
}

/* 激活状态的单选卡片图标样式 */
.radio-card.active .radio-icon {
  color: #003366;
}

/* 文件上传文本样式 */
.upload-text p {
  margin: 0;
  color: #333;
}

/* 表单操作按钮样式 */
.form-actions {
  padding: 15px 20px;
  background: #ffffff;
  border-top: 1px solid #ffffff;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 模态框特有样式（覆盖共享样式） */
.modal-overlay {
  background-color: rgba(0, 0, 0, 0.7);
}

.modal-content {
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  width: 90vw;
  height: 90vh;
  max-width: 1200px;
  max-height: 800px;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f4f8;
}

.modal-header h3 {
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-body {
  flex: 1;
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

/* 规则说明区域样式 */
.rule-description {
  margin-top: 15px;
  padding: 15px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
}

.rule-description .form-label {
  font-weight: 600;
  margin-bottom: 8px;
  display: block;
  color: #495057;
}

.rule-description .description-content {
  font-size: 14px;
  line-height: 1.6;
  color: #6c757d;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .form-actions {
    flex-direction: column;
    padding: 12px 15px;
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
    .rule-description {
      margin-top: 12px;
      padding: 12px;
    }

    .rule-description .description-content {
      font-size: 13px;
    }

    padding: 30px 15px;
  }

  .file-preview h4 {
    font-size: 1.1rem;
  }
}
</style>