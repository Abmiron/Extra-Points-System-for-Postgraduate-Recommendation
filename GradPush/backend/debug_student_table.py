#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细调试脚本：检查Student表并尝试手动创建记录
"""

from extensions import db
from models import Student, User
from app import app

with app.app_context():
    print("详细调试：Student表操作")
    print("=" * 50)
    
    # 1. 查看Student表结构
    print("\n1. Student表结构:")
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    columns = inspector.get_columns('student')
    for column in columns:
        print(f"   {column['name']}: {column['type']} (nullable: {column['nullable']})")
    
    # 2. 查看Student表中的所有记录
    print("\n2. Student表中的所有记录:")
    students = Student.query.all()
    if students:
        for student in students:
            print(f"   ID: {student.id}, 学号: {student.student_id}, 姓名: {student.student_name}")
    else:
        print("   Student表中没有记录")
    
    # 3. 尝试手动创建Student记录
    print("\n3. 尝试手动创建Student记录:")
    try:
        new_student = Student(
            student_id='debug_student',
            student_name='调试学生',
            faculty_id=84,
            department_id=163,
            major_id=269
        )
        db.session.add(new_student)
        db.session.flush()  # 立即执行SQL
        print("   ✓ 成功添加Student记录到会话")
        print(f"   新学生ID: {new_student.id}")
        print(f"   新学生学号: {new_student.student_id}")
        
        # 提交事务
        db.session.commit()
        print("   ✓ 成功提交事务")
        
        # 验证是否存在
        check_student = Student.query.filter_by(student_id='debug_student').first()
        if check_student:
            print("   ✓ 从数据库中成功查询到新创建的学生记录")
        else:
            print("   ✗ 从数据库中查询不到新创建的学生记录")
            
    except Exception as e:
        db.session.rollback()
        print(f"   ✗ 创建Student记录失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. 查看User表中teststudent001的详细信息
    print("\n4. User表中teststudent001的详细信息:")
    user = User.query.filter_by(username='teststudent001').first()
    if user:
        print(f"   ID: {user.id}")
        print(f"   username: {user.username}")
        print(f"   name: {user.name}")
        print(f"   role: {user.role}")
        print(f"   faculty_id: {user.faculty_id}")
        print(f"   department_id: {user.department_id}")
        print(f"   major_id: {user.major_id}")
        print(f"   student_id: {user.student_id}")
        print(f"   status: {user.status}")
        print(f"   created_at: {user.created_at}")
    else:
        print("   未找到该用户")
    
    # 5. 清理测试数据
    print("\n5. 清理测试数据:")
    debug_student = Student.query.filter_by(student_id='debug_student').first()
    if debug_student:
        db.session.delete(debug_student)
        db.session.commit()
        print("   ✓ 已删除调试学生记录")
    else:
        print("   ✗ 未找到调试学生记录")