# -*- coding: utf-8 -*-
"""
用户管理蓝图

该文件负责处理用户管理相关的API端点，包括：
- 获取用户信息
- 管理员获取所有用户
- 管理员删除用户
- 管理员更新用户信息
- 管理员重置用户密码
- 用户上传头像
"""

from flask import Blueprint, request, jsonify
from models import User, Faculty, Department, Major
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO

# 创建蓝图实例
user_bp = Blueprint('user', __name__, url_prefix='/api')

# 获取单个用户信息接口
@user_bp.route('/user/<username>', methods=['GET'])
def get_user(username):
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    return _get_user_data(user)

# 获取当前学生用户信息接口（为了解决前端调用/api/user/student的问题）
@user_bp.route('/user/student', methods=['GET'])
def get_student_user():
    # 从请求头获取用户名（实际项目中应该从JWT token获取）
    # 这里简化处理，从请求参数或请求体中获取username
    username = request.args.get('username') or request.json.get('username') if request.json else None
    
    if not username:
        return jsonify({'message': '缺少用户名参数'}), 400
    
    user = User.query.filter_by(username=username, role='student').first()
    
    if not user:
        return jsonify({'message': '学生用户不存在'}), 404
    
    return _get_user_data(user)

# 辅助函数：获取用户数据
def _get_user_data(user):
    # 安全获取学院、系和专业名称
    faculty = Faculty.query.get(user.faculty_id) if user.faculty_id else None
    faculty_name = faculty.name if faculty else ''
    
    department = Department.query.get(user.department_id) if user.department_id else None
    department_name = department.name if department else ''
    
    major = Major.query.get(user.major_id) if user.major_id else None
    major_name = major.name if major else ''
    
    # 返回用户信息（不包含密码）
    user_data = {
        'id': user.id,
        'username': user.username,
        'name': user.name,
        'role': user.role,
        'avatar': user.avatar,
        'faculty': faculty_name,
        'facultyId': user.faculty_id,
        'department': department_name,
        'departmentId': user.department_id,
        'major': major_name,
        'majorId': user.major_id,
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
        # 获取学院、系和专业名称
        faculty_name = Faculty.query.get(user.faculty_id).name if user.faculty_id else ''
        department_name = Department.query.get(user.department_id).name if user.department_id else ''
        major_name = Major.query.get(user.major_id).name if user.major_id else ''
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'role': user.role,
            'avatar': user.avatar,
            'faculty': faculty_name,
            'facultyId': user.faculty_id,
            'department': department_name,
            'departmentId': user.department_id,
            'major': major_name,
            'majorId': user.major_id,
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
    # 获取当前登录用户的ID
    current_user_id = request.args.get('currentUserId', type=int)
    
    # 检查是否尝试删除自己
    if current_user_id == user_id:
        return jsonify({'message': '无法删除自己的账号'}), 400
    
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
    # 获取当前登录用户的ID
    current_user_id = request.args.get('currentUserId', type=int)
    
    # 检查是否尝试修改自己
    if current_user_id == user_id:
        return jsonify({'message': '无法修改自己的账号信息'}), 400
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 更新用户信息
    if 'name' in data:
        user.name = data['name']
    if 'role' in data:
        user.role = data['role']
    if 'facultyId' in data:
        user.faculty_id = data['facultyId']
    if 'departmentId' in data:
        user.department_id = data['departmentId']
    if 'majorId' in data:
        user.major_id = data['majorId']
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
    # 获取当前登录用户的ID
    current_user_id = request.args.get('currentUserId', type=int)
    
    # 检查是否尝试重置自己的密码
    if current_user_id == user_id:
        return jsonify({'message': '无法重置自己的密码，请使用个人设置修改密码'}), 400
    
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

# 用户更新个人信息接口
@user_bp.route('/user/profile', methods=['PUT'])
def update_profile():
    # 从请求头获取用户名（实际项目中应该从JWT token获取）
    # 这里简化处理，假设从请求体获取username
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({'message': '缺少用户名参数'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    # 更新用户信息
    if 'name' in data:
        user.name = data['name']
    if 'facultyId' in data:
        user.faculty_id = data['facultyId']
    if 'departmentId' in data:
        user.department_id = data['departmentId']
    if 'majorId' in data:
        user.major_id = data['majorId']
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    
    from app import db
    db.session.commit()
    
    # 获取学院、系和专业名称
    faculty_name = Faculty.query.get(user.faculty_id).name if user.faculty_id else ''
    department_name = Department.query.get(user.department_id).name if user.department_id else ''
    major_name = Major.query.get(user.major_id).name if user.major_id else ''
    
    # 返回更新后的用户信息
    user_data = {
        'id': user.id,
        'username': user.username,
        'name': user.name,
        'role': user.role,
        'avatar': user.avatar,
        'faculty': faculty_name,
        'facultyId': user.faculty_id,
        'department': department_name,
        'departmentId': user.department_id,
        'major': major_name,
        'majorId': user.major_id,
        'studentId': user.student_id,
        'email': user.email,
        'phone': user.phone,
        'roleName': user.role_name,
        'lastLogin': user.last_login.isoformat() if user.last_login else None
    }
    
    return jsonify({'user': user_data, 'message': '个人信息更新成功'}), 200

# 用户上传头像接口
@user_bp.route('/user/avatar', methods=['POST'])
def upload_avatar():
    # 检查是否有文件上传
    if 'avatar' not in request.files:
        return jsonify({'message': '没有文件上传'}), 400
    
    file = request.files['avatar']
    
    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({'message': '请选择一个文件'}), 400
    
    # 检查文件类型是否为图片
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return jsonify({'message': '只支持PNG、JPG、JPEG和GIF格式的图片'}), 400
    
    # 从请求头或表单获取用户名（实际项目中应该从JWT token获取）
    # 这里简化处理，从表单获取username
    username = request.form.get('username')
    
    if not username:
        return jsonify({'message': '缺少用户名参数'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    try:
        # 导入app以避免循环导入
        from app import app
        
        # 确保上传目录存在
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        # 确保头像上传目录存在
        if not os.path.exists(app.config['AVATAR_FOLDER']):
            os.makedirs(app.config['AVATAR_FOLDER'])
        
        # 生成唯一的文件名
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(app.config['AVATAR_FOLDER'], unique_filename)
        
        # 处理图片：调整大小和压缩
        image = Image.open(file)
        
        # 最大尺寸限制
        max_size = (500, 500)
        
        # 调整图片大小
        image.thumbnail(max_size)
        
        # 创建字节流来保存处理后的图片
        output = BytesIO()
        
        # 保存图片（根据文件类型选择格式）
        if filename.lower().endswith(('.png', '.gif')):
            image.save(output, format='PNG', optimize=True)
        else:
            # JPEG格式可以压缩质量
            image.save(output, format='JPEG', quality=85, optimize=True)
        
        # 将字节流内容保存到文件
        with open(file_path, 'wb') as f:
            f.write(output.getvalue())
        
        # 更新用户头像路径
        user.avatar = f"/uploads/avatars/{unique_filename}"
        
        from app import db
        db.session.commit()
        
        # 获取学院、系和专业名称
        faculty_name = Faculty.query.get(user.faculty_id).name if user.faculty_id else ''
        department_name = Department.query.get(user.department_id).name if user.department_id else ''
        major_name = Major.query.get(user.major_id).name if user.major_id else ''
        
        # 返回更新后的用户信息
        user_data = {
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'role': user.role,
            'avatar': user.avatar,
            'faculty': faculty_name,
            'facultyId': user.faculty_id,
            'department': department_name,
            'departmentId': user.department_id,
            'major': major_name,
            'majorId': user.major_id,
            'studentId': user.student_id,
            'email': user.email,
            'phone': user.phone,
            'roleName': user.role_name,
            'lastLogin': user.last_login.isoformat() if user.last_login else None
        }
        
        return jsonify({'user': user_data, 'message': '头像上传成功'}), 200
    except Exception as e:
        return jsonify({'message': f'头像上传失败: {str(e)}'}), 500

# 用户修改密码接口
@user_bp.route('/user/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    username = data.get('username')
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
    
    if not username or not current_password or not new_password:
        return jsonify({'message': '缺少必要参数'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    # 验证当前密码
    if not user.check_password(current_password):
        return jsonify({'message': '当前密码错误'}), 400
    
    # 设置新密码
    user.set_password(new_password)
    
    from app import db
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'}), 200