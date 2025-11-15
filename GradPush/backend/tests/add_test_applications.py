# -*- coding: utf-8 -*-
"""
添加测试申请数据脚本

该脚本用于添加测试申请数据到数据库，以便测试审核统计功能
"""

import sys
import os
import random
from datetime import datetime, timedelta

# 将项目根目录添加到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Application

with app.app_context():
    try:
        # 清空现有申请数据（可选）
        Application.query.delete()
        db.session.commit()
        print("已清空现有申请数据")
        
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
                academic_type=random.choice(['research', 'competition', 'innovation']),
                self_score=random.uniform(60, 90),
                award_date=(datetime.utcnow() - timedelta(days=random.randint(10, 60))).date(),
                description=f'这是第{i+1}个学术项目申请',
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 10))
            )
            applications.append(app)
        
        # 创建已审核的申请
        for i in range(15):
            status = random.choice(['approved', 'rejected'])
            reviewed_by = f'teacher{i%2+1}'
            reviewed_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            
            # 确保部分申请是本月的
            if i < 8:
                reviewed_at = datetime.utcnow() - timedelta(days=random.randint(1, 15))
            
            app = Application(
                student_id=f'student{i%2+1}',
                student_name=['小明', '小红'][i%2],
                department=['计算机学院', '电子工程学院'][i%2],
                major=['计算机科学与技术', '电子信息工程'][i%2],
                application_type=random.choice(['academic', 'comprehensive']),
                project_name=f'项目{i+1}',
                status=status,
                academic_type=random.choice(['research', 'competition', 'innovation']),
                performance_type=random.choice(['international_internship', 'military_service', 'volunteer']),
                self_score=random.uniform(60, 90),
                award_date=(datetime.utcnow() - timedelta(days=random.randint(10, 60))).date(),
                description=f'这是第{i+1}个申请',
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
        
        # 检查教师审核的申请
        for teacher_id in ['teacher1', 'teacher2']:
            teacher_reviewed = Application.query.filter_by(reviewed_by=teacher_id).count()
            print(f"教师{teacher_id}审核的申请数: {teacher_reviewed}")
            
        # 检查本月审核的申请
        current_month = datetime.utcnow().month
        current_year = datetime.utcnow().year
        this_month_reviewed = Application.query.filter(
            Application.reviewed_at.isnot(None),
            Application.reviewed_at.cast(db.Date).between(
                datetime(current_year, current_month, 1).date(),
                datetime(current_year, current_month + 1, 1).date() - timedelta(days=1)
            )
        ).count()
        print(f"本月审核的申请数: {this_month_reviewed}")
            
    except Exception as e:
        print(f"添加测试数据失败: {e}")
        db.session.rollback()