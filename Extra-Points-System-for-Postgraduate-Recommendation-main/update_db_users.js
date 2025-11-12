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

// 查询现有用户并为学生用户添加缺失的student_id
async function checkAndUpdateUsers() {
  try {
    console.log('连接到数据库:', process.env.DB_NAME);
    
    // 查询所有用户
    const usersResult = await pool.query('SELECT id, username, role FROM users');
    console.log(`找到 ${usersResult.rows.length} 个用户`);
    
    // 为每个用户打印信息
    usersResult.rows.forEach(user => {
      console.log(`用户ID: ${user.id}, 用户名: ${user.username}, 角色: ${user.role}`);
    });
    
    // 查询学生表
    const studentsResult = await pool.query('SELECT * FROM students');
    console.log(`\n学生表中有 ${studentsResult.rows.length} 条记录`);
    studentsResult.rows.forEach(student => {
      console.log(`学生ID: ${student.id}, 用户ID: ${student.user_id}, 学号: ${student.student_id}, 姓名: ${student.name}`);
    });
    
    // 检查并修复缺失student_id的记录
    console.log('\n开始检查并修复缺失student_id的记录...');
    
    // 首先为学生表中student_id为null的记录设置值
    const fixStudentsResult = await pool.query(`
      UPDATE students 
      SET student_id = (SELECT username FROM users WHERE users.id = students.user_id)
      WHERE student_id IS NULL
      RETURNING id, user_id, student_id
    `);
    
    console.log(`修复了 ${fixStudentsResult.rowCount} 条学生记录`);
    
    // 检查是否有用户在users表但不在对应的角色表中
    console.log('\n检查孤立用户...');
    
    // 查找在users表中角色为student但不在students表中的用户
    const orphanStudentsResult = await pool.query(`
      SELECT u.id, u.username, u.role 
      FROM users u 
      LEFT JOIN students s ON u.id = s.user_id 
      WHERE u.role = 'student' AND s.user_id IS NULL
    `);
    
    console.log(`找到 ${orphanStudentsResult.rows.length} 个孤立的学生用户`);
    
    // 为这些用户创建对应的学生记录
    for (const user of orphanStudentsResult.rows) {
      console.log(`为用户 ${user.username} (ID: ${user.id}) 创建学生记录`);
      await pool.query(`
        INSERT INTO students (user_id, student_id, name, department, major) 
        VALUES ($1, $2, $2, '计算机科学与技术系', '计算机科学与技术')
      `, [user.id, user.username]);
    }
    
    console.log('\n数据库检查和修复完成!');
    
    // 再次查询所有用户和学生记录以验证
    console.log('\n验证修复结果:');
    const updatedStudentsResult = await pool.query('SELECT * FROM students');
    console.log(`更新后的学生表中有 ${updatedStudentsResult.rows.length} 条记录`);
    
    // 查询完整的用户信息（连接users和students表）
    const fullUserInfo = await pool.query(`
      SELECT u.id, u.username, u.role, u.status, s.student_id, s.name 
      FROM users u 
      LEFT JOIN students s ON u.id = s.user_id 
      ORDER BY u.id
    `);
    
    console.log('\n完整的用户信息:');
    fullUserInfo.rows.forEach(user => {
      console.log(`ID: ${user.id}, 用户名: ${user.username}, 角色: ${user.role}, 状态: ${user.status}, 学号: ${user.student_id || 'N/A'}, 姓名: ${user.name || 'N/A'}`);
    });
    
  } catch (error) {
    console.error('数据库操作失败:', error);
  } finally {
    // 关闭连接池
    await pool.end();
  }
}

// 运行脚本
checkAndUpdateUsers();