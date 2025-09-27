<template>
  <div class="page-content">
    <div class="page-title">
      <span>规则管理</span>
      <button class="btn" @click="showAddRuleModal = true">
        <font-awesome-icon :icon="['fas', 'plus']" /> 添加规则
      </button>
    </div>

    <!-- 筛选区域 -->
    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">规则类型:</span>
        <select v-model="filters.type">
          <option value="all">全部</option>
          <option value="academic">学术专长</option>
          <option value="comprehensive">综合表现</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">状态:</span>
        <select v-model="filters.status">
          <option value="all">全部</option>
          <option value="active">启用</option>
          <option value="disabled">禁用</option>
        </select>
      </div>
      <button class="btn" @click="searchRules">搜索</button>
    </div>

    <!-- 规则表格 -->
    <div class="card">
      <div class="table-container">
        <table class="application-table">
          <thead>
            <tr>
              <th>规则名称</th>
              <th>类型</th>
              <th>级别</th>
              <th>分值</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rule in filteredRules" :key="rule.id">
              <td>{{ rule.name }}</td>
              <td>{{ getTypeText(rule.type) }}</td>
              <td>{{ rule.level }}</td>
              <td>{{ rule.score }}</td>
              <td>
                <span :class="`status-badge status-${rule.status === 'active' ? 'approved' : 'rejected'}`">
                  {{ rule.status === 'active' ? '启用' : '禁用' }}
                </span>
              </td>
              <td>{{ formatDate(rule.createdAt) }}</td>
              <td>
                <button class="btn-outline btn small-btn" @click="editRule(rule)">
                  <font-awesome-icon :icon="['fas', 'edit']" />
                </button>
                <button v-if="rule.status === 'active'" 
                        class="btn-outline btn small-btn" 
                        @click="toggleRuleStatus(rule.id, 'disabled')">
                  <font-awesome-icon :icon="['fas', 'ban']" />
                </button>
                <button v-else 
                        class="btn-outline btn small-btn" 
                        @click="toggleRuleStatus(rule.id, 'active')">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </button>
              </td>
            </tr>
            <tr v-if="filteredRules.length === 0">
              <td colspan="7" class="no-data">暂无规则数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 分页控件 -->
    <div class="pagination">
      <div>显示 {{ startIndex + 1 }}-{{ endIndex }} 条，共 {{ totalRules }} 条记录</div>
      <div class="pagination-controls">
        <button class="btn-outline btn" :disabled="currentPage === 1" @click="prevPage">
          <font-awesome-icon :icon="['fas', 'chevron-left']" /> 上一页
        </button>
        <button class="btn-outline btn" :disabled="currentPage >= totalPages" @click="nextPage">
          下一页 <font-awesome-icon :icon="['fas', 'chevron-right']" />
        </button>
      </div>
    </div>

    <!-- 添加/编辑规则模态框 -->
    <div v-if="showAddRuleModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingRule ? '编辑规则' : '添加规则' }}</h3>
          <button class="close-btn" @click="closeModal">
            <font-awesome-icon :icon="['fas', 'times']" />
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveRule">
            <div class="form-group">
              <label class="form-label">规则名称</label>
              <input type="text" class="form-control" v-model="ruleForm.name" required>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">规则类型</label>
                <select class="form-control" v-model="ruleForm.type" required>
                  <option value="academic">学术专长</option>
                  <option value="comprehensive">综合表现</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">级别</label>
                <input type="text" class="form-control" v-model="ruleForm.level" required>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">分值</label>
                <input type="number" class="form-control" v-model="ruleForm.score" 
                       step="0.1" min="0" max="10" required>
              </div>
              <div class="form-group">
                <label class="form-label">状态</label>
                <select class="form-control" v-model="ruleForm.status" required>
                  <option value="active">启用</option>
                  <option value="disabled">禁用</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">规则描述</label>
              <textarea class="form-control" v-model="ruleForm.description" 
                        rows="3" placeholder="请输入规则详细描述"></textarea>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="closeModal">取消</button>
              <button type="submit" class="btn">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

const showAddRuleModal = ref(false)
const editingRule = ref(null)
const currentPage = ref(1)
const pageSize = 10

const filters = reactive({
  type: 'all',
  status: 'all'
})

const ruleForm = reactive({
  name: '',
  type: 'academic',
  level: '',
  score: 0,
  status: 'active',
  description: ''
})

// 模拟规则数据
const rules = ref([
  {
    id: 1,
    name: 'SCI论文A区',
    type: 'academic',
    level: 'A+',
    score: 5.0,
    status: 'active',
    description: '在SCI A区期刊发表论文',
    createdAt: '2023-01-15T00:00:00Z'
  },
  {
    id: 2,
    name: '国家级竞赛一等奖',
    type: 'academic',
    level: '国家级',
    score: 4.0,
    status: 'active',
    description: '获得国家级竞赛一等奖',
    createdAt: '2023-01-15T00:00:00Z'
  },
  {
    id: 3,
    name: '优秀志愿者',
    type: 'comprehensive',
    level: '省级',
    score: 2.0,
    status: 'disabled',
    description: '获得省级优秀志愿者称号',
    createdAt: '2023-02-20T00:00:00Z'
  }
])

// 计算属性
const filteredRules = computed(() => {
  let filtered = rules.value.filter(rule => {
    const typeMatch = filters.type === 'all' || rule.type === filters.type
    const statusMatch = filters.status === 'all' || rule.status === filters.status
    
    return typeMatch && statusMatch
  })
  
  return filtered
})

const totalRules = computed(() => filteredRules.value.length)
const totalPages = computed(() => Math.ceil(totalRules.value / pageSize))
const startIndex = computed(() => (currentPage.value - 1) * pageSize)
const endIndex = computed(() => Math.min(startIndex.value + pageSize, totalRules.value))

const paginatedRules = computed(() => {
  return filteredRules.value.slice(startIndex.value, endIndex.value)
})

// 方法
const getTypeText = (type) => {
  return type === 'academic' ? '学术专长' : '综合表现'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const searchRules = () => {
  currentPage.value = 1
}

const editRule = (rule) => {
  editingRule.value = rule
  Object.assign(ruleForm, rule)
  showAddRuleModal.value = true
}

const saveRule = () => {
  if (editingRule.value) {
    // 更新规则
    const index = rules.value.findIndex(r => r.id === editingRule.value.id)
    if (index !== -1) {
      rules.value[index] = { ...ruleForm, id: editingRule.value.id }
    }
  } else {
    // 添加新规则
    const newRule = {
      id: Math.max(...rules.value.map(r => r.id)) + 1,
      ...ruleForm,
      createdAt: new Date().toISOString()
    }
    rules.value.push(newRule)
  }
  
  closeModal()
  alert('规则保存成功')
}

const toggleRuleStatus = (ruleId, status) => {
  const rule = rules.value.find(r => r.id === ruleId)
  if (rule) {
    rule.status = status
    alert(`规则已${status === 'active' ? '启用' : '禁用'}`)
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const closeModal = () => {
  showAddRuleModal.value = false
  editingRule.value = null
  Object.assign(ruleForm, {
    name: '',
    type: 'academic',
    level: '',
    score: 0,
    status: 'active',
    description: ''
  })
}

// 生命周期
onMounted(() => {
  // 可以从API加载规则数据
})
</script>

<style scoped>
/* 样式与UserManagement.vue类似，已省略重复部分 */
</style>