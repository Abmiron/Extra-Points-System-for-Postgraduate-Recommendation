const { Pool } = require('pg');
const dotenv = require('dotenv');

// 加载环境变量
dotenv.config();

// 创建数据库连接池
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'admin',
  database: process.env.DB_NAME || 'postgres',
  ssl: process.env.DB_SSL === 'true'
});

/**
 * 查询数据库中的所有账户信息
 */
async function viewDatabaseAccounts() {
  try {
    console.log('开始查询数据库账户信息...');
    
    // 先查看users表结构
    console.log('\n=== 检查users表结构 ===');
    const tableStructure = await pool.query(
      "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position"
    );
    console.log('Users表字段:');
    tableStructure.rows.forEach(col => {
      console.log(`  ${col.column_name} (${col.data_type})`);
    });
    
    // 查询用户表所有字段
    const usersResult = await pool.query('SELECT * FROM users');
    console.log('\n=== 用户表 (users) ===');
    console.log(`共找到 ${usersResult.rows.length} 个用户：`);
    usersResult.rows.forEach(user => {
      console.log(`  用户 ${user.username} 信息:`);
      console.log(`    ID: ${user.id}`);
      console.log(`    用户名: ${user.username}`);
      console.log(`    角色: ${user.role}`);
      console.log(`    状态: ${user.status}`);
      if (user.password_hash) {
        console.log(`    密码哈希: ${user.password_hash.substring(0, 15)}...`);
      }
      if (user.created_at) {
        console.log(`    创建时间: ${new Date(user.created_at).toLocaleString()}`);
      }
      if (user.updated_at) {
        console.log(`    更新时间: ${new Date(user.updated_at).toLocaleString()}`);
      }
      if (user.last_login) {
        console.log(`    最后登录: ${new Date(user.last_login).toLocaleString()}`);
      }
      console.log();
    });
    
    // 查询学生表
    const studentsResult = await pool.query('SELECT * FROM students');
    console.log('\n=== 学生表 (students) ===');
    console.log(`共找到 ${studentsResult.rows.length} 条学生记录：`);
    studentsResult.rows.forEach(student => {
      console.log(`  用户ID: ${student.user_id}, 学号: ${student.student_id}, 姓名: ${student.name}`);
      console.log(`      学院: ${student.department}, 专业: ${student.major}`);
    });
    
    // 查询管理员表
    const adminsResult = await pool.query('SELECT * FROM admins');
    console.log('\n=== 管理员表 (admins) ===');
    console.log(`共找到 ${adminsResult.rows.length} 条管理员记录：`);
    adminsResult.rows.forEach(admin => {
      console.log(`  用户ID: ${admin.user_id}, 姓名: ${admin.name}, 学院: ${admin.department}`);
    });
    
    // 查询教师表
    const teachersResult = await pool.query('SELECT * FROM teachers');
    console.log('\n=== 教师表 (teachers) ===');
    console.log(`共找到 ${teachersResult.rows.length} 条教师记录：`);
    teachersResult.rows.forEach(teacher => {
      console.log(`  用户ID: ${teacher.user_id}, 姓名: ${teacher.name}, 学院: ${teacher.department}`);
    });
    
    console.log('\n数据库账户查询完成！');
    
  } catch (error) {
    console.error('查询数据库时出错:', error.message);
  } finally {
    // 关闭连接池
    await pool.end();
  }
}

// 执行查询
viewDatabaseAccounts();