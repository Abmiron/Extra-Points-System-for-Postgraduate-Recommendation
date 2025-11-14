# -*- coding: utf-8 -*-
"""
用户管理蓝图

该文件负责处理用户管理相关的API端点，包括：
- 获取用户信息
- 管理员获取所有用户
- 管理员删除用户
- 管理员更新用户信息
- 管理员重置用户密码
"""

from flask import Blueprint, request, jsonify
from models import User

# 创建蓝图实例
user_bp = Blueprint('user', __name__, url_prefix='/api')

# 获取单个用户信息接口
@user_bp.route('/user/<username>', methods=['GET'])
def get_user(username):
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
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
    
    return jsonify({'user': user_data}), 200

# 辅助函数：检查用户是否为管理员
def is_admin(user):
    return user and user.role == 'admin'

# 管理员获取所有用户接口
@user_bp.route('/admin/users', methods=['GET'])
def get_all_users():
    # 获取请求参数
    role = request.args.get('role')
    status = request.args.get('status')
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询
    query = User.query
    
    # 根据role筛选
    if role:
        query = query.filter_by(role=role)
    
    # 根据status筛选
    if status:
        query = query.filter_by(status=status)
    
    # 根据search关键词搜索
    if search:
        query = query.filter((User.name.like(f'%{search}%')) | (User.username.like(f'%{search}%')))
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    user_list = []
    for user in users:
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
            'status': user.status,
            'lastLogin': user.last_login.isoformat() if user.last_login else None
        }
        user_list.append(user_data)
    
    # 返回分页数据
    return jsonify({
        'users': user_list,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200

# 管理员删除用户接口
@user_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    from app import db
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': '用户删除成功'}), 200

# 管理员更新用户信息接口
@user_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 更新用户信息
    if 'name' in data:
        user.name = data['name']
    if 'role' in data:
        user.role = data['role']
    if 'faculty' in data:
        user.faculty = data['faculty']
    if 'department' in data:
        user.department = data['department']
    if 'major' in data:
        user.major = data['major']
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'roleName' in data:
        user.role_name = data['roleName']
    if 'status' in data:
        user.status = data['status']
    
    from app import db
    db.session.commit()
    
    return jsonify({'message': '用户信息更新成功'}), 200

# 管理员重置用户密码接口
@user_bp.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
def admin_reset_password(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    data = request.get_json()
    new_password = data.get('newPassword')
    
    if not new_password:
        return jsonify({'message': '新密码不能为空'}), 400
    
    # 设置新密码
    user.set_password(new_password)
    
    from app import db
    db.session.commit()
    
    return jsonify({'message': '密码重置成功'}), 200