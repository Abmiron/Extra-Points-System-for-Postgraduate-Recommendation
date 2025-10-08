<template>
  <div class="page-content">
    <div class="page-title">
      <span>调试页面</span>
    </div>

    <div class="debug-actions">
      <button class="btn" @click="clearStorage">清除本地存储</button>
      <button class="btn" @click="reloadData">重新加载数据</button>
      <button class="btn" @click="showStorage">显示存储内容</button>
    </div>

    <div class="debug-info">
      <h3>本地存储内容:</h3>
      <pre>{{ storageContent }}</pre>

      <h3>待审核申请:</h3>
      <pre>{{ pendingApplications }}</pre>

      <h3>已审核申请:</h3>
      <pre>{{ reviewedApplications }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const storageContent = ref('')
const pendingApplications = ref([])
const reviewedApplications = ref([])

const clearStorage = () => {
  localStorage.removeItem('studentApplications')
  alert('本地存储已清除')
  reloadData()
}

const reloadData = () => {
  const allApplications = JSON.parse(localStorage.getItem('studentApplications') || '[]')
  storageContent.value = JSON.stringify(allApplications, null, 2)
  pendingApplications.value = allApplications.filter(app => app.status === 'pending')
  reviewedApplications.value = allApplications.filter(app => app.status === 'approved' || app.status === 'rejected')
}

const showStorage = () => {
  reloadData()
}

onMounted(() => {
  reloadData()
})
</script>

<style scoped>
.debug-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.debug-info {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
}

.debug-info pre {
  background: white;
  padding: 10px;
  border-radius: 4px;
  overflow: auto;
  max-height: 300px;
}
</style>