#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：检查数据库中的基础数据
"""

from extensions import db
from models import Faculty, Department, Major
from app import app

with app.app_context():
    print("检查数据库中的基础数据...")
    
    # 检查学院表
    print("\n1. 学院数据 (Faculty):")
    faculties = Faculty.query.all()
    if faculties:
        for faculty in faculties:
            print(f"   ID: {faculty.id}, 名称: {faculty.name}")
    else:
        print("   学院表中没有数据")
    
    # 检查系表
    print("\n2. 系数据 (Department):")
    departments = Department.query.all()
    if departments:
        for dept in departments:
            print(f"   ID: {dept.id}, 名称: {dept.name}, 所属学院ID: {dept.faculty_id}")
    else:
        print("   系表中没有数据")
    
    # 检查专业表
    print("\n3. 专业数据 (Major):")
    majors = Major.query.all()
    if majors:
        for major in majors:
            print(f"   ID: {major.id}, 名称: {major.name}, 所属系ID: {major.department_id}")
    else:
        print("   专业表中没有数据")
    
    # 检查是否有ID为1的专业
    print("\n4. 检查ID为1的专业是否存在:")
    major_1 = Major.query.get(1)
    if major_1:
        print(f"   存在ID为1的专业: {major_1.name}")
    else:
        print("   不存在ID为1的专业")
        
    # 如果没有数据，询问是否要创建示例数据
    if not faculties and not departments and not majors:
        print("\n5. 数据库中没有基础数据，是否要创建示例数据？")
        create_data = input("   输入 'y' 或 'n': ")
        
        if create_data.lower() == 'y':
            try:
                # 创建示例学院
                faculty = Faculty(name="计算机学院", description="计算机科学与技术学院")
                db.session.add(faculty)
                db.session.flush()  # 获取自动生成的ID
                
                # 创建示例系
                department = Department(name="计算机科学与技术系", faculty_id=faculty.id, description="计算机科学与技术系")
                db.session.add(department)
                db.session.flush()  # 获取自动生成的ID
                
                # 创建示例专业
                major = Major(name="计算机科学与技术", department_id=department.id, description="计算机科学与技术专业")
                db.session.add(major)
                
                db.session.commit()
                print("\n   示例数据创建成功！")
                print(f"   创建的学院ID: {faculty.id}, 系ID: {department.id}, 专业ID: {major.id}")
            except Exception as e:
                db.session.rollback()
                print(f"\n   创建示例数据失败: {e}")