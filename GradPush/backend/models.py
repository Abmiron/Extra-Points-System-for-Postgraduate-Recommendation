# -*- coding: utf-8 -*-
"""
数据模型文件

该文件定义了应用的数据库模型，包括用户模型(User)和申请模型(Application)，
负责数据库表结构的设计和数据关系的定义，提供数据操作的基础。

主要模型：
- User: 用户信息模型，存储用户账号、密码、角色等信息
- Application: 申请信息模型，存储推免加分申请的相关数据
"""

from extensions import db
from datetime import datetime
import bcrypt

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, teacher, admin
    avatar = db.Column(db.String(200), nullable=True)
    faculty = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    major = db.Column(db.String(100), nullable=True)
    student_id = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    role_name = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='active')  # active, disabled
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    # 设置密码（哈希）
    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # 验证密码
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# 申请模型
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    major = db.Column(db.String(100), nullable=False)
    application_type = db.Column(db.String(50), nullable=False)  # academic, comprehensive
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    self_score = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, draft
    project_name = db.Column(db.String(200), nullable=False)
    award_date = db.Column(db.Date, nullable=False)
    award_level = db.Column(db.String(50), nullable=True)  # national, provincial, municipal, school
    award_type = db.Column(db.String(50), nullable=True)  # individual, team
    description = db.Column(db.Text, nullable=True)
    files = db.Column(db.JSON, nullable=True)  # 存储文件信息的JSON数组
    
    # 学术专长相关字段
    academic_type = db.Column(db.String(50), nullable=True)  # research, competition, innovation
    # 科研成果特有字段
    research_type = db.Column(db.String(50), nullable=True)  # thesis, patent
    # 创新创业特有字段
    innovation_level = db.Column(db.String(50), nullable=True)  # national, provincial, school
    innovation_role = db.Column(db.String(50), nullable=True)  # leader, member
    # 学业竞赛特有字段
    award_grade = db.Column(db.String(50), nullable=True)  # firstOrHigher, second, third
    award_category = db.Column(db.String(50), nullable=True)  # A+类, A类, A-类
    author_rank_type = db.Column(db.String(50), nullable=True)  # ranked, unranked
    author_order = db.Column(db.Integer, nullable=True)  # 作者排序
    
    # 综合表现相关字段
    performance_type = db.Column(db.String(100), nullable=True)  # international_internship, military_service, volunteer, social_work, sports, honor_title
    performance_level = db.Column(db.String(50), nullable=True)  # provincial, school, college
    performance_participation = db.Column(db.String(50), nullable=True)  # individual, team
    team_role = db.Column(db.String(50), nullable=True)  # leader, member
    
    # 审核信息
    final_score = db.Column(db.Float, nullable=True)
    review_comment = db.Column(db.Text, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Application {self.id}>'