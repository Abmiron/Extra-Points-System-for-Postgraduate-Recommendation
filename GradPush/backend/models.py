# -*- coding: utf-8 -*-
"""
数据模型文件

该文件定义了应用的数据库模型，包括用户模型(User)、申请模型(Application)和学生模型(Student)，
负责数据库表结构的设计和数据关系的定义，提供数据操作的基础。

主要模型：
- User: 用户信息模型，存储用户账号、密码、角色等信息
- Application: 申请信息模型，存储推免加分申请的相关数据
- Student: 学生信息模型，合并了学生基本信息和总评成绩
- PerformanceDetail: 合并了学术专长和综合表现详情
- Rule: 加分规则模型，存储推免加分的规则定义
- Faculty: 学院信息模型，存储学院信息
- Department: 系信息模型，存储系信息
- Major: 专业信息模型，存储专业信息
"""

from extensions import db
from datetime import datetime
import bcrypt

# 学院模型
class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # 学院名称
    description = db.Column(db.Text, nullable=True)  # 学院描述
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关系
    departments = db.relationship('Department', backref='faculty', lazy=True)
    
    def __repr__(self):
        return f'<Faculty {self.name}>'

# 系模型
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 系名称
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)  # 所属学院
    description = db.Column(db.Text, nullable=True)  # 系描述
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关系
    majors = db.relationship('Major', backref='department', lazy=True)
    
    def __repr__(self):
        return f'<Department {self.name}>'

# 专业模型
class Major(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 专业名称
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)  # 所属系
    description = db.Column(db.Text, nullable=True)  # 专业描述
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    def __repr__(self):
        return f'<Major {self.name}>'

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, teacher, admin
    avatar = db.Column(db.String(200), nullable=True)
    # 使用外键关联学院、系、专业
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    major_id = db.Column(db.Integer, db.ForeignKey('major.id'), nullable=True)
    # 保留原有字段用于兼容旧数据（可在后续版本中移除）
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
    student_id = db.Column(db.String(20), db.ForeignKey('student.student_id'), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    # 使用外键关联学院、系和专业
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    major_id = db.Column(db.Integer, db.ForeignKey('major.id'), nullable=False)
    application_type = db.Column(db.String(50), nullable=False)  # academic, comprehensive
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    self_score = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, draft
    project_name = db.Column(db.String(200), nullable=False)
    award_date = db.Column(db.Date, nullable=True)
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
    
    # 审核相关字段
    final_score = db.Column(db.Float, nullable=True)  # 最终核定分数
    review_comment = db.Column(db.Text, nullable=True)  # 审核意见
    reviewed_at = db.Column(db.DateTime, nullable=True)  # 审核时间
    reviewed_by = db.Column(db.String(100), nullable=True)  # 审核人
    
    # 规则关联
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id'), nullable=True)
    
    # 关系定义
    faculty = db.relationship('Faculty', backref=db.backref('applications', lazy=True))
    department = db.relationship('Department', backref=db.backref('applications', lazy=True))
    major = db.relationship('Major', backref=db.backref('applications', lazy=True))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Application {self.id}>'

# 合并学术专长详情和综合表现详情为统一的表现详情模型
class PerformanceDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), db.ForeignKey('student.student_id'), nullable=False)
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id'), nullable=True)  # 关联评分规则
    type = db.Column(db.String(50), nullable=False)  # performance_type: academic, comprehensive
    project_name = db.Column(db.String(200), nullable=False)  # 项目名称
    award_date = db.Column(db.Date, nullable=False)  # 获奖时间
    award_level = db.Column(db.String(50), nullable=True)  # 奖项级别
    award_type = db.Column(db.String(50), nullable=True)  # 个人或集体奖项
    author_order = db.Column(db.String(20), nullable=True)  # 集体奖项中第几作者/参赛者
    self_score = db.Column(db.Float, nullable=False)  # 自评加分
    score_basis = db.Column(db.Text, nullable=True)  # 加分依据
    approved_score = db.Column(db.Float, nullable=True)  # 学院核定加分
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键关联已定义，不使用ORM关系
    
    def __repr__(self):
        return f'<PerformanceDetail {self.id} ({self.type})>'

# 合并学生模型和学生总评模型
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)  # 学号
    student_name = db.Column(db.String(100), nullable=False)  # 姓名
    gender = db.Column(db.String(10), nullable=True)  # 性别
    # 外键关联学院、系和专业
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True)  # 学院ID
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)  # 系ID
    major_id = db.Column(db.Integer, db.ForeignKey('major.id'), nullable=False)  # 专业ID
    # 关系
    faculty = db.relationship('Faculty', backref=db.backref('students', lazy=True))
    department = db.relationship('Department', backref=db.backref('students', lazy=True))
    major = db.relationship('Major', backref=db.backref('students', lazy=True))
    cet4_score = db.Column(db.Integer, nullable=True)  # CET4成绩
    cet6_score = db.Column(db.Integer, nullable=True)  # CET6成绩
    
    # 学业综合成绩
    gpa = db.Column(db.Float, nullable=True)  # 推免绩点(满分4分)
    academic_score = db.Column(db.Float, nullable=True)  # 换算后的学业成绩(满分100分)
    academic_weighted = db.Column(db.Float, nullable=True)  # 学业综合成绩（80%）
    
    # 学术专长成绩（占总分12%）
    academic_specialty_total = db.Column(db.Float, nullable=True)  # 学院核定总分
    
    # 综合表现加分（占总分8%）
    comprehensive_performance_total = db.Column(db.Float, nullable=True)  # 学院核定总分
    
    # 总分与排名
    total_score = db.Column(db.Float, nullable=True)  # 考核综合成绩总分
    comprehensive_score = db.Column(db.Float, nullable=True)  # 综合成绩
    major_ranking = db.Column(db.Integer, nullable=True)  # 专业成绩排名
    total_students = db.Column(db.Integer, nullable=True)  # 排名人数
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Student {self.student_name} ({self.student_id})>'

# 加分规则模型
class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 规则名称
    type = db.Column(db.String(50), nullable=False)  # 规则类型: academic(学术专长), comprehensive(综合表现)
    sub_type = db.Column(db.String(50), nullable=True)  # 子类型: research(科研成果), competition(学业竞赛), innovation(创新创业训练), etc.
    level = db.Column(db.String(50), nullable=True)  # 级别: 国家级, 省级, 校级, A+, A, A-, etc.
    grade = db.Column(db.String(50), nullable=True)  # 等级: 一等奖及以上, 二等奖, 三等奖
    category = db.Column(db.String(50), nullable=True)  # 奖项类别: 个人奖项, 团队奖项
    participation_type = db.Column(db.String(50), default='individual')  # 参与类型: individual(个人), team(集体)
    team_role = db.Column(db.String(50), nullable=True)  # 团队角色: captain(队长), member(队员)
    author_rank_type = db.Column(db.String(50), default='unranked')  # 作者排序类型: ranked(区分排名), unranked(不区分排名)
    author_rank = db.Column(db.Integer, nullable=True)  # 作者排序: 数字，仅当区分排名时填写
    author_rank_ratio = db.Column(db.Float, nullable=True)  # 作者排序比例: 如80%填写0.8
    research_type = db.Column(db.String(50), nullable=True)  # 科研成果类型: thesis(学术论文), patent(发明专利)
    score = db.Column(db.Float, nullable=False)  # 基础分值
    max_score = db.Column(db.Float, nullable=True)  # 最大分数限制（如创新创业训练最多加2分）
    max_count = db.Column(db.Integer, nullable=True)  # 最大项目数量限制（如学业竞赛不超过3项）
    is_special = db.Column(db.Boolean, default=False)  # 是否为特殊规则（如Nature/Science论文）
    status = db.Column(db.String(20), default='active')  # 状态: active, disabled
    description = db.Column(db.Text, nullable=True)  # 规则描述
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    def __repr__(self):
        return f'<Rule {self.name}>'