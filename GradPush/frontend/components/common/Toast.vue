<template>
  <div class="toast-container" ref="toastContainer">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      :class="[
        'toast',
        `toast-${toast.type || 'success'}`,
        { 'toast-visible': toast.visible }
      ]"
      @click="removeToast(toast.id)"
    >
      <div class="toast-icon">
        {{ getToastIcon(toast.type) }}
      </div>
      <div class="toast-content">{{ toast.message }}</div>
      <button class="toast-close" @click.stop="removeToast(toast.id)">
        ×
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject, provide, onMounted, onUnmounted } from 'vue'
import { useToastStore } from '../../stores/toast'

// 使用Toast store
const toastStore = useToastStore()
const toastContainer = ref(null)

// 从store获取toasts
const toasts = computed(() => toastStore.toasts)

// 获取toast图标
const getToastIcon = (type) => {
  switch (type) {
    case 'success':
      return '✓'
    case 'error':
      return '✕'
    case 'warning':
      return '!'
    case 'info':
      return 'ℹ'
    default:
      return '✓'
  }
}

// 移除指定toast
const removeToast = (id) => {
  toastStore.removeToast(id)
}

// 注入并提供toast方法到全局
const toast = {
  success: (message, duration = 1500) => {
    toastStore.addToast({ type: 'success', message, duration })
  },
  error: (message, duration = 1500) => {
    toastStore.addToast({ type: 'error', message, duration })
  },
  warning: (message, duration = 1500) => {
    toastStore.addToast({ type: 'warning', message, duration })
  },
  info: (message, duration = 1500) => {
    toastStore.addToast({ type: 'info', message, duration })
  }
}

// 提供给全局使用
provide('toast', toast)
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: auto;
  max-width: 500px;
  padding: 16px;
  pointer-events: none;
}

.toast {
  padding: 6px 8px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 10px;
  opacity: 0;
  transform: translateY(-20px);
  transition: all 0.3s ease;
  pointer-events: auto;
  cursor: pointer;
}

.toast-visible {
  opacity: 1;
  transform: translateY(0);
}

.toast-success {
  background-color: #eafaf1;
  color: #27ae60;
  border-left: 4px solid #27ae60;
}

.toast-error {
  background-color: #fdedec;
  color: #e74c3c;
  border-left: 4px solid #e74c3c;
}

.toast-warning {
  background-color: #fff3cd;
  color: #f39c12;
  border-left: 4px solid #f39c12;
}

.toast-info {
  background-color: #d1ecf1;
  color: #3498db;
  border-left: 4px solid #3498db;
}

.toast-icon {
  font-size: 18px;
  flex-shrink: 0;
  font-weight: bold;
}

.toast-content {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
}

.toast-close {
  background: none;
  border: none;
  color: inherit;
  font-size: 16px;
  cursor: pointer;
  padding: 2px;
  border-radius: 3px;
  transition: background-color 0.2s;
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.toast-close:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .toast-container {
    max-width: 100%;
    padding: 15px;
  }
  
  .toast {
    padding: 12px 15px;
  }
  
  .toast-content {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .toast-container {
    padding: 10px;
  }
  
  .toast {
    padding: 10px 12px;
    gap: 8px;
  }
}
</style>