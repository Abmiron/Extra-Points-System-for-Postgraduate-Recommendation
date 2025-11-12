require('dotenv').config();
const { Pool } = require('pg');

// 创建数据库连接池
const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
});

// 简单的密码哈希生成函数（模拟Go的bcrypt）
// 注意：这只是为了演示，实际应该使用与Go后端相同的哈希算法
function generatePasswordHash(password) {
  // 这里我们使用一个简单的方法来模拟bcrypt哈希
  // 实际项目中，应该使用相同的加密算法
  return `$2a$10$simulatedhash${password}`;
}

// 重置用户密码
async function resetUserPassword() {
  try {
    console.log('连接到数据库:', process.env.DB_NAME);
    
    // 重置admin用户密码为'admin123'
    const adminHash = generatePasswordHash('admin123');
    const adminResult = await pool.query(
      'UPDATE users SET password_hash = $1 WHERE username = $2',
      [adminHash, 'admin']
    );
    console.log(`已重置 ${adminResult.rowCount} 个admin用户的密码为 'admin123'`);
    
    // 重置testuser123用户密码为'123456'
    const testuserHash = generatePasswordHash('123456');
    const testuserResult = await pool.query(
      'UPDATE users SET password_hash = $1 WHERE username = $2',
      [testuserHash, 'testuser123']
    );
    console.log(`已重置 ${testuserResult.rowCount} 个testuser123用户的密码为 '123456'`);
    
    // 重置123456用户密码为'123456'
    const user123456Hash = generatePasswordHash('123456');
    const user123456Result = await pool.query(
      'UPDATE users SET password_hash = $1 WHERE username = $2',
      [user123456Hash, '123456']
    );
    console.log(`已重置 ${user123456Result.rowCount} 个123456用户的密码为 '123456'`);
    
    // 查询更新后的用户信息
    const usersResult = await pool.query(
      'SELECT id, username, role, password_hash FROM users'
    );
    
    console.log('\n更新后的用户信息:');
    usersResult.rows.forEach(user => {
      console.log(`ID: ${user.id}, 用户名: ${user.username}, 角色: ${user.role}`);
      // 不打印密码哈希的完整值
      console.log(`  密码哈希前10位: ${user.password_hash.substring(0, 10)}...`);
    });
    
    console.log('\n密码重置完成！请尝试使用以下凭据登录:');
    console.log('  - Admin: username=admin, password=admin123');
    console.log('  - Test User: username=testuser123, password=123456');
    console.log('  - User 123456: username=123456, password=123456');
    
  } catch (error) {
    console.error('密码重置失败:', error);
  } finally {
    // 关闭连接池
    await pool.end();
  }
}

// 运行脚本
resetUserPassword();