# -*- coding: utf-8 -*-
"""
API路由定义文件

该文件负责定义应用的所有API端点，处理客户端请求，实现业务逻辑。

主要功能模块：
- 用户认证：登录、注册、密码重置
- 用户管理：获取用户信息
- 申请管理：创建、查询、更新、删除、审核申请
- 系统监控：健康检查
"""

from flask import request, jsonify
from app import app, db
from models import User, Application
from datetime import datetime
import bcrypt

# 根路径健康检查
@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

# 用户认证相关路由

# 登录接口
@app.route('/api/login', methods=['POST'])
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
@app.route('/api/register', methods=['POST'])
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
    
    # 保存到数据库
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': '注册成功'}), 201

# 密码重置接口
@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    username = data.get('username')
    new_password = data.get('newPassword')
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    # 更新密码（使用哈希）
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': '密码重置成功'}), 200

# 获取用户信息接口
@app.route('/api/user/<username>', methods=['GET'])
def get_user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
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
        'status': user.status
    }
    
    return jsonify(user_data), 200

# 管理员用户管理相关路由

# 检查是否为管理员的辅助函数
def is_admin(user):
    return user and user.role == 'admin'

# 获取所有用户列表（管理员专用）
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    # 获取当前登录用户信息
    current_user_id = request.args.get('currentUserId')
    if not current_user_id:
        return jsonify({'message': '未提供当前用户ID'}), 400
    
    current_user = User.query.get(current_user_id)
    if not current_user or not is_admin(current_user):
        return jsonify({'message': '权限不足'}), 403
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    role = request.args.get('role')
    status = request.args.get('status')
    search = request.args.get('search')
    
    # 构建查询
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    
    if status:
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(
            (User.username.like(f'%{search}%')) | 
            (User.name.like(f'%{search}%')) |
            (User.email.like(f'%{search}%'))
        )
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    users = []
    for user in pagination.items:
        users.append({
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'role': user.role,
            'faculty': user.faculty,
            'department': user.department,
            'major': user.major,
            'studentId': user.student_id,
            'email': user.email,
            'phone': user.phone,
            'status': user.status,
            'createdAt': user.created_at.isoformat(),
            'updatedAt': user.updated_at.isoformat()
        })
    
    return jsonify({
        'users': users,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

# 删除用户（管理员专用）
@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # 获取当前登录用户信息
    current_user_id = request.args.get('currentUserId')
    if not current_user_id:
        return jsonify({'message': '未提供当前用户ID'}), 400
    
    current_user = User.query.get(current_user_id)
    if not current_user or not is_admin(current_user):
        return jsonify({'message': '权限不足'}), 403
    
    # 不能删除自己
    if current_user.id == user_id:
        return jsonify({'message': '不能删除自己'}), 400
    
    # 查找要删除的用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    # 删除用户
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': '用户删除成功'}), 200

# 更新用户信息（管理员专用）
@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    # 获取当前登录用户信息
    current_user_id = request.args.get('currentUserId')
    if not current_user_id:
        return jsonify({'message': '未提供当前用户ID'}), 400
    
    current_user = User.query.get(current_user_id)
    if not current_user or not is_admin(current_user):
        return jsonify({'message': '权限不足'}), 403
    
    data = request.get_json()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    # 更新用户信息
    if 'name' in data:
        user.name = data['name']
    if 'role' in data and data['role'] in ['student', 'teacher', 'admin']:
        user.role = data['role']
    if 'faculty' in data:
        user.faculty = data['faculty']
    if 'department' in data:
        user.department = data['department']
    if 'major' in data:
        user.major = data['major']
    if 'studentId' in data:
        user.student_id = data['studentId']
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'status' in data and data['status'] in ['active', 'disabled']:
        user.status = data['status']
    if 'roleName' in data:
        user.role_name = data['roleName']
    
    # 保存更改
    db.session.commit()
    
    return jsonify({'message': '用户信息更新成功'}), 200

# 重置用户密码（管理员专用）
@app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
def admin_reset_password(user_id):
    # 获取当前登录用户信息
    current_user_id = request.args.get('currentUserId')
    if not current_user_id:
        return jsonify({'message': '未提供当前用户ID'}), 400
    
    current_user = User.query.get(current_user_id)
    if not current_user or not is_admin(current_user):
        return jsonify({'message': '权限不足'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    data = request.get_json()
    new_password = data.get('newPassword')
    
    if not new_password:
        return jsonify({'message': '请提供新密码'}), 400
    
    # 更新密码
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': '密码重置成功'}), 200

# 申请相关路由

# 获取所有申请
@app.route('/api/applications', methods=['GET'])
def get_applications():
    applications = Application.query.all()
    app_list = []
    
    for app in applications:
        app_data = {
            'id': app.id,
            'studentId': app.student_id,
            'studentName': app.student_name,
            'department': app.department,
            'major': app.major,
            'applicationType': app.application_type,
            'appliedAt': app.applied_at.isoformat() if app.applied_at else None,
            'selfScore': app.self_score,
            'status': app.status,
            'projectName': app.project_name,
            'awardDate': app.award_date.isoformat() if app.award_date else None,
            'awardLevel': app.award_level,
            'awardType': app.award_type,
            'description': app.description,
            'files': app.files,
            'finalScore': app.final_score,
            'reviewComment': app.review_comment,
            'reviewedAt': app.reviewed_at.isoformat() if app.reviewed_at else None,
            'reviewedBy': app.reviewed_by
        }
        app_list.append(app_data)
    
    return jsonify(app_list), 200

# 获取单个申请
@app.route('/api/applications/<int:id>', methods=['GET'])
def get_application(id):
    app = Application.query.get_or_404(id)
    
    app_data = {
        'id': app.id,
        'studentId': app.student_id,
        'studentName': app.student_name,
        'department': app.department,
        'major': app.major,
        'applicationType': app.application_type,
        'appliedAt': app.applied_at.isoformat() if app.applied_at else None,
        'selfScore': app.self_score,
        'status': app.status,
        'projectName': app.project_name,
        'awardDate': app.award_date.isoformat() if app.award_date else None,
        'awardLevel': app.award_level,
        'awardType': app.award_type,
        'description': app.description,
        'files': app.files,
        'finalScore': app.final_score,
        'reviewComment': app.review_comment,
        'reviewedAt': app.reviewed_at.isoformat() if app.reviewed_at else None,
        'reviewedBy': app.reviewed_by
    }
    
    return jsonify(app_data), 200

# 创建申请
@app.route('/api/applications', methods=['POST'])
def create_application():
    data = request.get_json()
    
    new_application = Application(
        student_id=data['studentId'],
        student_name=data['studentName'],
        department=data['department'],
        major=data['major'],
        application_type=data['applicationType'],
        applied_at=datetime.fromisoformat(data['appliedAt']),
        self_score=data['selfScore'],
        status='pending',
        project_name=data['projectName'],
        award_date=datetime.fromisoformat(data['awardDate']).date(),
        award_level=data['awardLevel'],
        award_type=data['awardType'],
        description=data['description'],
        files=data['files']
    )
    
    db.session.add(new_application)
    db.session.commit()
    
    return jsonify({'message': '申请创建成功', 'id': new_application.id}), 201

# 更新申请
@app.route('/api/applications/<int:id>', methods=['PUT'])
def update_application(id):
    app = Application.query.get_or_404(id)
    data = request.get_json()
    
    # 更新基本信息
    app.self_score = data.get('selfScore', app.self_score)
    app.project_name = data.get('projectName', app.project_name)
    app.award_date = datetime.fromisoformat(data['awardDate']).date() if 'awardDate' in data else app.award_date
    app.award_level = data.get('awardLevel', app.award_level)
    app.award_type = data.get('awardType', app.award_type)
    app.description = data.get('description', app.description)
    app.files = data.get('files', app.files)
    
    db.session.commit()
    
    return jsonify({'message': '申请更新成功'}), 200

# 审核申请
@app.route('/api/applications/<int:id>/review', methods=['POST'])
def review_application(id):
    app = Application.query.get_or_404(id)
    data = request.get_json()
    
    app.status = data['status']
    app.final_score = data.get('finalScore')
    app.review_comment = data.get('reviewComment')
    app.reviewed_at = datetime.utcnow()
    app.reviewed_by = data.get('reviewedBy')
    
    db.session.commit()
    
    return jsonify({'message': '申请审核成功'}), 200

# 删除申请
@app.route('/api/applications/<int:id>', methods=['DELETE'])
def delete_application(id):
    app = Application.query.get_or_404(id)
    
    db.session.delete(app)
    db.session.commit()
    
    return jsonify({'message': '申请删除成功'}), 200

# 获取待审核申请
@app.route('/api/applications/pending', methods=['GET'])
def get_pending_applications():
    applications = Application.query.filter_by(status='pending').all()
    app_list = []
    
    for app in applications:
        app_data = {
            'id': app.id,
            'studentId': app.student_id,
            'studentName': app.student_name,
            'department': app.department,
            'major': app.major,
            'applicationType': app.application_type,
            'appliedAt': app.applied_at.isoformat() if app.applied_at else None,
            'selfScore': app.self_score,
            'status': app.status,
            'projectName': app.project_name,
            'awardDate': app.award_date.isoformat() if app.award_date else None,
            'awardLevel': app.award_level,
            'awardType': app.award_type,
            'description': app.description,
            'files': app.files
        }
        app_list.append(app_data)
    
    return jsonify(app_list), 200

# 健康检查接口
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200