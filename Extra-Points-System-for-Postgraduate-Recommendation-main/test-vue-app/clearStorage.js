// 清除localStorage中的模拟数据
console.log('正在清除浏览器模拟数据...');

// 实际清除localStorage数据
localStorage.removeItem('users');
localStorage.removeItem('studentApplications');
localStorage.removeItem('user'); // 这是auth store使用的键
console.log('执行以下操作:');
console.log('1. 已清除 localStorage["users"] - 所有用户账户数据已清除');
console.log('2. 已清除 localStorage["studentApplications"] - 所有申请数据已清除');
console.log('3. 已清除 localStorage["user"] - 登录状态已清除');
console.log('\n数据已完全清除！');
console.log('- 项目重新启动后，将使用新的初始数据');
console.log('- admin账户将恢复为默认状态，用户名: admin, 密码: 123456');