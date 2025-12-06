<template>
  <div v-if="visible" class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ editingRule ? '编辑规则' : '添加规则' }}</h3>
        <button class="close-btn" @click="$emit('close')">
          <font-awesome-icon :icon="['fas', 'times']" />
        </button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="handleSave">
          <!-- 两列布局容器 -->
          <div class="form-layout">
            <!-- 左侧容器：基本信息、规则配置、规则说明 -->
            <div class="form-layout-left">
              <!-- 基本信息卡片 -->
              <div class="card">
                <div class="card-title">基本信息</div>
                <div class="card-body">
                  <div class="form-group">
                    <label class="form-label">规则名称</label>
                    <input type="text" class="form-control" v-model="ruleForm.name" required>
                  </div>

                  <!-- 规则类型（卡片式选择） -->
                  <div class="form-group">
                    <label class="form-label">规则类型</label>
                    <div class="radio-cards compact">
                      <div class="radio-card" :class="{ active: ruleForm.type === 'academic' }"
                        @click.stop="handleTypeChange('academic')">
                        <div class="radio-icon">
                          <font-awesome-icon :icon="['fas', 'book']" />
                        </div>
                        <span>学术专长</span>
                      </div>
                      <div class="radio-card" :class="{ active: ruleForm.type === 'comprehensive' }"
                        @click.stop="handleTypeChange('comprehensive')">
                        <div class="radio-icon">
                          <font-awesome-icon :icon="['fas', 'trophy']" />
                        </div>
                        <span>综合表现</span>
                      </div>
                    </div>
                  </div>

                  <!-- 规则子类型（卡片式选择） -->
                  <div class="form-group" v-if="ruleForm.type">
                    <label class="form-label">具体类型</label>
                    <div class="radio-cards">
                      <div class="radio-card" v-for="type in currentSubTypes" :key="type.value"
                        :class="{ active: ruleForm.sub_type === type.value }"
                        @click.stop="ruleForm.sub_type = type.value; handleSubTypeChange()">
                        <div class="radio-icon">
                          <font-awesome-icon :icon="type.icon" />
                        </div>
                        <span>{{ type.label }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- 科研成果类型选择（只有科研成果需要） -->
                  <div class="form-group" v-if="ruleForm.type === 'academic' && ruleForm.sub_type === 'research'">
                    <label class="form-label">科研成果种类</label>
                    <div class="radio-cards compact">
                      <div class="radio-card small" :class="{ active: ruleForm.research_type === 'paper' }"
                        @click.stop="ruleForm.research_type = 'paper'">
                        <div class="radio-icon">
                          <font-awesome-icon :icon="['fas', 'file-alt']" />
                        </div>
                        <span>学术论文</span>
                      </div>
                      <div class="radio-card small" :class="{ active: ruleForm.research_type === 'patent' }"
                        @click.stop="ruleForm.research_type = 'patent'">
                        <div class="radio-icon">
                          <font-awesome-icon :icon="['fas', 'file-invoice']" />
                        </div>
                        <span>发明专利</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 规则配置卡片 -->
              <div class="card">
                <div class="card-title">规则配置</div>
                <div class="card-body">

                  <div class="form-row">
                    <!-- 最大分数限制（可选） -->
                    <div class="form-group">
                      <label class="form-label">最高分数</label>
                      <input type="number" class="form-control" v-model="ruleForm.max_score" step="0.1" min="0"
                        placeholder="请输入最大分数限制（留空表示无限制）">
                    </div>

                    <!-- 最大项目数量限制（可选） -->
                    <div class="form-group">
                      <label class="form-label">最多项目数</label>
                      <input type="number" class="form-control" v-model="ruleForm.max_count" min="1"
                        placeholder="请输入最大项目数量（留空表示无限制）">
                    </div>
                  </div>

                  <div class="form-row">
                    <div class="form-group">
                      <label class="form-label">学院</label>
                      <select class="form-control" v-model="ruleForm.faculty_id">
                        <option value="">全部学院</option>
                        <option v-for="faculty in faculties" :key="faculty.id" :value="faculty.id">{{ faculty.name }}
                        </option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label class="form-label">默认分数</label>
                      <input type="number" class="form-control" v-model="ruleForm.score" step="0.1" min="0" max="30"
                        required>
                      <div class="help-text">当计分方式无法计算时，系统将使用此分数</div>
                    </div>
                    <div class="form-group">
                      <label class="form-label">状态</label>
                      <select class="form-control" v-model="ruleForm.status" required>
                        <option value="active">启用</option>
                        <option value="disabled">禁用</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
              <!-- 规则说明卡片 -->
              <div class="card">
                <div class="card-title">规则说明</div>
                <div class="card-body">
                  <div class="form-group">
                    <textarea class="form-control" v-model="ruleForm.description" rows="3"
                      placeholder="请输入规则详细描述"></textarea>
                  </div>
                </div>
              </div>
            </div>

            <!-- 右侧容器：计算规则 -->
            <div class="form-layout-right">
              <!-- 计算规则卡片 -->
              <div class="card">
                <div class="card-title">计算规则</div>
                <div class="card-body">

                  <!-- 计分方式设置 -->
                  <div class="json-formula-config">
                    <div class="form-group">
                      <label class="form-label">计分方式</label>
                      <div class="radio-cards">

                        <div class="radio-card horizontal"
                          :class="{ active: jsonFormulaConfig.type === 'multiplicative' }"
                          @click="jsonFormulaConfig.type = 'multiplicative'">
                          <div class="radio-icon">
                            <font-awesome-icon :icon="['fas', 'times']" />
                          </div>
                          <span>乘积式计算</span>
                        </div>

                        <div class="radio-card horizontal" :class="{ active: jsonFormulaConfig.type === 'cumulative' }"
                          @click="jsonFormulaConfig.type = 'cumulative'">
                          <div class="radio-icon">
                            <font-awesome-icon :icon="['fas', 'chart-line']" />
                          </div>
                          <span>累积式计算</span>
                        </div>
                      </div>
                    </div>

                    <!-- 乘积式计算配置 -->
                    <div v-if="jsonFormulaConfig.type === 'multiplicative'" class="multiplicative-config">
                      <div class="help-text">
                        乘积式计算将基础分数与多个系数相乘得到最终分数，适用于竞赛、论文等需要考虑多种因素的评分场景。
                        <br>计算方式：最终分数 = 基础分数 × 系数1 × 系数2 × ... × 系数n
                      </div>

                      <!-- 动态系数类型列表 -->
                      <div v-for="(coefficient, coefIndex) in jsonFormulaConfig.coefficients" :key="coefIndex"
                        class="coefficient-type-group">
                        <!-- 删除按钮 - 右上角 -->
                        <button type="button" class="btn btn-outline delete-btn"
                          @click="removeCoefficientType(coefIndex)" title="删除系数类型"
                          :disabled="jsonFormulaConfig.coefficients.length <= 1">
                          <font-awesome-icon icon="times" />
                        </button>

                        <div class="form-group">
                          <label class="form-label">系数类型</label>
                          <input type="text" class="form-control" v-model="coefficient.name" placeholder="请输入系数类型名称">
                        </div>

                        <div class="help-text small">设置不同{{ coefficient.name }}对应的系数值</div>

                        <!-- 系数项列表 -->
                        <div v-for="(item, itemIndex) in coefficient.items" :key="itemIndex" class="grade-config-item">
                          <div class="form-row coefficient-row">
                            <div class="form-group">
                              <label class="form-label">名称</label>
                              <input type="text" class="form-control" v-model="item.name"
                                :placeholder="`如：${coefficient.name === '等级系数' ? '一等奖、二等奖' : coefficient.name === '团队角色系数' ? '组长、核心成员' : '选项1、选项2'}`">
                            </div>
                            <div class="form-group">
                              <label class="form-label">系数值</label>
                              <input type="number" class="form-control" v-model="item.multiplier" step="0.1"
                                placeholder="如：2.0、1.5">
                            </div>
                            <div class="form-group">
                              <button type="button" class="btn btn-outline"
                                @click="removeCoefficientItem(coefIndex, itemIndex)" title="删除该项">
                                <font-awesome-icon icon="times" />
                              </button>
                            </div>
                          </div>
                        </div>

                        <!-- 添加系数项按钮 -->
                        <button type="button" @click="addCoefficientItem(coefIndex)"
                          class="btn btn-outline btn-icon-only btn-add-option" title="添加系数选项">
                          <font-awesome-icon icon="plus-circle" />
                        </button>
                      </div>

                      <!-- 添加系数类型按钮 -->
                      <button type="button" @click="addCoefficientType()"
                        class="btn btn-primary btn-icon-only btn-add-coefficient" title="添加新系数类型">
                        <font-awesome-icon icon="plus-square" />
                      </button>
                    </div>

                    <!-- 累积式计算配置 -->
                    <div v-if="jsonFormulaConfig.type === 'cumulative'" class="form-group">
                      <label class="form-label">累积计算配置</label>
                      <div class="help-text">
                        累积式计算根据累积字段值乘以系数计算得分，适用于志愿服务小时数等场景。
                        <br>计算方式：最终分数 = 累积字段值 × 系数
                      </div>
                      <div class="form-row">
                        <div class="form-group">
                          <label class="form-label">累积字段</label>
                          <input type="text" class="form-control" v-model="jsonFormulaConfig.cumulative_field"
                            placeholder="如：volunteer_hours">
                          <div class="help-text small">要累积计算的字段名称</div>
                        </div>
                        <div class="form-group">
                          <label class="form-label">累积乘数</label>
                          <input type="number" class="form-control" v-model="jsonFormulaConfig.cumulative_multiplier"
                            step="0.1" placeholder="如：0.1">
                          <div class="help-text small">每个单位累积值对应的分数</div>
                        </div>
                      </div>
                      <div class="form-row">
                        <div class="form-group">
                          <label class="form-label">最小分数</label>
                          <input type="number" class="form-control" v-model="jsonFormulaConfig.min_score" step="0.1">
                          <div class="help-text small">计算结果的最小分数限制</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-outline" @click="$emit('close')">取消</button>
            <button type="submit" class="btn">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch } from 'vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

// 属性
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  editingRule: {
    type: Object,
    default: null
  },

  faculties: {
    type: Array,
    default: () => []
  },
  allRules: {
    type: Array,
    default: () => []
  }
})

// 事件
const emit = defineEmits(['close', 'save'])

// 表单数据
const ruleForm = reactive({
  name: '',
  type: '',
  sub_type: '',
  research_type: '',
  max_score: null,
  max_count: null,
  faculty_id: '',
  score: 0,

  calculation_formula: null,
  status: 'active',
  description: ''
})

// 公式配置 - 支持多种计算类型
const jsonFormulaConfig = reactive({
  type: 'multiplicative',
  coefficients: [
    { name: '等级系数', key: 'award_grades', items: [] },
    { name: '团队角色系数', key: 'team_roles', items: [] }
  ],
  cumulative_field: '',
  cumulative_multiplier: 0.1,
  min_score: null
})

// JSON公式配置方法

// 添加系数类型
function addCoefficientType() {
  const typeCount = jsonFormulaConfig.coefficients.length + 1
  jsonFormulaConfig.coefficients.push({
    name: `自定义系数${typeCount}`,
    key: `custom_coef${typeCount}`,
    items: []
  })
}

// 移除系数类型
function removeCoefficientType(index) {
  if (jsonFormulaConfig.coefficients.length > 1) {
    jsonFormulaConfig.coefficients.splice(index, 1)
  }
}

// 更新系数类型名称
function updateCoefficientTypeName(index, newName) {
  if (newName.trim()) {
    jsonFormulaConfig.coefficients[index].name = newName.trim()
  }
}

// 添加系数项
function addCoefficientItem(coefIndex) {
  jsonFormulaConfig.coefficients[coefIndex].items.push({ name: '', multiplier: 1.0 })
}

// 移除系数项
function removeCoefficientItem(coefIndex, itemIndex) {
  jsonFormulaConfig.coefficients[coefIndex].items.splice(itemIndex, 1)
}

// 监听编辑规则的变化
watch(() => props.editingRule, (newRule) => {
  if (newRule) {
    // 分配基本规则数据
    Object.assign(ruleForm, newRule)

    // 处理计算设置
    if (newRule.calculation) {
      // 设置计算类型，支持json_formula、multiplicative和cumulative
      jsonFormulaConfig.type = newRule.calculation.calculation_type || 'multiplicative'

      // 从计算参数中复制配置
      if (newRule.calculation.parameters) {
        // 检查是否有动态系数配置
        if (newRule.calculation.parameters.coefficients) {
          jsonFormulaConfig.coefficients = newRule.calculation.parameters.coefficients
        } else {
          // 兼容旧的配置结构
          jsonFormulaConfig.coefficients = []
          if (newRule.calculation.parameters.award_grades) {
            jsonFormulaConfig.coefficients.push({
              name: '等级系数',
              key: 'award_grades',
              items: newRule.calculation.parameters.award_grades
            })
          }
          if (newRule.calculation.parameters.team_roles) {
            jsonFormulaConfig.coefficients.push({
              name: '团队角色系数',
              key: 'team_roles',
              items: newRule.calculation.parameters.team_roles
            })
          }
          // 如果没有任何系数配置，添加默认配置
          if (jsonFormulaConfig.coefficients.length === 0) {
            jsonFormulaConfig.coefficients.push(
              { name: '等级系数', key: 'award_grades', items: [] },
              { name: '团队角色系数', key: 'team_roles', items: [] }
            )
          }
        }

        // 设置其他配置项
        jsonFormulaConfig.cumulative_field = newRule.calculation.parameters.cumulative_field || ''
        jsonFormulaConfig.cumulative_multiplier = newRule.calculation.parameters.cumulative_multiplier || 0.1
        jsonFormulaConfig.min_score = newRule.calculation.parameters.min_score
      }

      // 如果存在，从计算参数设置最大分数和最大数量
      if (newRule.calculation.parameters?.max_score) {
        ruleForm.max_score = newRule.calculation.parameters.max_score
      }
      if (newRule.calculation.parameters?.max_count) {
        ruleForm.max_count = newRule.calculation.parameters.max_count
      }
    } else {
      // 默认JSON公式配置
      jsonFormulaConfig.type = 'multiplicative'
      jsonFormulaConfig.coefficients = [
        { name: '等级系数', key: 'award_grades', items: [] },
        { name: '团队角色系数', key: 'team_roles', items: [] }
      ]
      jsonFormulaConfig.cumulative_field = ''
      jsonFormulaConfig.cumulative_multiplier = 0.1
      jsonFormulaConfig.min_score = null
    }
  } else {
    // 重置表单
    Object.assign(ruleForm, {
      name: '',
      type: '',
      sub_type: '',
      research_type: '',
      max_score: null,
      max_count: null,
      faculty_id: '',
      score: 0,
      calculation_formula: null,
      status: 'active',
      description: ''
    })

    // 重置公式配置
    Object.assign(jsonFormulaConfig, {
      type: 'multiplicative',
      coefficients: [
        { name: '等级系数', key: 'award_grades', items: [] },
        { name: '团队角色系数', key: 'team_roles', items: [] }
      ],
      cumulative_field: '',
      cumulative_multiplier: 0.1,
      min_score: null
    })
  }
}, { immediate: true })

// 监听visible属性的变化
watch(() => props.visible, (newVisible) => {
  if (!newVisible) {
    // 当模态框关闭时重置表单
  }
})

// 根据所选类型的规则子类型
const currentSubTypes = computed(() => {
  if (ruleForm.type === 'academic') {
    return [
      { value: 'competition', label: '学术竞赛', icon: ['fas', 'trophy'] },
      { value: 'research', label: '科研成果', icon: ['fas', 'microscope'] },
      { value: 'innovation', label: '创新创业', icon: ['fas', 'lightbulb'] }
    ]
  } else if (ruleForm.type === 'comprehensive') {
    return [
      { value: 'volunteer', label: '志愿服务', icon: ['fas', 'hand-holding-heart'] },
      { value: 'sports', label: '体育竞赛', icon: ['fas', 'futbol'] },
      { value: 'international_internship', label: '国际组织实习', icon: ['fas', 'globe'] },
      { value: 'military_service', label: '参军入伍', icon: ['fas', 'shield'] },
      { value: 'honor_title', label: '荣誉称号', icon: ['fas', 'medal'] },
      { value: 'social_work', label: '社会工作', icon: ['fas', 'users-cog'] }
    ]
  }
  return []
})

// 处理类型变化
const handleTypeChange = (type) => {
  ruleForm.type = type
  ruleForm.sub_type = ''
  ruleForm.research_type = ''
  // 重置其他类型特定字段
}

// 处理子类型变化
const handleSubTypeChange = () => {
  if (ruleForm.sub_type !== 'research') {
    ruleForm.research_type = ''
  }
  // 重置其他子类型特定字段
}

// 为后端准备计算数据 - 支持多种计算类型
const prepareCalculationData = () => {
  // 根据选择的计算类型准备参数
  let params = {
    base_score: ruleForm.score,
    max_count: ruleForm.max_count
  }

  // 乘积式计算配置
  if (jsonFormulaConfig.type === 'multiplicative') {
    // 保存完整的系数配置，包括类型和具体系数项
    params.coefficients = jsonFormulaConfig.coefficients
  }
  // 累积式计算配置
  else if (jsonFormulaConfig.type === 'cumulative') {
    // 使用用户配置的累积字段和乘数
    params.cumulative_field = jsonFormulaConfig.cumulative_field || 'value'
    params.multiplier = jsonFormulaConfig.cumulative_multiplier || 1.0
  }

  return {
    calculation_type: jsonFormulaConfig.type, // 使用正确的计算类型（multiplicative或cumulative）
    formula: null,
    parameters: params,
    max_score: ruleForm.max_score
  }
}

// 处理表单提交
const handleSave = () => {
  // 准备规则数据
  const ruleData = {
    ...ruleForm,
    // 将空字符串转换为null（对于可能为null的字段）
    faculty_id: ruleForm.faculty_id === '' ? null : ruleForm.faculty_id,
    research_type: ruleForm.research_type === '' ? null : ruleForm.research_type,
    // 添加嵌套字段
    calculation: prepareCalculationData()
  }

  // 对于非科研类型，清空科研类型字段
  if (!(ruleData.type === 'academic' && ruleData.sub_type === 'research')) {
    ruleData.research_type = null
  }

  // 发送保存事件并携带规则数据
  emit('save', ruleData)
}
</script>

<style scoped>
/* Modal styles */
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
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 1200px;
  max-height: 85vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
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
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background-color: #f1f1f1;
  color: #333;
}

.modal-body {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

/* Form layout */
.form-layout {
  display: flex;
  gap: 25px;
  margin-bottom: 20px;
}

.form-layout-left {
  flex: 1;
}

.form-layout-right {
  flex: 1;
}

/* Component specific form styles */
.form-layout-left .form-row,
.form-layout-right :not(.json-formula-config) .form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  align-items: flex-start;
}

.form-layout-left .form-row .form-group,
.form-layout-right :not(.json-formula-config) .form-row .form-group {
  flex: 1;
  margin-bottom: 0;
}

/* Formula Configuration */
.json-formula-config {
  margin-top: 15px;
}

.multiplicative-config {
  margin-top: 15px;
}

/* Coefficient configuration */
.coefficient-type-group {
  position: relative;
  background-color: #f9f9f9;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 20px;
}

.grade-config-item {
  margin-bottom: 15px;
  padding: 10px;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 4px;
}

/* Coefficient row layout */
.multiplicative-config .grade-config-item {
  margin-bottom: 10px;
}

.multiplicative-config .grade-config-item .coefficient-row {
  display: flex;
  align-items: center;
  gap: 15px;
  width: 100%;
  margin-bottom: 0px;
}

.multiplicative-config .grade-config-item .coefficient-row .form-group {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
  flex: 1;
  margin-bottom: 0;
}

.multiplicative-config .grade-config-item .coefficient-row .form-group .form-label {
  display: inline-block;
  white-space: nowrap;
  min-width: 30px;
  margin-bottom: 0;
  font-weight: 500;
  color: #555;
}

.multiplicative-config .grade-config-item .coefficient-row .form-group .form-control {
  flex: 1;
}

/* Delete button */
.delete-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  margin: 0;
  padding: 4px 8px;
  font-size: 12px;
  height: auto;
  width: auto;
}

.multiplicative-config .grade-config-item .coefficient-row .form-group:last-child {
  flex: none;
  width: auto;
  margin-left: auto;
}

/* Custom buttons */
.btn-add-option {
  background-color: transparent;
  border: 1px dashed #003366;
  color: #003366;
  margin-top: 10px;
  padding: 10px;
  width: 100%;
  height: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.btn-add-option:hover {
  background-color: rgba(0, 51, 102, 0.05);
  border-style: solid;
  border-color: #00254a;
}

.btn-add-coefficient {
  background-color: #fbfdff;
  border: 2px dashed #003366;
  color: #003366;
  margin-top: 15px;
  padding: 12px;
  width: 100%;
  height: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s ease;
}

.btn-add-coefficient:hover {
  background-color: #eef8ff;
  border-style: solid;
  border-color: #003366;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

/* Responsive Design */
@media (max-width: 992px) {
  .form-layout {
    flex-direction: column;
    gap: 20px;
  }

  .form-layout-left,
  .form-layout-right {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    margin: 10px;
  }

  .form-row {
    flex-direction: column;
    gap: 15px;
  }

  .form-row .form-group {
    width: 100%;
  }

  .radio-card {
    min-width: calc(50% - 8px);
  }

  .radio-card.horizontal {
    min-width: 120px;
  }

  .form-actions {
    flex-wrap: wrap;
  }

  .form-actions .btn {
    flex: 1;
    min-width: 120px;
  }
}

@media (max-width: 576px) {
  .modal-header {
    padding: 15px;
  }

  .modal-body {
    padding: 15px;
  }

  .radio-card {
    min-width: 100%;
  }

  .coefficient-type-group {
    padding: 12px;
  }
}
</style>