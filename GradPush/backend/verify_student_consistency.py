#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证User模型和Student模型中学生会数据的一致性
"""
from app import app
from extensions import db
from models import User, Student

# 创建验证函数
def verify_student_consistency():
    with app.app_context():
        print("正在验证User模型和Student模型中学生会数据的一致性...")
        
        # 获取所有学生用户
        user_students = User.query.filter_by(role='student').all()
        print(f"User模型中的学生用户数量: {len(user_students)}")
        
        # 获取所有Student模型数据
        students = Student.query.all()
        print(f"Student模型中的学生数据数量: {len(students)}")
        
        # 创建映射便于对比
        student_id_to_user = {user.student_id: user for user in user_students}
        student_id_to_student = {student.student_id: student for student in students}
        
        # 检查学生学号是否完全一致
        user_student_ids = set(student_id_to_user.keys())
        student_ids = set(student_id_to_student.keys())
        
        print("\n=== 1. 学号一致性检查 ===")
        if user_student_ids == student_ids:
            print("✓ 所有学生学号在两个模型中完全一致")
        else:
            missing_in_user = student_ids - user_student_ids
            missing_in_student = user_student_ids - student_ids
            if missing_in_user:
                print(f"✗ Student模型中存在但User模型中不存在的学号: {missing_in_user}")
            if missing_in_student:
                print(f"✗ User模型中存在但Student模型中不存在的学号: {missing_in_student}")
        
        # 检查每个学生的详细信息是否一致
        print("\n=== 2. 学生信息一致性检查 ===")
        consistent_count = 0
        inconsistent_count = 0
        
        for student_id, user in student_id_to_user.items():
            if student_id not in student_id_to_student:
                continue
                
            student = student_id_to_student[student_id]
            
            # 检查关键字段是否一致
            name_match = user.name == student.student_name
            faculty_match = user.faculty_id == student.faculty_id
            dept_match = user.department_id == student.department_id
            major_match = user.major_id == student.major_id
            
            if name_match and faculty_match and dept_match and major_match:
                consistent_count += 1
            else:
                inconsistent_count += 1
                print(f"\n学号: {student_id} 信息不一致:")
                if not name_match:
                    print(f"  姓名: User={user.name}, Student={student.student_name}")
                if not faculty_match:
                    print(f"  学院ID: User={user.faculty_id}, Student={student.faculty_id}")
                if not dept_match:
                    print(f"  系ID: User={user.department_id}, Student={student.department_id}")
                if not major_match:
                    print(f"  专业ID: User={user.major_id}, Student={student.major_id}")
        
        print(f"\n一致的学生数量: {consistent_count}")
        print(f"不一致的学生数量: {inconsistent_count}")
        
        # 总结
        print("\n=== 验证结果总结 ===")
        if len(user_students) == len(students) and user_student_ids == student_ids and inconsistent_count == 0:
            print("🎉 所有学生数据在User模型和Student模型中完全一致！")
        else:
            print("⚠️  发现数据不一致问题，请检查！")

if __name__ == "__main__":
    verify_student_consistency()