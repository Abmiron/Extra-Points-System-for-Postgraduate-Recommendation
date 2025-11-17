#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证测试学生用户teststudent003的注册情况
检查用户和学生记录是否都正确创建，以及两者是否正确关联
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 直接导入app实例
from app import app
from models import User, Student, db

def verify_test_user():
    """验证测试用户的注册情况"""
    
    with app.app_context():
        # 查询用户记录
        user = User.query.filter_by(username='teststudent003').first()
        print(f"\n=== 用户记录查询结果 ===")
        if user:
            print(f"用户存在: {user.username}")
            print(f"角色: {user.role}")
            print(f"姓名: {user.name}")
            print(f"学院ID: {user.faculty_id}")
            print(f"系ID: {user.department_id}")
            print(f"专业ID: {user.major_id}")
            print(f"学生ID: {user.student_id}")
        else:
            print("用户不存在")
        
        # 查询学生记录
        student = Student.query.filter_by(student_id='teststudent003').first()
        print(f"\n=== 学生记录查询结果 ===")
        if student:
            print(f"学生存在: {student.student_id}")
            print(f"姓名: {student.student_name}")
            print(f"学院ID: {student.faculty_id}")
            print(f"系ID: {student.department_id}")
            print(f"专业ID: {student.major_id}")
        else:
            print("学生不存在")
        
        # 检查关联关系
        print(f"\n=== 关联关系检查 ===")
        if user and user.student_id and student:
            print("✅ 用户和学生记录正确关联")
        elif user and not user.student_id:
            print("❌ 用户存在，但student_id为空")
        elif not user and student:
            print("❌ 学生存在，但用户不存在")
        else:
            print("❌ 用户和学生记录都不存在")
        
        # 列出所有学生记录
        print(f"\n=== 所有学生记录列表 ===")
        all_students = Student.query.all()
        if all_students:
            print(f"共有 {len(all_students)} 条学生记录")
            for s in all_students:
                print(f"- {s.student_id} (姓名: {s.student_name}, 专业: {s.major_id})")
        else:
            print("没有学生记录")

def cleanup():
    """清理测试数据"""
    
    with app.app_context():
        # 删除测试用户
        user = User.query.filter_by(username='teststudent003').first()
        if user:
            db.session.delete(user)
            print(f"已删除用户: {user.username}")
        
        # 删除测试学生
        student = Student.query.filter_by(student_id='teststudent003').first()
        if student:
            db.session.delete(student)
            print(f"已删除学生: {student.student_id}")
        
        db.session.commit()

if __name__ == '__main__':
    verify_test_user()
    # cleanup()  # 取消注释以清理测试数据