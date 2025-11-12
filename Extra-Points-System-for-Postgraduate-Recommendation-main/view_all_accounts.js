const { Pool } = require('pg');
require('dotenv').config();

// 创建数据库连接池
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || '123456',
  database: process.env.DB_NAME || 'hd_golang',
  ssl: process.env.DB_SSLMODE === 'disable' ? false : undefined
});

// 查看所有用户账户信息
async function viewAllAccounts() {
  try {
    console.log('=== 所有用户账户信息 ===');
    console.log(`连接到数据库: ${process.env.DB_NAME || 'hd_golang'}`);
    console.log('');
    
    // 查询所有用户信息
    const usersResult = await pool.query(`
      SELECT id, username, role, status, created_at, 
             CASE WHEN role = 'student' THEN '学生' 
                  WHEN role = 'admin' THEN '管理员' 
                  WHEN role = 'teacher' THEN '教师' 
                  ELSE role END AS role_cn,
             CASE WHEN status = 'active' THEN '活跃' 
                  WHEN status = 'inactive' THEN '非活跃' 
                  ELSE status END AS status_cn
      FROM users 
      ORDER BY id
    `);
    
    if (usersResult.rowCount === 0) {
      console.log('数据库中没有用户记录');
      return;
    }
    
    // 打印用户数量统计
    console.log(`共找到 ${usersResult.rowCount} 个用户账户:`);
    console.log('');
    
    // 打印用户信息表格
    console.log('+-----+-------------+-----------+-----------+----------------------------+');
    console.log('| ID  | 用户名      | 角色      | 状态      | 创建时间                   |');
    console.log('+-----+-------------+-----------+-----------+----------------------------+');
    
    usersResult.rows.forEach(user => {
      const createTime = new Date(user.created_at).toLocaleString('zh-CN');
      console.log(
        `| ${String(user.id).padEnd(3)} | ${user.username.padEnd(11)} | ` +
        `${user.role_cn.padEnd(9)} | ${user.status_cn.padEnd(9)} | ` +
        `${createTime.padEnd(26)} |`
      );
    });
    
    console.log('+-----+-------------+-----------+-----------+----------------------------+');
    console.log('');
    
    // 统计角色分布
    const roleStats = {};
    usersResult.rows.forEach(user => {
      roleStats[user.role_cn] = (roleStats[user.role_cn] || 0) + 1;
    });
    
    console.log('角色分布统计:');
    Object.entries(roleStats).forEach(([role, count]) => {
      console.log(`- ${role}: ${count} 个`);
    });
    
    // 提示用户如何使用
    console.log('\n提示: 您可以随时运行此脚本来查看最新的用户账户信息');
    
  } catch (error) {
    console.error('查看账户信息时出错:', error);
  } finally {
    // 关闭连接池
    await pool.end();
  }
}

// 运行查看函数
viewAllAccounts();