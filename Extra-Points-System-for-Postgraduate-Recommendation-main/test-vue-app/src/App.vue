<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

// 简化版App.vue，移除对store的依赖
onMounted(() => {
  console.log('App组件已挂载')
})
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html,
body {
  height: 100%;
  width: 100%;
  overflow: hidden;
}

#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>