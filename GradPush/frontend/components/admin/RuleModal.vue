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
                        <div class="radio-card horizontal" :class="{ active: jsonFormulaConfig.type === 'tree' }"
                          @click="jsonFormulaConfig.type = 'tree'">
                          <div class="radio-icon">
                            <font-awesome-icon :icon="['fas', 'tree']" />
                          </div>
                          <span>树结构计算</span>
                        </div>
                      </div>
                    </div>

                    <!-- 树结构计算配置 -->
                    <div v-if="jsonFormulaConfig.type === 'tree'" class="tree-config">
                      <div class="help-text">
                        树结构计算支持层级化的计分配置，适用于复杂的评分场景。
                        <br>计算方式：根据树结构的节点组合应用对应分数
                      </div>

                      <!-- 树结构配置 -->
                      <div v-if="jsonFormulaConfig.tree.mode === 'tree'" class="tree-config">
                        <h4>树结构配置</h4>
                        <div class="tree-config-container">
                          <!-- 树可视化区域 -->
                          <div class="tree-visualization">
                            <!-- 根节点 -->
                            <div v-if="treeData.root" class="tree-root">
                              <tree-node :node="treeData.root" :level="0" :selected-node-id="selectedNodeId"
                                @node-select="handleNodeSelect" @add-child="handleAddChild"
                                @delete-node="handleDeleteNode" @update-node="handleUpdateNode" />
                            </div>
                            <div v-else class="tree-empty">
                              <p>树结构为空，请添加根节点</p>
                              <button type="button" class="btn btn-primary" @click="initializeTree">
                                <font-awesome-icon icon="tree" /> 初始化树结构
                              </button>
                            </div>
                          </div>

                          <!-- 节点编辑面板 -->
                          <div v-if="selectedNode" class="node-editor-panel">
                            <div class="panel-header">
                              <h5>节点编辑</h5>
                              <button type="button" class="close-btn" @click="selectedNodeId = null">
                                <font-awesome-icon icon="times" />
                              </button>
                            </div>

                            <div class="panel-body">
                              <!-- 节点基本信息 -->
                              <div class="form-group">
                                <label class="form-label">节点名称</label>
                                <input type="text" class="form-control" v-model="selectedNode.dimension.name"
                                  @input="updateNodeDimensionName" placeholder="输入节点名称">
                              </div>

                              <div class="form-group">
                                <label class="form-label">分数</label>
                                <input type="number" class="form-control" v-model="selectedNode.score"
                                  @input="updateNodeScore" step="0.1" min="0" :max="maxScore">
                              </div>

                              <!-- 节点路径显示 -->
                              <div class="form-group">
                                <label class="form-label">节点路径</label>
                                <div class="node-path">{{ getNodePath(selectedNode) }}</div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      <!-- 分数矩阵 -->
                      <div class="tree-scores">
                        <h4>分数矩阵</h4>
                        <div class="tree-table">
                          <!-- 表头 - 仅在矩阵模式下显示 -->
                          <div v-if="jsonFormulaConfig.tree.mode === 'tree'" class="tree-header">
                            <div v-for="(dimension, index) in getTreeDimensions()" :key="index"
                              class="tree-header-cell">
                              {{ dimension }}
                            </div>
                            <div class="tree-header-cell">分数</div>
                          </div>

                          <!-- 分数表内容 -->
                          <div v-for="key in generateKeysFromTree()" :key="key" class="tree-row">
                            <div v-for="(value, index) in key.split('_')" :key="index" class="tree-cell">
                              {{ value }}
                            </div>
                            <div class="tree-cell">
                              <input type="number" class="form-control" :value="jsonFormulaConfig.tree.scores[key] || 0"
                                @input="updateTreeScore(key, $event.target.value)" step="0.1">
                            </div>
                          </div>

                          <!-- 树结构模式下的提示 -->
                          <div v-if="jsonFormulaConfig.tree.mode === 'tree' && generateKeysFromTree().length === 0"
                            class="text-center text-muted mt-3">
                            <p>树结构中没有叶子节点，无法生成分数矩阵。</p>
                            <p>请在树结构中添加叶子节点（无子节点的节点）或切换到矩阵模式。</p>
                          </div>

                          <!-- 矩阵模式下的空提示 -->
                          <div v-else-if="jsonFormulaConfig.tree.mode === 'tree' && generateKeysFromTree().length === 0"
                            class="text-center text-muted mt-3">
                            <p>请添加维度和维度项以生成分数矩阵。</p>
                          </div>
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

// 公式配置 - 支持树结构计算
const jsonFormulaConfig = reactive({
  type: 'tree',
  // 树结构计算配置
  tree: {
    mode: 'tree', // 'tree'
    // 树结构配置 - 简单默认值，实际使用时会被覆盖或初始化
    structure: {
      root: {
        id: 'root',
        dimension: { name: '根节点', key: 'root' },
        value: 'root',
        children: []
      }
    },
    scores: {} // 存储维度组合的分数
  }
})

// 获取树结构的所有维度名称
function getTreeDimensions() {
  // 检查树结构是否存在
  if (!jsonFormulaConfig.tree.structure || !jsonFormulaConfig.tree.structure.root) {
    return []
  }

  const root = jsonFormulaConfig.tree.structure.root
  const dimensions = []

  // 递归遍历树，获取所有维度名称
  function traverse(node, depth = 0) {
    if (node.dimension && node.dimension.key === 'root') {
      // 跳过根节点
      node.children.forEach(child => {
        traverse(child, depth)
      })
    } else {
      // 如果是第一层节点，添加到维度列表
      if (depth === 0) {
        dimensions.push(node.dimension.name)
      }

      if (node.children.length > 0) {
        // 有子节点，继续遍历
        node.children.forEach(child => {
          traverse(child, depth + 1)
        })
      }
    }
  }

  traverse(root)
  return dimensions
}

// 从树结构生成所有维度组合的键
function generateKeysFromTree() {
  // 检查树结构是否存在
  if (!jsonFormulaConfig.tree.structure || !jsonFormulaConfig.tree.structure.root) {
    return []
  }

  const root = jsonFormulaConfig.tree.structure.root
  const keys = []
  const keyCount = new Map() // 用于跟踪重复键的数量

  // 递归遍历树，生成所有叶子节点的路径键
  function traverse(node, currentPath) {
    if (node.dimension && node.dimension.key === 'root') {
      // 跳过根节点
      node.children.forEach(child => {
        traverse(child, [])
      })
    } else {
      // 添加当前节点到路径，优先使用node.value
      let nodeValue = node.value || (node.dimension ? node.dimension.name : '')
      const newPath = [...currentPath, nodeValue]

      if (node.children.length > 0) {
        // 有子节点，继续遍历
        node.children.forEach(child => {
          traverse(child, newPath)
        })
      } else {
        // 叶子节点，生成键
        let key = newPath.join('_')

        // 检查键是否重复，如果重复则添加唯一标识符
        if (keyCount.has(key)) {
          const count = keyCount.get(key)
          keyCount.set(key, count + 1)
          key = `${key}_${count}`
        } else {
          keyCount.set(key, 1)
        }

        keys.push(key)
      }
    }
  }

  traverse(root, [])
  return keys
}

// 更新分数矩阵，确保所有维度组合都有对应的分数
function updateTreeScores() {
  const keys = generateKeysFromTree()
  const scores = { ...jsonFormulaConfig.tree.scores }

  // 从树节点获取分数（我们只支持树结构模式）
  // 遍历树结构，获取所有叶子节点的分数
  const keyCount = new Map() // 用于跟踪重复键的数量

  function traverseTree(node, currentPath) {
    if (!node) return

    if (node.dimension && node.dimension.key === 'root') {
      // 跳过根节点
      node.children.forEach(child => {
        traverseTree(child, [])
      })
    } else {
      // 添加当前节点到路径，优先使用node.value
      const nodeValue = node.value || (node.dimension ? node.dimension.name : '')
      const newPath = [...currentPath, nodeValue]

      if (node.children && node.children.length > 0) {
        // 有子节点，继续遍历
        node.children.forEach(child => {
          traverseTree(child, newPath)
        })
      } else {
        // 叶子节点，更新分数矩阵
        let key = newPath.join('_')

        // 检查键是否重复，如果重复则添加唯一标识符（与generateKeysFromTree保持一致）
        if (keyCount.has(key)) {
          const count = keyCount.get(key)
          keyCount.set(key, count + 1)
          key = `${key}_${count}`
        } else {
          keyCount.set(key, 1)
        }

        scores[key] = parseFloat(node.score || 0)
      }
    }
  }

  // 从根节点开始遍历
  if (treeData.value.root) {
    traverseTree(treeData.value.root, [])
  }

  // 移除不再存在的组合的分数
  Object.keys(scores).forEach(key => {
    if (!keys.includes(key)) {
      delete scores[key]
    }
  })

  jsonFormulaConfig.tree.scores = scores
}

// 树节点组件
// 导入TreeNode组件
import TreeNode from './TreeNode.vue'

// 树结构管理逻辑
// 生成唯一节点ID
function generateNodeId() {
  return `node_${Date.now()}_${Math.floor(Math.random() * 1000)}`
}

// 计算树数据
const treeData = computed(() => {
  if (jsonFormulaConfig.tree.structure && jsonFormulaConfig.tree.structure.root) {
    return jsonFormulaConfig.tree.structure
  }
  return { root: null }
})

// 选中节点管理
const selectedNodeId = ref(null)
const selectedNode = computed(() => {
  if (!selectedNodeId.value) return null
  return findNodeById(treeData.value.root, selectedNodeId.value)
})

// 查找节点函数
function findNodeById(node, id) {
  if (!node) return null
  if (node.id === id) return node
  for (const child of node.children || []) {
    const found = findNodeById(child, id)
    if (found) return found
  }
  return null
}

// 节点操作函数
// 处理节点选择
function handleNodeSelect(nodeId) {
  selectedNodeId.value = nodeId

  // 定位编辑面板到选中节点右侧
  setTimeout(() => {
    const selectedNodeElement = document.querySelector(`[data-node-id="${nodeId}"]`)
    const editorPanel = document.querySelector('.node-editor-panel')

    if (selectedNodeElement && editorPanel) {
      const nodeRect = selectedNodeElement.getBoundingClientRect()
      const panelRect = editorPanel.getBoundingClientRect()

      // 使用fixed定位直接相对于视口定位
      let top = nodeRect.top
      let left = nodeRect.right + 10 // 10px间距

      // 确保面板不会超出视口右侧
      const viewportWidth = window.innerWidth
      if (left + panelRect.width > viewportWidth - 20) {
        left = nodeRect.left - panelRect.width - 10
      }

      // 确保面板不会超出视口底部
      const viewportHeight = window.innerHeight
      if (top + panelRect.height > viewportHeight - 20) {
        top = viewportHeight - panelRect.height - 20
      }

      // 确保面板不会超出视口顶部
      if (top < 20) {
        top = 20
      }

      // 设置面板位置
      editorPanel.style.position = 'fixed'
      editorPanel.style.top = `${top}px`
      editorPanel.style.left = `${left}px`
    }
  }, 0)
}

// 处理添加子节点
function handleAddChild(parent) {
  const parentNode = typeof parent === 'object' ? parent : findNodeById(treeData.value.root, parent)
  if (!parentNode) return

  const newNode = {
    id: generateNodeId(),
    dimension: {
      name: '新维度',
      key: 'new_dimension'
    },
    value: '新维度',
    children: [],
    score: 0
  }

  if (!parentNode.children) parentNode.children = []
  parentNode.children.push(newNode)

  // 自动展开父节点
  parentNode.expanded = true

  // 选中新节点并更新编辑面板位置
  handleNodeSelect(newNode.id)
}

// 处理删除节点
function handleDeleteNode(node) {
  const nodeToDelete = typeof node === 'object' ? node : findNodeById(treeData.value.root, node)
  if (!nodeToDelete || nodeToDelete.id === 'root') return
  if (!nodeToDelete) return

  function findParent(currentNode, targetNode) {
    if (!currentNode || !currentNode.children) return null
    if (currentNode.children.some(child => child.id === targetNode.id)) {
      return currentNode
    }
    for (const child of currentNode.children) {
      const result = findParent(child, targetNode)
      if (result) return result
    }
    return null
  }

  const parent = findParent(treeData.value.root, nodeToDelete)
  if (parent) {
    parent.children = parent.children.filter(child => child.id !== nodeToDelete.id)
    if (selectedNodeId.value === nodeToDelete.id) {
      selectedNodeId.value = null
    }
  }
}

// 处理更新节点
function handleUpdateNode(updatedNode) {
  const node = findNodeById(treeData.value.root, updatedNode.id)
  if (node) {
    Object.assign(node, updatedNode)
  }
}

// 初始化树结构
function initializeTree() {
  if (!jsonFormulaConfig.tree) jsonFormulaConfig.tree = {}
  if (!jsonFormulaConfig.tree.structure) jsonFormulaConfig.tree.structure = {}

  jsonFormulaConfig.tree.structure.root = {
    id: 'root',
    dimension: {
      name: '根节点',
      key: 'root'
    },
    value: '根节点',
    children: [],
    score: 0
  }
  // 初始选中根节点
  selectedNodeId.value = 'root'
}

// 更新节点维度名称
function updateNodeDimensionName() {
  if (selectedNode.value) {
    selectedNode.value.dimension.key = selectedNode.value.dimension.name.toLowerCase().replace(/\s+/g, '_')
    selectedNode.value.value = selectedNode.value.dimension.name
    updateTreeScores()
  }
}

// 更新节点分数
function updateNodeScore() {
  if (selectedNode.value) {
    updateTreeScores()
  }
}

// 更新树分数
function updateTreeScore(key, value) {
  jsonFormulaConfig.tree.scores[key] = parseFloat(value) || 0
}

// 获取节点路径
function getNodePath(node) {
  function findPath(currentNode, targetNode, path = []) {
    if (!currentNode) return null

    const currentPath = [...path, currentNode.dimension ? currentNode.dimension.name : '']

    if (currentNode.id === targetNode.id) {
      return currentPath
    }

    for (const child of currentNode.children) {
      const result = findPath(child, targetNode, currentPath)
      if (result) return result
    }

    return null
  }

  const path = findPath(jsonFormulaConfig.tree.structure.root, node)
  return path ? path.join(' → ') : ''
}

// 监听编辑规则的变化
watch(() => props.editingRule, (newRule) => {
  if (newRule) {
    // 分配基本规则数据
    Object.assign(ruleForm, newRule)

    // 处理计算设置
    if (newRule.calculation) {
      // 设置计算类型为tree（仅支持树结构计算）
      jsonFormulaConfig.type = 'tree'

      // 从计算参数中复制配置
      if (newRule.calculation.parameters) {
        // 设置树结构配置
        if (newRule.calculation.parameters.tree) {
          // 确保树结构模式
          jsonFormulaConfig.tree.mode = 'tree'
          // 复制树结构数据
          if (newRule.calculation.parameters.tree.structure) {
            jsonFormulaConfig.tree.structure = newRule.calculation.parameters.tree.structure
          }
          // 复制分数配置
          if (newRule.calculation.parameters.tree.scores) {
            jsonFormulaConfig.tree.scores = newRule.calculation.parameters.tree.scores
          }
        } else {
          // 如果没有树结构配置，创建默认配置
          jsonFormulaConfig.tree.structure = {
            root: {
              id: 'root',
              dimension: { name: '根节点', key: 'root' },
              value: 'root',
              children: []
            }
          }
          jsonFormulaConfig.tree.scores = {}
        }

        // 如果存在，从计算参数设置最大分数和最大数量
        if (newRule.calculation.parameters.max_score) {
          ruleForm.max_score = newRule.calculation.parameters.max_score
        }
        if (newRule.calculation.parameters.max_count) {
          ruleForm.max_count = newRule.calculation.parameters.max_count
        }
      }
    } else {
      // 默认JSON公式配置 - 仅支持树结构计算
      jsonFormulaConfig.type = 'tree'
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
      type: 'tree',
      // 树结构计算配置
      tree: {
        mode: 'tree',
        // 树结构配置
        structure: {
          root: {
            id: 'root',
            dimension: { name: '根节点', key: 'root' },
            value: 'root',
            children: []
          }
        },
        scores: {} // 存储维度组合的分数
      }
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

// 计算最大分数（用于限制输入）
const maxScore = computed(() => {
  return parseFloat(ruleForm.max_score) || 100
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

  // 树结构计算配置
  params.tree = jsonFormulaConfig.tree
  // 确保模式为tree
  params.tree.mode = 'tree'

  return {
    calculation_type: 'tree', // 仅支持tree类型
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
  width: 50%;
}

.form-layout-right {
  flex: 1;
  width: 50%;
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
.coefficient-type-group .grade-config-item {
  margin-bottom: 10px;
}

.coefficient-type-group .grade-config-item .coefficient-row {
  display: flex;
  align-items: center;
  gap: 15px;
  width: 100%;
  margin-bottom: 0px;
}

.coefficient-type-group .grade-config-item .coefficient-row .form-group {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
  flex: 1;
  margin-bottom: 0;
}

.coefficient-type-group .grade-config-item .coefficient-row .form-group .form-label {
  display: inline-block;
  white-space: nowrap;
  min-width: 36px;
  margin-bottom: 0;
  font-weight: 500;
  color: #555;
}

.coefficient-type-group .grade-config-item .coefficient-row .form-group .form-control {
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

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

/* 树结构计算样式 */
.tree-config {
  margin-top: 15px;
}

.tree-scores {
  margin-top: 25px;
}

.tree-table {
  overflow-x: auto;
  border: 1px solid #e9ecef;
  border-radius: 6px;
}

.tree-header {
  display: flex;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  font-weight: bold;
}

.tree-row {
  display: flex;
  border-bottom: 1px solid #dee2e6;
}

.tree-row:last-child {
  border-bottom: none;
}

.tree-header-cell,
.tree-cell {
  padding: 10px;
  min-width: 120px;
  border-right: 1px solid #dee2e6;
}

.tree-header-cell:last-child,
.tree-cell:last-child {
  border-right: none;
}

/* Tree Structure Styles */
.tree-config-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.tree-visualization {
  position: relative;
  min-height: 200px;
  max-height: 600px;
  overflow-y: auto;
  padding: 20px;
  background-color: #f9fafb;
  border-radius: 6px;
}

.tree-root {
  display: flex;
  justify-content: center;
  margin-bottom: 40px;
}

.tree-empty {
  text-align: center;
  padding: 40px 20px;
  color: #9ca3af;
}

.tree-empty p {
  margin-bottom: 20px;
}

.node-editor-panel {
  position: absolute;
  width: 280px;
  max-height: 80vh;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow-y: auto;
}

.node-editor-panel .panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid #e0e0e0;
}

.node-editor-panel .panel-header h5 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}

.node-editor-panel .panel-header .close-btn {
  background: none;
  border: none;
  font-size: 16px;
  color: #9ca3af;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.node-editor-panel .panel-body {
  padding: 10px 12px;
}

.node-editor-panel .form-group {
  margin-bottom: 12px;
}

.node-editor-panel .form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
  color: #374151;
}

.node-editor-panel .form-control {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 13px;
}

.node-editor-panel .help-text {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.node-path {
  padding: 8px 12px;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 12px;
  color: #6b7280;
  word-break: break-all;
  font-family: monospace;
}

.node-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.node-actions .btn {
  flex: 1;
  font-size: 14px;
  padding: 8px 12px;
}

.tree-node {
  margin-bottom: 20px;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 图形化树结构样式 */
.tree-children {
  display: flex !important;
  flex-direction: row !important;
  justify-content: center;
  gap: 50px;
  margin-top: 40px;
  position: relative;
  flex-wrap: wrap;
  width: 100%;
  box-sizing: border-box;
  overflow-x: auto;
  padding: 0 20px;
  /* 确保连接线不被裁剪 */
  overflow: visible;
}

/* 连接线样式 - 水平连接线（节点间） */
.tree-children::after {
  content: '';
  position: absolute;
  top: -10px;
  left: 20px;
  right: 20px;
  height: 4px;
  background-color: #3b82f6 !important;
  z-index: 1 !important;
  opacity: 1 !important;
  visibility: visible !important;
  pointer-events: none;
  width: calc(100% - 40px);
  /* 确保连接线在节点之间 */
}

/* 连接线样式 - 垂直连接线（父节点到子节点组） */
.tree-children::before {
  content: '';
  position: absolute;
  top: -30px;
  left: 50%;
  width: 4px;
  height: 30px;
  background-color: #3b82f6 !important;
  transform: translateX(-50%) !important;
  z-index: 1 !important;
  opacity: 1 !important;
  visibility: visible !important;
  pointer-events: none;
}

/* 确保所有层次的连接线都能正确显示 */
.tree-node .tree-children::after,
.tree-node .tree-children::before {
  display: block !important;
  opacity: 1 !important;
  visibility: visible !important;
}

/* 隐藏旧的连接线 */
.tree-node::before {
  display: none;
}

/* 节点内容样式 - 数据结构节点风格 */
.node-content {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 40px !important;
  height: 40px !important;
  border-radius: 50% !important;
  cursor: pointer !important;
  user-select: none !important;
  transition: all 0.3s ease !important;
  background-color: #ffffff !important;
  border: 2px solid #6366f1 !important;
  position: relative !important;
  z-index: 2 !important;
  /* 确保节点在连接线之上 */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
  margin: 0 auto !important;
  margin-bottom: 10px !important;
  padding: 0 !important;
}

/* 节点悬停效果 */
.node-content:hover {
  background-color: #f0f4ff;
  border-color: #4f46e5;
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
}

/* 选中节点样式 */
.node-content.selected {
  background-color: #003366;
  color: white;
  border: 2px solid #002244;
  box-shadow: 0 10px 30px rgba(0, 51, 102, 0.4);
  transform: translateY(-4px) scale(1.05);
}

/* 选中状态下的子元素颜色 */
.node-content.selected .node-label {
  color: white;
}

.node-content.selected .node-score {
  color: #b3d7ff;
}

.node-content.selected .node-toggle {
  color: white;
}

.node-toggle {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  margin-right: 16px;
  font-size: 20px;
  transition: all 0.3s ease;
  border-radius: 50%;
  background-color: #f0f4ff;
  border: 2px solid #e0e7ff;
}

.node-content:hover .node-toggle {
  background-color: #e0e7ff;
  border-color: #c7d2fe;
}

.node-content.selected .node-toggle {
  background-color: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.node-label {
  flex: 1;
  font-weight: 700;
  margin-right: 16px;
  font-size: 18px;
  color: #1f2937;
  text-align: center;
}

.node-score {
  padding: 8px 20px;
  border-radius: 25px;
  background-color: #fef3c7;
  color: #d97706;
  font-weight: 700;
  font-size: 16px;
  border: 2px solid #fde68a;
  white-space: nowrap;
}

.node-content.selected .node-score {
  background-color: rgba(255, 255, 255, 0.2);
  color: #b3d7ff;
  border-color: rgba(255, 255, 255, 0.3);
}

/* 节点操作按钮容器 */
.node-actions {
  display: flex;
  gap: 10px;
  margin-left: 45px;
  margin-top: 8px;
  padding: 12px;
  background-color: #f8fafc;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

/* 树节点按钮样式 */
.node-actions .btn {
  padding: 8px 16px;
  font-size: 14px;
  opacity: 1;
  transition: all 0.3s ease;
  transform-origin: left center;
  border-radius: 6px;
  font-weight: 500;
  min-width: 100px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.node-actions .btn:hover {
  opacity: 1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 根节点特殊样式 */
.root-node .node-content {
  background-color: #f0f8ff;
  border-color: #d0e8ff;
}

.root-node .node-content:hover {
  background-color: #e6f3ff;
}

/* 树控件面板样式 */
.tree-controls {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  background-color: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  margin-left: 20px;
}

.tree-controls .form-group {
  margin-bottom: 15px;
}

/* Tree Styles */
.tree-row {
  display: flex;
  margin-bottom: 5px;
}

.tree-cell {
  margin-right: 10px;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
  min-width: 100px;
  text-align: center;
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