const { execSync } = require('child_process');

console.log('=== 检查服务器状态 ===\n');

// 检查端口使用情况
console.log('--- 端口使用情况 ---');
try {
  // Windows系统使用netstat命令
  const netstatOutput = execSync('netstat -ano | findstr "9001 9004 5432"', { encoding: 'utf8' });
  console.log(netstatOutput);
} catch (error) {
  console.log('未找到相关端口占用或命令执行失败');
}

// 检查正在运行的Go进程
console.log('\n--- Go进程运行状态 ---');
try {
  const tasklistOutput = execSync('tasklist | findstr "app.exe main.exe"', { encoding: 'utf8' });
  console.log(tasklistOutput);
} catch (error) {
  console.log('未找到相关Go进程或命令执行失败');
}

// 检查数据库连接
console.log('\n--- 检查数据库连接 ---');
try {
  const psqlCheck = execSync('psql --version', { encoding: 'utf8' });
  console.log('PostgreSQL客户端可用:', psqlCheck.trim());
} catch (error) {
  console.log('PostgreSQL客户端不可用或未安装');
}

// 显示端口配置对比
console.log('\n--- 配置信息对比 ---');
console.log('config.go中配置的服务器端口: 9004');
console.log('backend.log中显示的服务器端口: 9001');
console.log('config.go中配置的数据库密码: 123456');
console.log('JavaScript脚本中使用的数据库密码: admin');

console.log('\n=== 检查完成 ===');
console.log('可能的问题：');
console.log('1. 端口配置不一致 (9004 vs 9001)');
console.log('2. 数据库密码配置不一致 (123456 vs admin)');
console.log('3. 可能存在多个实例或旧实例未关闭');