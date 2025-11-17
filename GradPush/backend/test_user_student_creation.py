#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：直接测试User和Student的创建和关联
"""

from extensions import db
from models import User, Student
from app import app

with app.app_context():
    print("直接测试User和Student的创建和关联")
    print("=" * 50)
    
    # 清理之前的测试数据
    print("\n1. 清理之前的测试数据:")
    user = User.query.filter_by(username='test_direct').first()
    if user:
        db.session.delete(user)
    student = Student.query.filter_by(student_id='test_direct').first()
    if student:
        db.session.delete(student)
    db.session.commit()
    print("   ✓ 已清理测试数据")
    
    # 测试1: 先创建Student，再创建User
    print("\n2. 测试1: 先创建Student，再创建User")
    try:
        # 创建Student记录
        student = Student(
            student_id='test_direct',
            student_name='直接测试学生',
            faculty_id=84,
            department_id=163,
            major_id=269
        )
        db.session.add(student)
        db.session.flush()
        print(f"   ✓ Student创建成功: {student.student_id}")
        
        # 创建User记录
        user = User(
            username='test_direct',
            name='直接测试学生',
            role='student',
            faculty_id=84,
            department_id=163,
            major_id=269,
            student_id='test_direct'
        )
        user.set_password('123456')
        db.session.add(user)
        db.session.flush()
        print(f"   ✓ User创建成功: {user.username}")
        print(f"   ✓ User.student_id: {user.student_id}")
        
        # 提交事务
        db.session.commit()
        print("   ✓ 事务提交成功")
        
        # 验证
        check_user = User.query.filter_by(username='test_direct').first()
        check_student = Student.query.filter_by(student_id='test_direct').first()
        if check_user and check_student:
            print(f"   ✓ 验证成功 - User.student_id: {check_user.student_id}")
            print(f"   ✓ 验证成功 - Student存在: {check_student.student_id}")
        else:
            print("   ✗ 验证失败")
            
    except Exception as e:
        db.session.rollback()
        print(f"   ✗ 测试1失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 清理测试数据
    user = User.query.filter_by(username='test_direct').first()
    if user:
        db.session.delete(user)
    student = Student.query.filter_by(student_id='test_direct').first()
    if student:
        db.session.delete(student)
    db.session.commit()
    
    # 测试2: 直接在注册流程中添加调试信息
    print("\n3. 测试2: 模拟注册流程并添加详细调试")
    from flask import request
    
    # 模拟请求数据
    data = {
        'username': 'test_register',
        'name': '注册测试学生',
        'password': '123456',
        'role': 'student',
        'facultyId': 84,
        'departmentId': 163,
        'majorId': 269
    }
    
    try:
        from models import Faculty, Department, Major
        
        # 模拟注册逻辑
        faculty_id = data.get('facultyId')
        department_id = data.get('departmentId')
        major_id = data.get('majorId')
        
        # 学生角色验证
        if data['role'] == 'student':
            # 验证关联ID是否存在
            faculty = Faculty.query.get(faculty_id)
            department = Department.query.get(department_id)
            major = Major.query.get(major_id)
            
            if not faculty:
                print("   ✗ 学院不存在")
                exit()
            if not department:
                print("   ✗ 系不存在")
                exit()
            if not major:
                print("   ✗ 专业不存在")
                exit()
        
        # 开始事务
        db.session.begin()
        
        # 学生角色需要先处理Student记录
        student_id = None
        if data['role'] == 'student':
            print("   ✓ 处理学生角色")
            # 检查是否已存在对应的Student记录
            existing_student = Student.query.filter_by(student_id=data['username']).first()
            if not existing_student:
                print("   ✓ 创建新的Student记录")
                # 如果不存在，创建新的Student记录
                new_student = Student(
                    student_id=data['username'],
                    student_name=data['name'],
                    faculty_id=faculty_id,
                    department_id=department_id,
                    major_id=major_id
                )
                db.session.add(new_student)
                # 立即刷新以获取新创建的记录
                db.session.flush()
                print(f"   ✓ Student记录已添加到会话: {new_student.student_id}")
            student_id = data['username']
            print(f"   ✓ 设置student_id为: {student_id}")
        
        print(f"   ✓ 创建User前的student_id值: {student_id}")
        
        # 创建新用户
        new_user = User(
            username=data['username'],
            name=data['name'],
            role=data['role'],
            avatar='/images/default-avatar.jpg',
            faculty_id=faculty_id,
            department_id=department_id if data['role'] == 'student' else None,
            major_id=major_id if data['role'] == 'student' else None,
            student_id=student_id,
            email='',
            phone='',
            role_name='审核员' if data['role'] == 'teacher' else None
        )
        
        # 设置密码（哈希）
        new_user.set_password(data.get('password', '123456'))
        print(f"   ✓ 创建User对象，student_id: {new_user.student_id}")

        db.session.add(new_user)
        print(f"   ✓ User添加到会话后，student_id: {new_user.student_id}")
        
        # 提交事务
        db.session.commit()
        print(f"   ✓ 事务提交后，student_id: {new_user.student_id}")
        
        # 验证最终结果
        final_user = User.query.filter_by(username=data['username']).first()
        final_student = Student.query.filter_by(student_id=data['username']).first()
        
        print(f"\n4. 最终验证:")
        print(f"   ✓ User记录: {final_user.username}")
        print(f"   ✓ User.student_id: {final_user.student_id}")
        print(f"   ✓ Student记录: {final_student.student_id if final_student else 'None'}")
        
        if final_user.student_id and final_student:
            print("   ✓ 注册成功，学生记录和用户记录都已创建并关联")
        else:
            print("   ✗ 注册失败，学生记录或用户关联存在问题")
            
    except Exception as e:
        # 发生异常时回滚事务
        db.session.rollback()
        print(f"   ✗ 测试2失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 清理测试数据
    user = User.query.filter_by(username='test_register').first()
    if user:
        db.session.delete(user)
    student = Student.query.filter_by(student_id='test_register').first()
    if student:
        db.session.delete(student)
    db.session.commit()
    print("\n5. 测试数据已清理")