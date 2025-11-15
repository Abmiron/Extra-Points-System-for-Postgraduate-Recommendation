# -*- coding: utf-8 -*-
"""
添加测试数据脚本

该脚本用于添加测试数据到数据库，以便测试审核统计功能
"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User, Application, AcademicSpecialtyDetail, ComprehensivePerformanceDetail, StudentEvaluation, Student
from datetime import datetime, timedelta
import random

with app.app_context():
    try:
        # 创建一些教师用户
        teacher_usernames = ['teacher1', 'teacher2']
        teachers = []
        for i, username in enumerate(teacher_usernames):
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                teacher = User(username=username, name=['张老师', '李老师'][i], role='teacher', faculty=['计算机学院', '电子工程学院'][i], password='123456')
                teachers.append(teacher)
        
        # 创建一些学生用户
        student_usernames = ['student1', 'student2', 'student3', 'student4']
        students = []
        for i, username in enumerate(student_usernames):
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                student = User(username=username, name=['小明', '小红', '小刚', '小丽'][i], role='student', faculty=['计算机学院', '电子工程学院', '计算机学院', '电子工程学院'][i], major=['计算机科学与技术', '电子信息工程', '计算机科学与技术', '电子信息工程'][i], password='123456')
                students.append(student)
        
        # 添加用户到数据库
        if teachers + students:
            for user in teachers + students:
                db.session.add(user)
            db.session.commit()
            print("用户数据添加成功!")
        else:
            print("用户数据已存在，跳过添加!")
        
        # 检查是否已有申请数据，如果有就跳过添加
        existing_applications = Application.query.count()
        if existing_applications > 0:
            print("申请数据已存在，跳过添加!")
        else:
            # 创建一些申请数据
            applications = []
            
            # 创建待审核的申请
            for i in range(5):
                app = Application(
                    student_id=f'student{i%2+1}',
                    student_name=['小明', '小红'][i%2],
                    department=['计算机学院', '电子工程学院'][i%2],
                    major=['计算机科学与技术', '电子信息工程'][i%2],
                    application_type='academic',
                    project_name=f'学术项目{i+1}',
                    status='pending',
                    academic_type='paper',
                    performance_type='first_author',
                    description=f'这是第{i+1}个学术项目申请',
                    self_score=random.uniform(5, 15),
                    award_date=datetime.utcnow().date() - timedelta(days=random.randint(1, 30)),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 10))
                )
                applications.append(app)
            
            # 创建已审核的申请
            for i in range(15):
                status = random.choice(['approved', 'rejected'])
                reviewed_by = f'teacher{i%2+1}'
                reviewed_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
                student_idx = i % 4  # 使用4个学生
                
                # 确保部分申请是本月的
                if i < 8:
                    reviewed_at = datetime.utcnow() - timedelta(days=random.randint(1, 15))
                
                app = Application(
                    student_id=f'student{student_idx+1}',
                    student_name=['小明', '小红', '小刚', '小丽'][student_idx],
                    department=['计算机学院', '电子工程学院', '计算机学院', '电子工程学院'][student_idx],
                    major=['计算机科学与技术', '电子信息工程', '计算机科学与技术', '电子信息工程'][student_idx],
                    application_type=random.choice(['academic', 'comprehensive']),
                    project_name=f'项目{i+1}',
                    status=status,
                    academic_type=random.choice(['paper', 'competition', 'patent']),
                    performance_type=random.choice(['first_author', 'second_author', 'participant']),
                    description=f'这是第{i+1}个申请',
                    self_score=random.uniform(5, 15),
                    award_date=datetime.utcnow().date() - timedelta(days=random.randint(1, 30)),
                    final_score=random.uniform(60, 100) if status == 'approved' else None,
                    review_comment=f'审核意见{i+1}',
                    reviewed_at=reviewed_at,
                    reviewed_by=reviewed_by,
                    created_at=reviewed_at - timedelta(days=random.randint(1, 5))
                )
                applications.append(app)
            
            # 添加申请到数据库
            for app in applications:
                db.session.add(app)
            db.session.commit()
            print("申请数据添加成功!")
        
        # 验证数据添加
        total_applications = Application.query.count()
        pending_count = Application.query.filter_by(status='pending').count()
        reviewed_count = Application.query.filter(Application.status.in_(['approved', 'rejected'])).count()
        
        print(f"总申请数: {total_applications}")
        print(f"待审核数: {pending_count}")
        print(f"已审核数: {reviewed_count}")
        
        # 添加学生基本信息
        students_basic_data = [
            {'student_id': 'student1', 'student_name': '小明', 'gender': '男', 'department': '计算机学院', 'major': '计算机科学与技术', 'cet4_score': 425, 'cet6_score': 450, 'gpa': 3.8, 'academic_score': 92.5, 'academic_weighted': 74.0, 'ranking': 1, 'total_students': 100},
            {'student_id': 'student2', 'student_name': '小红', 'gender': '女', 'department': '电子工程学院', 'major': '电子信息工程', 'cet4_score': 450, 'cet6_score': 480, 'gpa': 3.9, 'academic_score': 95.0, 'academic_weighted': 76.0, 'ranking': 2, 'total_students': 100},
            {'student_id': 'student3', 'student_name': '小刚', 'gender': '男', 'department': '计算机学院', 'major': '计算机科学与技术', 'cet4_score': 410, 'cet6_score': 430, 'gpa': 3.6, 'academic_score': 88.5, 'academic_weighted': 70.8, 'ranking': 3, 'total_students': 100},
            {'student_id': 'student4', 'student_name': '小丽', 'gender': '女', 'department': '电子工程学院', 'major': '电子信息工程', 'cet4_score': 435, 'cet6_score': 460, 'gpa': 3.7, 'academic_score': 90.5, 'academic_weighted': 72.4, 'ranking': 4, 'total_students': 100}
        ]
        
        students_basic = []
        for data in students_basic_data:
            existing_student = Student.query.filter_by(student_id=data['student_id']).first()
            if not existing_student:
                student = Student(**data)
                students_basic.append(student)
        
        if students_basic:
            for student in students_basic:
                db.session.add(student)
            db.session.commit()
            print("学生基本信息添加成功!")
        else:
            print("学生基本信息已存在，跳过添加!")
        
        # 添加学术专长详情
        academic_details = []
        for i in range(4):
            student_id = f'student{i+1}'
            existing_detail = AcademicSpecialtyDetail.query.filter_by(student_id=student_id).first()
            if not existing_detail:
                detail = AcademicSpecialtyDetail(
                    student_id=student_id,
                    project_name=f'学术项目{i+1}',
                    award_date=datetime.utcnow().date() - timedelta(days=random.randint(1, 60)),
                    award_level=random.choice(['国家级', '省级', '校级']),
                    award_type=random.choice(['individual', 'team']),
                    author_order=str(i+1),
                    self_score=random.uniform(5, 15),
                    score_basis=f'学术专长项目{i+1}的加分依据',
                    approved_score=random.uniform(5, 15)
                )
                academic_details.append(detail)
        
        if academic_details:
            for detail in academic_details:
                db.session.add(detail)
            db.session.commit()
            print("学术专长详情添加成功!")
        else:
            print("学术专长详情已存在，跳过添加!")
        
        # 添加综合表现详情
        comprehensive_details = []
        for i in range(4):
            student_id = f'student{i+1}'
            existing_detail = ComprehensivePerformanceDetail.query.filter_by(student_id=student_id).first()
            if not existing_detail:
                detail = ComprehensivePerformanceDetail(
                    student_id=student_id,
                    project_name=f'综合表现项目{i+1}',
                    award_date=datetime.utcnow().date() - timedelta(days=random.randint(1, 60)),
                    award_level=random.choice(['国家级', '省级', '校级']),
                    award_type=random.choice(['individual', 'team']),
                    author_order=str(i+1),
                    self_score=random.uniform(2, 8),
                    score_basis=f'综合表现项目{i+1}的加分依据',
                    approved_score=random.uniform(2, 8)
                )
                comprehensive_details.append(detail)
        
        if comprehensive_details:
            for detail in comprehensive_details:
                db.session.add(detail)
            db.session.commit()
            print("综合表现详情添加成功!")
        else:
            print("综合表现详情已存在，跳过添加!")
        
        # 添加学生总评
        evaluations = []
        for i in range(4):
            student_id = f'student{i+1}'
            existing_evaluation = StudentEvaluation.query.filter_by(student_id=student_id).first()
            if not existing_evaluation:
                academic_score = random.uniform(85, 95)
                comprehensive_score = random.uniform(80, 90)
                total_score = academic_score * 0.6 + comprehensive_score * 0.4 + random.uniform(0, 10)  # 加权总分加上综合加分
                
                evaluation = StudentEvaluation(
                    student_id=student_id,
                    student_name=['小明', '小红', '小刚', '小丽'][i],
                    department=['计算机学院', '电子工程学院', '计算机学院', '电子工程学院'][i],
                    major=['计算机科学与技术', '电子信息工程', '计算机科学与技术', '电子信息工程'][i],
                    gender=['男', '女', '男', '女'][i],
                    cet4_score=[425, 450, 410, 435][i],
                    cet6_score=[450, 480, 430, 460][i],
                    gpa=[3.8, 3.9, 3.6, 3.7][i],
                    academic_score=academic_score,
                    academic_weighted=academic_score * 0.8,
                    academic_specialty_total=random.uniform(5, 15),
                    comprehensive_performance_total=random.uniform(5, 10),
                    total_score=total_score,
                    comprehensive_score=comprehensive_score,
                    major_ranking=i+1,
                    total_students=100
                )
                evaluations.append(evaluation)
        
        if evaluations:
            for evaluation in evaluations:
                db.session.add(evaluation)
            db.session.commit()
            print("学生总评添加成功!")
        else:
            print("学生总评已存在，跳过添加!")
        
        # 检查教师审核的申请
        for teacher in teachers:
            teacher_reviewed = Application.query.filter_by(reviewed_by=teacher.username).count()
            print(f"{teacher.name}({teacher.username})审核的申请数: {teacher_reviewed}")
        
        # 检查学生总评数据
        total_evaluations = StudentEvaluation.query.count()
        print(f"学生总评数据数: {total_evaluations}")
            
    except Exception as e:
        print(f"添加测试数据失败: {e}")
        db.session.rollback()