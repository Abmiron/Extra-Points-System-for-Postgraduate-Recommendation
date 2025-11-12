const { Pool } = require('pg');
require('dotenv').config();

// 创建数据库连接池
const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  ssl: process.env.DB_SSLMODE === 'disable' ? false : undefined
});

async function checkUsers() {
  try {
    console.log(`连接到数据库: ${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_NAME}`);
    
    // 检查数据库中是否存在users表
    const tableCheck = await pool.query(
      "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
    );
    
    if (!tableCheck.rows[0].exists) {
      console.log('错误: users表不存在！');
      return;
    }
    
    console.log('\nusers表存在，开始查询用户数据...');
    
    // 查询users表中的所有数据
    const usersResult = await pool.query('SELECT * FROM users');
    
    if (usersResult.rows.length === 0) {
      console.log('\n结果: users表中没有找到任何用户数据！');
    } else {
      console.log(`\n结果: 找到 ${usersResult.rows.length} 个用户记录:`);
      console.log('用户列表:');
      usersResult.rows.forEach((user, index) => {
        console.log(`\n用户 ${index + 1}:`);
        console.log(`  ID: ${user.id}`);
        console.log(`  用户名: ${user.username}`);
        console.log(`  姓名: ${user.name || '未设置'}`);
        console.log(`  邮箱: ${user.email || '未设置'}`);
        console.log(`  密码哈希: ${user.password_hash.substring(0, 20)}...`);
        console.log(`  创建时间: ${user.created_at}`);
      });
    }
    
    // 检查其他可能存储用户信息的表
    console.log('\n检查其他可能的用户相关表...');
    const tablesResult = await pool.query(
      "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    );
    
    console.log('\n数据库中的表列表:');
    tablesResult.rows.forEach((table, index) => {
      console.log(`  ${index + 1}. ${table.table_name}`);
    });
    
  } catch (error) {
    console.error('数据库操作错误:', error.message);
  } finally {
    await pool.end();
  }
}

// 执行检查
checkUsers();