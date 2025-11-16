# -*- coding: utf-8 -*-
"""
用户认证蓝图

该文件负责处理用户认证相关的API端点，包括：
- 登录
- 注册
- 密码重置
"""

from flask import Blueprint, request, jsonify
from models import User
from datetime import datetime

# 创建蓝图实例
auth_bp = Blueprint('auth', __name__, url_prefix='/api')

# 登录接口
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # 查找用户
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'message': '用户不存在'}), 401
    
    if user.status == 'disabled':
        return jsonify({'message': '账户已被禁用'}), 401
    
    # 验证密码
    if not user.check_password(password):
        return jsonify({'message': '密码错误'}), 401
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    from app import db
    db.session.commit()
    
    # 返回用户信息（不包含密码）
    user_data = {
        'id': user.id,
        'username': user.username,
        'name': user.name,
        'role': user.role,
        'avatar': user.avatar,
        'faculty': user.faculty,
        'department': user.department,
        'major': user.major,
        'studentId': user.student_id,
        'email': user.email,
        'phone': user.phone,
        'roleName': user.role_name,
        'lastLogin': user.last_login.isoformat() if user.last_login else None
    }
    
    return jsonify({'user': user_data, 'message': '登录成功'}), 200

# 注册接口
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'message': '用户名已存在'}), 400
    
    # 创建新用户
    new_user = User(
        username=data['username'],
        name=data['name'],
        role=data['role'],
        avatar='/images/default-avatar.jpg',  # 统一使用默认头像
        faculty=data.get('faculty', ''),  # 从请求中获取学院
        email='',  # 默认值
        phone=''   # 默认值
    )
    
    # 设置密码（哈希）
    new_user.set_password(data['password'])
    
    # 根据角色添加额外信息
    if data['role'] == 'student':
        new_user.student_id = data['username']
        new_user.department = data.get('department', '')  # 从请求中获取系
        new_user.major = data.get('major', '')  # 从请求中获取专业
    elif data['role'] == 'teacher':
        new_user.role_name = '审核员'  # 默认值
    
    from app import db
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': '注册成功'}), 201

# 密码重置接口
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    username = data.get('username')
    new_password = data.get('newPassword')
    
    # 查找用户
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    # 设置新密码
    user.set_password(new_password)
    
    from app import db
    db.session.commit()
    
    return jsonify({'message': '密码重置成功'}), 200

# 获取所有学院（用于注册选择）
@auth_bp.route('/faculties', methods=['GET'])
def get_faculties():
    from models import Faculty
    faculties = Faculty.query.all()
    result = []
    for faculty in faculties:
        result.append({
            'id': faculty.id,
            'name': faculty.name
        })
    return jsonify({'faculties': result}), 200

# 根据学院ID获取系列表（用于注册选择）
@auth_bp.route('/departments/<int:faculty_id>', methods=['GET'])
def get_departments_by_faculty(faculty_id):
    from models import Department
    departments = Department.query.filter_by(faculty_id=faculty_id).all()
    result = []
    for department in departments:
        result.append({
            'id': department.id,
            'name': department.name
        })
    return jsonify({'departments': result}), 200

# 根据系ID获取专业列表（用于注册选择）
@auth_bp.route('/majors/<int:department_id>', methods=['GET'])
def get_majors_by_department(department_id):
    from models import Major
    majors = Major.query.filter_by(department_id=department_id).all()
    result = []
    for major in majors:
        result.append({
            'id': major.id,
            'name': major.name
        })
    return jsonify({'majors': result}), 200