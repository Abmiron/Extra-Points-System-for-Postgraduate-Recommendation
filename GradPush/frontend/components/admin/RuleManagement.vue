<template>
  <div class="page-content">
    <div class="page-title">
      <span>规则管理</span>
      <div class="page-title-actions">
        <button class="btn btn-outline" @click="openAddRuleModal">
          <font-awesome-icon :icon="['fas', 'plus']" /> 添加规则
        </button>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">规则名称:</span>
        <input type="text" class="form-control" v-model="filters.name" placeholder="请输入规则名称">
      </div>
      <div class="filter-group">
        <span class="filter-label">规则类型:</span>
        <select class="form-control" v-model="filters.type" @change="handleFilterTypeChange">
          <option value="all">全部</option>
          <option value="academic">学术专长</option>
          <option value="comprehensive">综合表现</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">子类型:</span>
        <select class="form-control" v-model="filters.subType">
          <option value="all">全部</option>
          <!-- 学术专长子类型 -->
          <template v-if="filters.type === 'academic' || filters.type === 'all'">
            <option value="competition">学业竞赛</option>
            <option value="research">科研成果</option>
            <option value="innovation">创新创业训练</option>
          </template>
          <!-- 综合表现子类型 -->
          <template v-if="filters.type === 'comprehensive' || filters.type === 'all'">
            <option value="international_internship">国际组织实习</option>
            <option value="military_service">参军入伍服兵役</option>
            <option value="volunteer">志愿服务</option>
            <option value="social_work">社会工作</option>
            <option value="sports">体育比赛</option>
            <option value="honor_title">荣誉称号</option>
          </template>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">状态:</span>
        <select class="form-control" v-model="filters.status">
          <option value="all">全部</option>
          <option value="active">启用</option>
          <option value="disabled">禁用</option>
        </select>
      </div>
      <button class="btn btn-outline" @click="resetFilters">清空筛选</button>
    </div>

    <!-- 规则表格 -->
    <div class="card">
      <div class="table-container">
        <!-- 加载状态指示器 -->
        <div v-if="loading" class="loading-overlay">
          <div class="loading-spinner"></div>
          <div class="loading-text">加载中...</div>
        </div>
        <table class="application-table">
          <thead>
              <tr>
                <th>规则名称</th>
                <th>类型</th>
                <th>子类型</th>
                <th>级别</th>
                <th>等级</th>
                <th>基础分值</th>
                <th>作者排序比例</th>
                <th>最大分数</th>
                <th>最大数量</th>
                <th>规则类型</th>
                <th>状态</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
          <tbody>
            <tr v-for="rule in paginatedRules" :key="rule.id">
              <td>{{ rule.name }}</td>
              <td>{{ getTypeText(rule.type) }}</td>
              <td>{{ getSubTypeText(rule.sub_type) }}</td>
              <td>{{ getLevelText(rule.level) }}</td>
              <td>{{ getGradeText(rule.grade) }}</td>
              <td>{{ rule.score }}</td>
              <td>{{ rule.author_rank_ratio ? (rule.author_rank_ratio * 100).toFixed(0) + '%' : '-' }}</td>
              <td>{{ rule.max_score || '-' }}</td>
              <td>{{ rule.max_count || '-' }}</td>
              <td>
                <span :class="`status-badge status-${rule.is_special ? 'special' : 'normal'}`">
                  {{ rule.is_special ? '特殊' : '普通' }}
                </span>
              </td>
              <td>
                <span :class="`status-badge status-${rule.status === 'active' ? 'approved' : 'rejected'}`">
                  {{ rule.status === 'active' ? '启用' : '禁用' }}
                </span>
              </td>
              <td>{{ formatDate(rule.createdAt) }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn-outline btn small-btn" @click="editRule(rule)" title="编辑">
                    <font-awesome-icon :icon="['fas', 'edit']" />
                  </button>
                  <button v-if="rule.status === 'active'" class="btn-outline btn small-btn"
                    @click="toggleRuleStatus(rule.id, 'disabled')" title="禁用">
                    <font-awesome-icon :icon="['fas', 'ban']" />
                  </button>
                  <button v-else class="btn-outline btn small-btn" @click="toggleRuleStatus(rule.id, 'active')"
                    title="启用">
                    <font-awesome-icon :icon="['fas', 'check']" />
                  </button>
                  <button class="btn-outline btn small-btn delete-btn" @click="deleteRule(rule)" title="删除">
                    <font-awesome-icon :icon="['fas', 'trash-alt']" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="paginatedRules.length === 0">
              <td colspan="7" class="no-data">暂无规则数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 分页控件 -->
    <div class="pagination">
      <div class="pagination-info">显示 {{ startIndex + 1 }}-{{ endIndex }} 条，共 {{ totalRules }} 条记录</div>
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
            
            <!-- 规则类型（卡片式选择） -->
            <div class="form-group">
              <label class="form-label">规则类型</label>
              <div class="radio-cards compact">
                <div class="radio-card" :class="{ active: ruleForm.type === 'academic' }" @click.stop="handleTypeChange('academic')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'book']" />
                  </div>
                  <span>学术专长</span>
                </div>
                <div class="radio-card" :class="{ active: ruleForm.type === 'comprehensive' }" @click.stop="handleTypeChange('comprehensive')">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'trophy']" />
                  </div>
                  <span>综合表现</span>
                </div>
              </div>
            </div>
            
            <!-- 规则子类型（卡片式选择） -->
            <div class="form-group" v-if="ruleForm.type">
              <label class="form-label">规则子类型</label>
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
            
            <!-- 级别选择 -->
            <div class="form-group" v-if="!(ruleForm.type === 'academic' && (ruleForm.sub_type === 'research' || ruleForm.sub_type === 'innovation')) && currentLevels.length > 0">
              <label class="form-label">级别</label>
              <div class="radio-cards">
                <div class="radio-card" v-for="level in currentLevels" :key="level.value" 
                  :class="{ active: ruleForm.level === level.value }" 
                  @click.stop="ruleForm.level = level.value; handleLevelChange()">
                  <span>{{ level.label }}</span>
                </div>
                <div class="radio-card" v-if="currentLevels.length === 0" :class="{ disabled: true }">
                  <span>请先选择类型和子类型</span>
                </div>
              </div>
            </div>
            
            <!-- 等级选择（科研成果、创新创业训练和综合表现不需要） -->
            <div class="form-group" v-if="ruleForm.type === 'academic' && !(ruleForm.sub_type === 'research' || ruleForm.sub_type === 'innovation')">
              <label class="form-label">等级</label>
              <div class="radio-cards">
                <div class="radio-card" v-for="grade in currentGrades" :key="grade.value" 
                  :class="{ active: ruleForm.grade === grade.value, disabled: !ruleForm.level && currentLevels.length > 0 }" 
                  @click.stop="(currentLevels.length === 0 || ruleForm.level) && (ruleForm.grade = grade.value)">
                  <span>{{ grade.label }}</span>
                </div>
                <div class="radio-card" v-if="currentGrades.length === 0" :class="{ disabled: true }">
                  <span>{{ !ruleForm.level && currentLevels.length > 0 ? '请先选择级别' : '该类型无等级选项' }}</span>
                </div>
              </div>
            </div>
            
            <!-- 科研成果类型选择（只有科研成果需要） -->
            <div class="form-group" v-if="ruleForm.type === 'academic' && ruleForm.sub_type === 'research'">
              <label class="form-label">科研成果类型</label>
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
            
            <!-- 只有学业竞赛才显示奖项类别选择 -->
            <div class="form-group" v-if="ruleForm.type === 'academic' && ruleForm.sub_type === 'competition'">
              <label class="form-label">奖项类别</label>
              <div class="radio-cards">
                <div class="radio-card" v-for="category in currentCategories" :key="category" 
                  :class="{ active: ruleForm.category === category }" 
                  @click.stop="ruleForm.category = category">
                  <span>{{ category }}</span>
                </div>
                <div class="radio-card" v-if="currentCategories.length === 0" :class="{ disabled: true }">
                  <span>暂无奖项类别</span>
                </div>
              </div>
            </div>
            
            <!-- 参与类型选择（创新创业训练不需要） -->
            <div class="form-group" v-if="!(ruleForm.type === 'academic' && ruleForm.sub_type === 'innovation')">
              <label class="form-label">参与类型</label>
              <div class="radio-cards compact">
                <div class="radio-card small" :class="{ active: ruleForm.participation_type === 'individual' }" 
                  @click.stop="ruleForm.participation_type = 'individual'">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'user']" />
                  </div>
                  <span>个人</span>
                </div>
                <div class="radio-card small" :class="{ active: ruleForm.participation_type === 'team' }" 
                  @click.stop="ruleForm.participation_type = 'team'">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'users']" />
                  </div>
                  <span>集体</span>
                </div>
              </div>
            </div>
            
            <!-- 团队角色选择（综合表现且选择集体时，或创新创业训练时显示） -->
            <div class="form-group" v-if="(ruleForm.type === 'comprehensive' && ruleForm.participation_type === 'team') || (ruleForm.type === 'academic' && ruleForm.sub_type === 'innovation')">
              <label class="form-label">团队角色</label>
              <div class="radio-cards compact">
                <div class="radio-card small" :class="{ active: ruleForm.team_role === 'leader' }" 
                  @click.stop="ruleForm.team_role = 'leader'">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'flag']" />
                  </div>
                  <span>队长</span>
                </div>
                <div class="radio-card small" :class="{ active: ruleForm.team_role === 'member' }" 
                  @click.stop="ruleForm.team_role = 'member'">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'user-friends']" />
                  </div>
                  <span>队员</span>
                </div>
              </div>
            </div>
            
            <!-- 作者排序类型选择（只有集体参与且为学业竞赛时显示） -->
            <div class="form-group" v-if="ruleForm.type === 'academic' && ruleForm.sub_type === 'competition' && ruleForm.participation_type === 'team'">
              <label class="form-label">作者排序类型</label>
              <div class="radio-cards compact">
                <div class="radio-card small" :class="{ active: ruleForm.author_rank_type === 'ranked' }" 
                  @click.stop="ruleForm.author_rank_type = 'ranked'">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'sort-numeric-up']" />
                  </div>
                  <span>区分排名</span>
                </div>
                <div class="radio-card small" :class="{ active: ruleForm.author_rank_type === 'unranked' }" 
                  @click.stop="ruleForm.author_rank_type = 'unranked'">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'sort']" />
                  </div>
                  <span>不区分排名</span>
                </div>
              </div>
            </div>
            
            <!-- 作者排序输入（只有区分排名时显示） -->
            <div class="form-group" v-if="ruleForm.type === 'academic' && ruleForm.sub_type === 'competition' && ruleForm.participation_type === 'team' && ruleForm.author_rank_type === 'ranked'">
              <label class="form-label">作者排序</label>
              <input type="number" class="form-control" v-model="ruleForm.author_rank" min="1" placeholder="请输入作者排序（数字）">
            </div>
            
            <!-- 作者排序比例（科研成果和区分排名的学业竞赛显示） -->
            <div class="form-group" v-if="(ruleForm.type === 'academic' && (ruleForm.sub_type === 'research' || (ruleForm.sub_type === 'competition' && ruleForm.author_rank_type === 'ranked')))">
              <label class="form-label">作者排序比例 (%)</label>
              <input type="number" class="form-control" v-model="ruleForm.author_rank_ratio" min="0" max="100" step="1" placeholder="请输入比例（如80%填写80）">
            </div>
            
            <!-- 最大分数限制（可选） -->
            <div class="form-group">
              <label class="form-label">最大分数限制</label>
              <input type="number" class="form-control" v-model="ruleForm.max_score" step="0.1" min="0" placeholder="请输入最大分数限制（留空表示无限制）">
            </div>
            
            <!-- 最大项目数量限制（可选） -->
            <div class="form-group">
              <label class="form-label">最大项目数量限制</label>
              <input type="number" class="form-control" v-model="ruleForm.max_count" min="1" placeholder="请输入最大项目数量（留空表示无限制）">
            </div>
            
            <!-- 特殊规则标记 -->
            <div class="form-group">
              <label class="form-label">特殊规则</label>
              <div class="radio-cards compact">
                <div class="radio-card small" :class="{ active: ruleForm.is_special === true }" 
                  @click.stop="ruleForm.is_special = true">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'check']" />
                  </div>
                  <span>是</span>
                </div>
                <div class="radio-card small" :class="{ active: ruleForm.is_special === false }" 
                  @click.stop="ruleForm.is_special = false">
                  <div class="radio-icon">
                    <font-awesome-icon :icon="['fas', 'times']" />
                  </div>
                  <span>否</span>
                </div>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">分值</label>
                <input type="number" class="form-control" v-model="ruleForm.score" step="0.1" min="0" max="30" required>
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
              <textarea class="form-control" v-model="ruleForm.description" rows="3" placeholder="请输入规则详细描述"></textarea>
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import api from '../../utils/api'

const showAddRuleModal = ref(false)
const editingRule = ref(null)
const currentPage = ref(1)
const pageSize = 10
const loading = ref(false)

const filters = reactive({
  name: '',
  type: 'all',
  subType: 'all',
  status: 'all'
})

const ruleForm = reactive({
  name: '',
  type: 'academic',
  sub_type: '',
  level: '',
  grade: '',
  category: '',  // 奖项类别，用于学业竞赛
  research_type: '',  // 科研成果类型：学术论文/paper、发明专利/patent
  participation_type: 'individual',  // 参与类型：个人/集体
  team_role: '',  // 团队角色：队长/队员
  author_rank_type: 'unranked',  // 作者排序类型：区分排名/ranked、不区分排名/unranked
  author_rank: null,  // 作者排序：数字，仅当区分排名时填写
  author_rank_ratio: null,  // 作者排序比例：如80%填写0.8
  score: 0,  // 基础分值
  max_score: null,  // 最大分数限制
  max_count: null,  // 最大项目数量限制
  is_special: false,  // 是否为特殊规则
  status: 'active',
  description: ''
})

// 规则数据
const rules = ref([])

// 计算属性
const filteredRules = computed(() => {
  let filtered = rules.value.filter(rule => {
    const nameMatch = !filters.name || rule.name.includes(filters.name)
    const typeMatch = filters.type === 'all' || rule.type === filters.type
    const subTypeMatch = filters.subType === 'all' || rule.sub_type === filters.subType
    const statusMatch = filters.status === 'all' || rule.status === filters.status

    return nameMatch && typeMatch && subTypeMatch && statusMatch
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

const getSubTypeText = (subType) => {
  const subTypeMap = {
    // 学术专长
    'competition': '学业竞赛',
    'research': '科研成果',
    'innovation': '创新创业训练',
    // 综合表现
    'international_internship': '国际组织实习',
    'military_service': '参军入伍服兵役',
    'volunteer': '志愿服务',
    'social_work': '社会工作',
    'sports': '体育比赛',
    'honor_title': '荣誉称号'
  }
  return subTypeMap[subType] || '-'  // 如果找不到对应的子类型，显示'-'
}

// 获取级别文本
const getLevelText = (level) => {
  const levelMap = {
    'national': '国家级',
    'provincial': '省级',
    'university': '校级',
    'school': '校级',  // 与学生端保持一致，同时支持school和university
    'college': '院级',
    'department': '系级',
    'international': '国际级'
  }
  return levelMap[level] || '-'  // 如果找不到对应的级别，显示'-'
}

// 获取等级文本
const getGradeText = (grade) => {
  const gradeMap = {
    // 通用学术等级
    'special': '特等奖',
    'first': '一等奖',
    'second': '二等奖',
    'third': '三等奖',
    'firstOrHigher': '一等奖及以上',  // 与学生端保持一致
    'excellent': '优秀奖',
    'good': '良好',
    'general': '合格',
    'participation': '参与奖',
    
    // 国际组织实习
    'full_year': '满一学年',
    'half_year': '超过一学期不满一年',
    
    // 参军入伍服兵役
    '1-2_years': '1-2年',
    '2+_years': '2年以上',
    
    // 志愿服务
    'captain': '队长',
    'team_member': '队员',
    'individual': '个人',
    
    // 社会工作
    'executive_chair': '院学生会执行主席/团总支书记',
    'presidium_member': '院学生会主席团成员/团总支副书记',
    'department_head': '院学生会/团总支各部部长',
    'branch_secretary': '党支部书记',
    'monitor': '班长/团支部书记',
    'assistant_department_head': '系团总支书记/院学生会/团总支各部门副部长',
    'club_president': '社团社长',
    'committee_member': '党支部委员/系团总支各部部长/各班班委/团支部委员',
    'assistant_club_president': '院学生会/团总支长期志愿者/社团副社长及主要干部',
    
    // 体育比赛
    'champion': '冠军',
    'runner_up': '亚军',
    'third_place': '季军',
    'top_8': '第四至八名',
    
    // 荣誉称号
    'collective': '集体'
  }
  return gradeMap[grade] || '-'  // 如果找不到对应的等级，显示'-'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 加载规则数据
const loadRules = async () => {
  loading.value = true
  try {
    const response = await api.getRules(filters)
    rules.value = response.rules
  } catch (error) {
    console.error('加载规则失败:', error)
    alert('加载规则失败')
  } finally {
    loading.value = false
  }
}

// 处理筛选类型变化
const handleFilterTypeChange = () => {
  filters.subType = 'all' // 切换类型时重置子类型筛选
}

// 处理规则类型变化
const handleRuleTypeChange = () => {
  // 如果规则类型不是综合表现，清空团队角色
  if (ruleForm.type !== 'comprehensive') {
    ruleForm.team_role = ''
  }
  // 重置子类型
  ruleForm.sub_type = ''
  // 重置等级
  ruleForm.grade = ''
}

// 重置筛选条件
const resetFilters = () => {
  filters.name = ''
  filters.type = 'all'
  filters.subType = 'all'
  filters.status = 'all'
  currentPage.value = 1
}

// 监听筛选条件变化，自动搜索
watch(
  () => ({ ...filters }),
  () => {
    currentPage.value = 1
    loadRules()
  },
  { deep: true }
)

const editRule = (rule) => {
  editingRule.value = rule
  ruleForm.name = rule.name
  ruleForm.type = rule.type
  ruleForm.sub_type = rule.sub_type || ''
  ruleForm.level = rule.level
  ruleForm.grade = rule.grade || ''
  ruleForm.category = rule.category || '' // 设置奖项类别
  ruleForm.research_type = rule.research_type || '' // 设置科研成果类型
  ruleForm.participation_type = rule.participation_type || 'individual' // 设置参与类型
  ruleForm.team_role = rule.team_role || '' // 设置团队角色
  ruleForm.author_rank_type = rule.author_rank_type || 'unranked' // 设置作者排序类型
  ruleForm.author_rank = rule.author_rank || null // 设置作者排序
  ruleForm.author_rank_ratio = rule.author_rank_ratio ? rule.author_rank_ratio * 100 : null // 从数据库读取的是小数，转换为百分比显示
  ruleForm.score = rule.score
  ruleForm.max_score = rule.max_score || null
  ruleForm.max_count = rule.max_count || null
  ruleForm.is_special = rule.is_special || false
  ruleForm.status = rule.status
  ruleForm.description = rule.description || ''
  showAddRuleModal.value = true
}

const saveRule = async () => {
  try {
    // 表单验证
    if (!ruleForm.name || !ruleForm.type || !ruleForm.sub_type || !ruleForm.score) {
      // 检查级别字段是否必填
      const needLevel = ['volunteer', 'sports', 'honor_title', 'international_internship', 'military_service', 'social_work'] // 需要级别的综合表现子类型
      if ((ruleForm.type !== 'academic' || !(ruleForm.sub_type === 'research' || ruleForm.sub_type === 'innovation')) && 
          (ruleForm.type !== 'comprehensive' || needLevel.includes(ruleForm.sub_type)) && 
          !ruleForm.level) {
        alert('请填写必填字段')
        return
      }
    }
    
    // 检查等级字段是否必填
    // 综合表现类型不需要等级，只有学术类型需要等级（科研成果和创新创业训练除外）
    if (ruleForm.type !== 'comprehensive' && !(ruleForm.type === 'academic' && (ruleForm.sub_type === 'research' || ruleForm.sub_type === 'innovation')) && !ruleForm.grade) {
      alert('请选择等级')
      return
    }
    
    // 对于学业竞赛，奖项类别是必填的
    if (ruleForm.type === 'academic' && ruleForm.sub_type === 'competition' && !ruleForm.category) {
      alert('请选择奖项类别')
      return
    }
    
    // 对于科研成果，科研成果类型是必填的
    if (ruleForm.type === 'academic' && ruleForm.sub_type === 'research' && !ruleForm.research_type) {
      alert('请选择科研成果类型')
      return
    }
    
    // 对于综合表现类型，清空等级字段
    // 综合表现类型不需要等级，设置为空值（已在表单验证中处理）
    
    // 对于非学业竞赛类型，清空奖项类别字段
    if (!(ruleForm.type === 'academic' && ruleForm.sub_type === 'competition')) {
      ruleForm.category = ''
    }
    
    // 对于非科研成果类型，清空科研成果类型字段
    if (!(ruleForm.type === 'academic' && ruleForm.sub_type === 'research')) {
      ruleForm.research_type = ''
    }
    
    // 准备要发送的数据，处理作者排序比例
    const ruleData = { ...ruleForm }
    // 将百分比转换为小数
    if (ruleData.author_rank_ratio !== null) {
      ruleData.author_rank_ratio = parseFloat(ruleData.author_rank_ratio) / 100
    }
    
    // 处理可能的空值，确保与数据库字段类型匹配
    // 将空字符串转换为null
    for (const key in ruleData) {
      if (ruleData[key] === '') {
        ruleData[key] = null
      }
    }
    
    // 处理可能的空值，确保与数据库字段类型匹配
    if (ruleData.author_rank === null) {
      delete ruleData.author_rank
    }
    if (ruleData.max_score === null) {
      delete ruleData.max_score
    }
    if (ruleData.max_count === null) {
      delete ruleData.max_count
    }
    
    if (editingRule.value) {
      // 更新规则
      await api.updateRule(editingRule.value.id, ruleData)
      alert('规则更新成功')
    } else {
      // 添加新规则
      await api.createRule(ruleData)
      alert('规则添加成功')
    }

    closeModal()
    loadRules() // 重新加载规则数据
  } catch (error) {
    console.error('保存规则失败:', error)
    alert('保存规则失败')
  }
}

const toggleRuleStatus = async (ruleId) => {
  try {
    await api.toggleRuleStatus(ruleId)
    await loadRules() // 重新加载规则数据
  } catch (error) {
    console.error('切换规则状态失败:', error)
    alert('切换规则状态失败')
  }
}

const deleteRule = async (rule) => {
  if (confirm(`确定要删除规则「${rule.name}」吗？此操作不可撤销。`)) {
    try {
      await api.deleteRule(rule.id)
      await loadRules() // 重新加载规则数据
      // 如果当前页没有数据了，且不是第一页，则回到上一页
      if (paginatedRules.value.length === 0 && currentPage.value > 1) {
        currentPage.value--
      }
      alert('规则删除成功')
    } catch (error) {
      console.error('删除规则失败:', error)
      alert('删除规则失败')
    }
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

// 根据规则类型和子类型定义级别和等级选项，与学生端保持一致
const levelGradeOptions = {
  academic: {
    competition: {
      levels: ['national', 'provincial'],
      grades: {
        national: ['firstOrHigher', 'second', 'third'],
        provincial: ['firstOrHigher', 'second']
      },
      categories: ['A+', 'A', 'A-']  // 学业竞赛奖项类别
    },
    research: {
      levels: ['national', 'provincial', 'university'],
      grades: {
        national: ['first', 'second', 'third'],
        provincial: ['first', 'second', 'third'],
        university: ['first', 'second']
      }
    },
    innovation: {
      levels: ['national', 'provincial', 'school'],
      grades: {
        national: ['first', 'second', 'third'],
        provincial: ['first', 'second', 'third'],
        school: ['first', 'second']
      }
    }
  },
  comprehensive: {
    international_internship: {
      levels: ['provincial', 'school', 'college'],  // 国际组织实习级别
      grades: {
        provincial: ['full_year', 'half_year'],  // 省级：满一学年、超过一学期不满一年
        school: ['full_year', 'half_year'],  // 校级：满一学年、超过一学期不满一年
        college: ['full_year', 'half_year']  // 院级：满一学年、超过一学期不满一年
      }
    },
    military_service: {
      levels: ['provincial', 'school', 'college'],  // 参军入伍服兵役级别
      grades: {
        provincial: ['1-2_years', '2+_years'],  // 省级：1-2年、2年以上
        school: ['1-2_years', '2+_years'],  // 校级：1-2年、2年以上
        college: ['1-2_years', '2+_years']  // 院级：1-2年、2年以上
      }
    },
    volunteer: {
      levels: ['provincial', 'school', 'college'],  // 志愿服务表彰级别
      grades: {
        provincial: ['captain', 'team_member', 'individual'],  // 省级：队长、队员、个人
        school: ['captain', 'team_member', 'individual'],  // 校级：队长、队员、个人
        college: ['captain', 'team_member', 'individual']  // 院级：队长、队员、个人
      }
    },
    social_work: {
      levels: ['provincial', 'school', 'college'],  // 社会工作级别
      grades: {
        provincial: ['executive_chair', 'presidium_member', 'department_head', 'branch_secretary', 'monitor', 
             'assistant_department_head', 'club_president', 'committee_member', 'assistant_club_president'],  // 省级：各类职务
        school: ['executive_chair', 'presidium_member', 'department_head', 'branch_secretary', 'monitor', 
             'assistant_department_head', 'club_president', 'committee_member', 'assistant_club_president'],  // 校级：各类职务
        college: ['executive_chair', 'presidium_member', 'department_head', 'branch_secretary', 'monitor', 
             'assistant_department_head', 'club_president', 'committee_member', 'assistant_club_president']  // 院级：各类职务
      }
    },
    sports: {
      levels: ['provincial', 'school', 'college'],  // 体育比赛级别
      grades: {
        provincial: ['champion', 'runner_up', 'third_place', 'top_8'],  // 省级：冠军、亚军、季军、第四至八名
        school: ['champion', 'runner_up', 'third_place', 'top_8'],  // 校级：冠军、亚军、季军、第四至八名
        college: ['champion', 'runner_up', 'third_place', 'top_8']  // 院级：冠军、亚军、季军、第四至八名
      }
    },
    honor_title: {
      levels: ['provincial', 'school', 'college'],  // 荣誉称号级别
      grades: {
        provincial: ['individual', 'collective'],  // 省级：个人、集体
        school: ['individual', 'collective'],  // 校级：个人、集体
        college: ['individual', 'collective']  // 院级：个人、集体
      }
    }
  }
}

// 处理规则类型变化
const handleTypeChange = (type) => {
  ruleForm.type = type
  ruleForm.sub_type = '' // 切换类型时清空子类型
  ruleForm.level = '' // 清空级别
  ruleForm.grade = '' // 清空等级
  ruleForm.category = '' // 清空奖项类别
  // 如果不是综合表现类型，清空团队角色
  if (type !== 'comprehensive') {
    ruleForm.team_role = ''
  }
}

// 处理子类型变化
const handleSubTypeChange = () => {
  ruleForm.level = '' // 切换子类型时清空级别
  // 综合表现类型不需要等级，其他类型需要清空等级
  if (ruleForm.type !== 'comprehensive') {
    ruleForm.grade = '' // 清空等级
  }
  ruleForm.category = '' // 清空奖项类别
  ruleForm.research_type = '' // 清空科研成果类型
}

// 处理级别变化
const handleLevelChange = () => {
  // 综合表现类型不需要等级，其他类型切换级别时清空等级
  if (ruleForm.type !== 'comprehensive') {
    ruleForm.grade = '' // 切换级别时清空等级
  }
}

// 根据当前规则类型获取子类型选项
const currentSubTypes = computed(() => {
  const subTypes = {
    academic: [
      { value: 'competition', label: '学业竞赛', icon: ['fas', 'trophy'] },
      { value: 'research', label: '科研成果', icon: ['fas', 'flask'] },
      { value: 'innovation', label: '创新创业训练', icon: ['fas', 'lightbulb'] }
    ],
    comprehensive: [
      { value: 'international_internship', label: '国际组织实习', icon: ['fas', 'globe'] },
      { value: 'military_service', label: '参军入伍服兵役', icon: ['fas', 'shield-alt'] },
      { value: 'volunteer', label: '志愿服务', icon: ['fas', 'hands-helping'] },
      { value: 'social_work', label: '社会工作', icon: ['fas', 'users'] },
      { value: 'sports', label: '体育比赛', icon: ['fas', 'futbol'] },
      { value: 'honor_title', label: '荣誉称号', icon: ['fas', 'award'] }
    ]
  }
  return ruleForm.type ? subTypes[ruleForm.type] : []
})

// 根据当前规则类型和子类型获取级别选项
const currentLevels = computed(() => {
  if (!ruleForm.type || !ruleForm.sub_type) return []
  
  const options = levelGradeOptions[ruleForm.type][ruleForm.sub_type]
  if (!options) return []
  
  return options.levels.map(level => ({
    value: level,
    label: getLevelText(level)
  }))
})

// 根据当前级别获取等级选项
const currentGrades = computed(() => {
  if (!ruleForm.type || !ruleForm.sub_type) return []
  
  const options = levelGradeOptions[ruleForm.type][ruleForm.sub_type]
  if (!options || !options.grades) return []
  
  // 获取当前级别的等级选项，如果没有级别则使用空字符串作为键
  const levelKey = ruleForm.level || ''
  if (!options.grades[levelKey]) return []
  
  return options.grades[levelKey].map(grade => ({
    value: grade,
    label: getGradeText(grade)
  }))
})

// 根据当前规则类型和子类型获取奖项类别选项
const currentCategories = computed(() => {
  if (!ruleForm.type || !ruleForm.sub_type) {
    return []
  }
  // 只有学业竞赛有奖项类别
  if (ruleForm.type === 'academic' && ruleForm.sub_type === 'competition') {
    return levelGradeOptions[ruleForm.type]?.[ruleForm.sub_type]?.categories || []
  }
  return []
})

// 打开添加规则模态框
const openAddRuleModal = () => {
  editingRule.value = null
  ruleForm.name = ''
  ruleForm.type = 'academic'
  ruleForm.sub_type = ''
  ruleForm.level = ''
  ruleForm.grade = ''
  ruleForm.category = ''
  ruleForm.research_type = ''
  ruleForm.participation_type = 'individual' // 默认为个人参与
  ruleForm.team_role = '' // 默认为空，仅当参与类型为集体时需要
  ruleForm.author_rank_type = 'unranked' // 默认为不区分排名
  ruleForm.author_rank = null // 默认为空，仅当区分排名时需要
  ruleForm.score = 0
  ruleForm.status = 'active'
  ruleForm.description = ''
  showAddRuleModal.value = true
}

const closeModal = () => {
  showAddRuleModal.value = false
  editingRule.value = null
  Object.assign(ruleForm, {
    name: '',
    type: 'academic',
    sub_type: '',
    level: '',
    grade: '',
    category: '',
    research_type: '',
    participation_type: 'individual',
    team_role: '',
    author_rank_type: 'unranked',
    author_rank: null,
    score: 0,
    status: 'active',
    description: ''
  })
}

// 生命周期
onMounted(() => {
  loadRules() // 从API加载规则数据
})
</script>

<style scoped>
/* 组件特有样式 - 如果没有特殊样式，可以留空 */
/* 覆盖或补充共享样式 */
/* 加载状态样式 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 10px;
  color: #007bff;
  font-size: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.application-table th:last-child,
.application-table td:last-child {
  width: 160px; /* 增加宽度以容纳删除按钮 */
  min-width: 160px;
  text-align: center;
}

/* 删除按钮样式 */
.delete-btn {
  color: #dc3545; /* 红色表示危险操作 */
}

/* 特殊规则状态标签样式 */
.status-badge.status-special {
  background-color: #ffc107; /* 黄色表示特殊规则 */
  color: #212529;
}

.status-badge.status-normal {
  background-color: #17a2b8; /* 青色表示普通规则 */
  color: white;
}

.delete-btn:hover {
  background-color: #f8d7da;
  border-color: #dc3545;
}
</style>

<style>
/* 引入共享样式 */
@import '../common/shared-styles.css';
</style>