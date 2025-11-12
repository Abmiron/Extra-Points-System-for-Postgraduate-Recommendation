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

// 验证数据库中的用户信息
async function verifyDatabaseUsers() {
  try {
    console.log('=== 数据库账户验证 ===');
    console.log('连接到数据库:', process.env.DB_NAME);
    
    // 1. 列出所有用户表
    console.log('\n1. 数据库中的表:');
    const tablesResult = await pool.query(
      "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    );
    tablesResult.rows.forEach((table, index) => {
      console.log(`${index + 1}. ${table.table_name}`);
    });
    
    // 2. 查询users表的结构
    console.log('\n2. users表结构:');
    const usersTableStructure = await pool.query(
      "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users'"
    );
    usersTableStructure.rows.forEach(col => {
      console.log(`  - ${col.column_name} (${col.data_type})`);
    });
    
    // 3. 查询users表中的所有用户
    console.log('\n3. users表中的所有用户:');
    const usersResult = await pool.query(
      'SELECT id, username, role, status, created_at FROM users ORDER BY id'
    );
    console.log(`找到 ${usersResult.rowCount} 个用户记录:`);
    usersResult.rows.forEach(user => {
      console.log(`  ID: ${user.id}`);
      console.log(`  用户名: ${user.username}`);
      console.log(`  角色: ${user.role}`);
      console.log(`  状态: ${user.status}`);
      console.log(`  创建时间: ${user.created_at}`);
      console.log('  --------------------');
    });
    
    // 4. 查询students表中的记录
    console.log('\n4. students表中的记录:');
    const studentsResult = await pool.query(
      'SELECT * FROM students ORDER BY id'
    );
    console.log(`找到 ${studentsResult.rowCount} 个学生记录:`);
    studentsResult.rows.forEach(student => {
      console.log(`  ID: ${student.id}`);
      console.log(`  用户ID: ${student.user_id}`);
      console.log(`  学号: ${student.student_id}`);
      console.log(`  姓名: ${student.name}`);
      console.log(`  系别: ${student.department}`);
      console.log(`  专业: ${student.major}`);
      console.log('  --------------------');
    });
    
    // 5. 查询admins表中的记录
    console.log('\n5. admins表中的记录:');
    try {
      const adminsResult = await pool.query(
        'SELECT * FROM admins ORDER BY id'
      );
      console.log(`找到 ${adminsResult.rowCount} 个管理员记录:`);
      adminsResult.rows.forEach(admin => {
        console.log(`  ID: ${admin.id}`);
        console.log(`  用户ID: ${admin.user_id}`);
        console.log(`  姓名: ${admin.name}`);
        console.log('  --------------------');
      });
    } catch (e) {
      console.log(`  错误: ${e.message}`);
    }
    
    // 6. 查询teachers表中的记录
    console.log('\n6. teachers表中的记录:');
    try {
      const teachersResult = await pool.query(
        'SELECT * FROM teachers ORDER BY id'
      );
      console.log(`找到 ${teachersResult.rowCount} 个教师记录:`);
      teachersResult.rows.forEach(teacher => {
        console.log(`  ID: ${teacher.id}`);
        console.log(`  用户ID: ${teacher.user_id}`);
        console.log(`  姓名: ${teacher.name}`);
        console.log(`  系别: ${teacher.department}`);
        console.log('  --------------------');
      });
    } catch (e) {
      console.log(`  错误: ${e.message}`);
    }
    
    // 7. 检查数据库连接和权限
    console.log('\n7. 数据库连接和权限检查:');
    console.log('  ✅ 成功连接到数据库');
    console.log('  ✅ 成功读取用户表');
    console.log('  ✅ 成功读取学生表');
    
    console.log('\n=== 验证总结 ===');
    console.log(`数据库中共有 ${usersResult.rowCount} 个用户账户`);
    console.log(`其中学生账户: ${studentsResult.rowCount} 个`);
    console.log('账户信息已成功从数据库中读取，说明数据库中的账户是可见的。');
    console.log('如果登录失败，可能是密码哈希格式不匹配或API实现问题。');
    
  } catch (error) {
    console.error('数据库验证失败:', error);
  } finally {
    // 关闭连接池
    await pool.end();
  }
}

// 运行脚本
verifyDatabaseUsers();