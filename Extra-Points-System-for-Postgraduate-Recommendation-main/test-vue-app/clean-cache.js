// 清理localStorage中的数据
try {
  localStorage.removeItem('token');
  localStorage.removeItem('userInfo');
  console.log('缓存已清理');
} catch (error) {
  console.error('清理缓存时出错:', error);
}