const { Pool } = require('pg');
require('dotenv').config();

// 创建数据库连接池 - 首先连接到默认数据库以执行管理操作
const adminPool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || '123456',
  database: 'postgres', // 连接到默认数据库以执行管理操作
  ssl: process.env.DB_SSLMODE === 'disable' ? false : undefined
});

// 主函数
async function main() {
  try {
    console.log('=== 数据库操作开始 ===');
    
    // 1. 检查并删除postgres数据库
    console.log('\n1. 检查并删除postgres数据库...');
    await deletePostgresDatabase();
    
    // 2. 确保hd_golang数据库存在
    console.log('\n2. 确保hd_golang数据库存在...');
    await ensureDatabaseExists(process.env.DB_NAME || 'hd_golang');
    
    // 关闭admin连接
    await adminPool.end();
    
    // 3. 连接到hd_golang数据库并创建用户表
    console.log('\n3. 连接到hd_golang数据库并创建用户表...');
    await setupUserTables(process.env.DB_NAME || 'hd_golang');
    
    console.log('\n=== 数据库操作完成 ===');
  } catch (error) {
    console.error('操作失败:', error);
  }
}

// 删除postgres数据库（注意：这通常不是推荐的做法，因为postgres是默认维护数据库）
async function deletePostgresDatabase() {
  try {
    // 首先终止所有连接到postgres数据库的会话
    await adminPool.query(`
      SELECT pg_terminate_backend(pid) 
      FROM pg_stat_activity 
      WHERE datname = 'postgres' AND pid <> pg_backend_pid();
    `);
    
    // 尝试删除数据库（注意：这可能会失败，因为postgres通常是默认维护数据库）
    try {
      await adminPool.query('DROP DATABASE IF EXISTS postgres');
      console.log('postgres数据库已删除');
    } catch (e) {
      console.log('警告: 无法删除postgres数据库（这是正常的，因为它通常是默认维护数据库）:', e.message);
    }
  } catch (error) {
    console.error('删除postgres数据库失败:', error);
  }
}

// 确保数据库存在
async function ensureDatabaseExists(dbName) {
  try {
    // 检查数据库是否存在
    const result = await adminPool.query(
      "SELECT 1 FROM pg_database WHERE datname = $1",
      [dbName]
    );
    
    // 如果数据库不存在，则创建它
    if (result.rowCount === 0) {
      await adminPool.query(`CREATE DATABASE ${dbName}`);
      console.log(`数据库 ${dbName} 已创建`);
    } else {
      console.log(`数据库 ${dbName} 已存在`);
    }
  } catch (error) {
    console.error(`确保数据库 ${dbName} 存在时出错:`, error);
  }
}

// 设置用户表
async function setupUserTables(dbName) {
  // 创建新的连接池连接到指定数据库
  const pool = new Pool({
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || '123456',
    database: dbName,
    ssl: process.env.DB_SSLMODE === 'disable' ? false : undefined
  });
  
  try {
    // 创建用户表（如果不存在）
    await pool.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
      );
    `);
    console.log('users表已创建或已存在');
    
    // 检查是否有用户记录
    const usersResult = await pool.query('SELECT id, username, role, status, created_at FROM users');
    console.log(`\n当前数据库中有 ${usersResult.rowCount} 个用户账户:`);
    
    if (usersResult.rowCount > 0) {
      usersResult.rows.forEach(user => {
        console.log(`- ID: ${user.id}, 用户名: ${user.username}, 角色: ${user.role}, 状态: ${user.status}`);
      });
    } else {
      console.log('警告: 数据库中没有用户记录');
      
      // 提示用户如何添加用户
      console.log('\n提示: 您可以使用项目中的其他脚本来添加用户，或者运行以下命令:');
      console.log('node reset_password.js');
    }
    
    // 添加一个方便查看用户的函数
    await pool.query(`
      CREATE OR REPLACE FUNCTION get_all_users()
      RETURNS TABLE(id INT, username VARCHAR, role VARCHAR, status VARCHAR, created_at TIMESTAMP)
      LANGUAGE sql
      AS $$
        SELECT id, username, role, status, created_at FROM users ORDER BY id;
      $$;
    `);
    console.log('\n已创建get_all_users()函数，可用于快速查看所有用户');
    
  } catch (error) {
    console.error('设置用户表时出错:', error);
  } finally {
    // 关闭连接池
    await pool.end();
  }
}

// 运行主函数
main();