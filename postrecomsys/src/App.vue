<template>
  <div id="app">
            <!-- 调试信息，上线前删除 -->
            <div v-if="false" style="position: fixed; top: 0; left: 0; background: red; color: white; padding: 5px; z-index: 9999;">
            当前路由: {{ $route.path }}
            </div>
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  mounted() {
    console.log('App mounted, current route:', this.$route)
  }
}
</script>
<style>
/* 全局样式 */
</style>