#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证脚本：检查注册的用户和学生记录
"""

from extensions import db
from models import User, Student
from app import app

with app.app_context():
    print("验证注册的用户和学生记录...")
    
    # 检查用户记录
    print("\n1. 用户记录 (User):")
    user = User.query.filter_by(username='teststudent001').first()
    if user:
        print(f"   用户名: {user.username}")
        print(f"   姓名: {user.name}")
        print(f"   角色: {user.role}")
        print(f"   学院ID: {user.faculty_id}")
        print(f"   系ID: {user.department_id}")
        print(f"   专业ID: {user.major_id}")
        print(f"   学生ID: {user.student_id}")
        print(f"   状态: {user.status}")
    else:
        print("   未找到用户记录")
    
    # 检查学生记录
    print("\n2. 学生记录 (Student):")
    student = Student.query.filter_by(student_id='teststudent001').first()
    if student:
        print(f"   学号: {student.student_id}")
        print(f"   姓名: {student.student_name}")
        print(f"   学院ID: {student.faculty_id}")
        print(f"   系ID: {student.department_id}")
        print(f"   专业ID: {student.major_id}")
    else:
        print("   未找到学生记录")
    
    # 检查用户和学生的关联
    print("\n3. 用户和学生关联:")
    if user and user.student:
        print(f"   用户 {user.username} 成功关联到学生 {user.student.student_id}")
    else:
        print("   用户和学生关联失败")