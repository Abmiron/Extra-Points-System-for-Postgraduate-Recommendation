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
        avatar='/images/头像1.jpg' if data['role'] == 'student' else '/images/头像2.jpg',
        faculty='信息学院',  # 默认值
        email='',  # 默认值
        phone=''   # 默认值
    )
    
    # 设置密码（哈希）
    new_user.set_password(data['password'])
    
    # 根据角色添加额外信息
    if data['role'] == 'student':
        new_user.student_id = data['username']
        new_user.department = '计算机科学与技术系'  # 默认值
        new_user.major = '计算机科学与技术'  # 默认值
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