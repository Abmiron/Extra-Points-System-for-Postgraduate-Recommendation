from extensions import db
from datetime import datetime

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
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    project_name = db.Column(db.String(200), nullable=False)
    award_date = db.Column(db.Date, nullable=False)
    award_level = db.Column(db.String(50), nullable=False)  # national, provincial, municipal, school
    award_type = db.Column(db.String(50), nullable=False)  # individual, team
    description = db.Column(db.Text, nullable=False)
    files = db.Column(db.JSON, nullable=True)  # 存储文件信息的JSON数组
    
    # 审核信息
    final_score = db.Column(db.Float, nullable=True)
    review_comment = db.Column(db.Text, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Application {self.id}>'