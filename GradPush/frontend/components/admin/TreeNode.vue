<template>
  <div class="tree-node" :class="{ expanded: node.expanded }">
    <!-- 节点内容 -->
    <div 
      class="node-content"
      :class="{ 
        selected: node.id === selectedNodeId,
        leaf: !node.children || node.children.length === 0
      }"
      @click="$emit('node-select', node.id)"
      :data-node-id="node.id"
    >
      <!-- 展开/折叠按钮 -->
      <button 
        v-if="node.children && node.children.length > 0"
        type="button"
        class="node-toggle"
        @click.stop="toggleExpand"
        :title="node.expanded ? '折叠' : '展开'"
      >
        <font-awesome-icon :icon="node.expanded ? 'chevron-down' : 'chevron-right'" />
      </button>
      
      <!-- 节点信息 -->
      <div class="node-info">
        <div class="node-name">{{ node.dimension.name }}</div>
        <div class="node-meta">
          <span class="node-score">分数: {{ node.score }}</span>
        </div>
      </div>
      
      <!-- 节点操作 -->
      <div class="node-actions">
        <button 
          type="button" 
          class="btn-icon"
          @click.stop="$emit('add-child', node)"
          title="添加子节点"
        >
          <font-awesome-icon icon="plus" />
        </button>
        <button 
          v-if="node.id !== 'root'"
          type="button" 
          class="btn-icon"
          @click.stop="$emit('delete-node', node)"
          title="删除节点"
        >
          <font-awesome-icon icon="trash" />
        </button>
      </div>
    </div>
    
    <!-- 子节点 -->
    <div v-if="node.expanded && node.children && node.children.length > 0" class="node-children">
      <tree-node
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :level="level + 1"
        :selected-node-id="selectedNodeId"
        @node-select="$emit('node-select', $event)"
        @add-child="$emit('add-child', $event)"
        @delete-node="$emit('delete-node', $event)"
        @update-node="$emit('update-node', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  node: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 0
  },
  selectedNodeId: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['node-select', 'add-child', 'delete-node', 'update-node'])

function toggleExpand() {
  props.node.expanded = !props.node.expanded
  emit('update-node', props.node)
}
</script>

<style scoped>
.tree-node {
  margin-left: calc(var(--level, 0) * 24px);
  transition: margin-left 0.3s ease;
}

.node-content {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  margin-bottom: 4px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.node-content:hover {
  background: #f8f9fa;
  border-color: #c0c0c0;
}

.node-content.selected {
  background: #e3f2fd;
  border-color: #2196f3;
  box-shadow: 0 0 0 1px rgba(33, 150, 243, 0.1);
}

.node-content.leaf {
  border-left: 3px solid #4caf50;
}

.node-toggle {
  background: none;
  border: none;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
  color: #666;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.node-toggle:hover {
  background: #f0f0f0;
  color: #333;
}

.node-info {
  flex: 1;
  min-width: 0;
}

.node-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 2px;
  font-size: 14px;
}

.node-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #666;
}

.node-value {
  color: #666;
}

.node-score {
  color: #2196f3;
  font-weight: 500;
}

.node-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.node-content:hover .node-actions {
  opacity: 1;
}

.btn-icon {
  background: none;
  border: none;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: #f0f0f0;
  color: #333;
}

.node-children {
  margin-left: 24px;
  border-left: 1px dashed #e0e0e0;
  padding-left: 12px;
}

@media (max-width: 768px) {
  .tree-node {
    margin-left: calc(var(--level, 0) * 16px);
  }
  
  .node-content {
    padding: 8px 10px;
  }
  
  .node-meta {
    gap: 8px;
    font-size: 11px;
  }
}
</style>