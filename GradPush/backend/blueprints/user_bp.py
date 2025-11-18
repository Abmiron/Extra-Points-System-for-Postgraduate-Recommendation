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
- 学生信息管理（增删改查）
"""

from flask import Blueprint, request, jsonify, current_app
from models import User, Faculty, Department, Major, Student
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO
from extensions import db

# 创建蓝图实例
user_bp = Blueprint('user', __name__, url_prefix='/api')

# 获取单个用户信息接口
@user_bp.route('/user/<username>', methods=['GET'])
def get_user(username):
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    return _get_user_data(user)

# 获取当前登录用户信息接口
@user_bp.route('/user/current', methods=['GET'])
def get_current_user():
    # 从请求头获取用户名（实际项目中应该从JWT token获取）
    # 这里简化处理，只从URL参数获取username
    username = request.args.get('username')
    
    if not username:
        return jsonify({'message': '缺少用户名参数'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    return _get_user_data(user)

# 获取当前学生用户信息接口（为了解决前端调用/api/user/student的问题）
@user_bp.route('/user/student', methods=['GET'])
def get_student_user():
    # 从请求头获取用户名（实际项目中应该从JWT token获取）
    # 这里简化处理，只从URL参数获取username
    username = request.args.get('username')
    
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
    
    # 如果是学生用户，同时删除关联的Student记录
    if user.role == 'student' and user.student:
        db.session.delete(user.student)
    
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

# 恢复默认头像接口
@user_bp.route('/user/avatar/reset', methods=['POST'])
def reset_avatar():
    # 从表单获取用户名
    username = request.form.get('username')
    
    if not username:
        return jsonify({'message': '缺少用户名参数'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    try:
        # 将用户头像设置为空字符串，表示使用默认头像
        user.avatar = ''
        
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
        
        return jsonify({'user': user_data, 'message': '恢复默认头像成功'}), 200
    except Exception as e:
        return jsonify({'message': f'恢复默认头像失败: {str(e)}'}), 500

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
        # 确保上传目录存在
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])
        
        # 确保头像上传目录存在
        if not os.path.exists(current_app.config['AVATAR_FOLDER']):
            os.makedirs(current_app.config['AVATAR_FOLDER'])
        
        # 生成唯一的文件名和路径
        filename = file.filename
        ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(current_app.config['AVATAR_FOLDER'], unique_filename)
        
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
    
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'}), 200

# 以下是学生管理相关接口
# 获取所有学生信息接口
@user_bp.route('/admin/students', methods=['GET'])
def get_all_students():
    # 获取请求参数
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询
    query = Student.query
    
    # 根据search关键词搜索
    if search:
        query = query.filter((Student.student_name.like(f'%{search}%')) | (Student.student_id.like(f'%{search}%')))
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    students = pagination.items
    
    student_list = []
    for student in students:
        # 获取学院、系和专业名称
        faculty_name = Faculty.query.get(student.faculty_id).name if student.faculty_id else ''
        department_name = Department.query.get(student.department_id).name if student.department_id else ''
        major_name = Major.query.get(student.major_id).name if student.major_id else ''
        
        student_data = {
            'id': student.id,
            'student_id': student.student_id,
            'student_name': student.student_name,
            'gender': student.gender,
            'faculty': faculty_name,
            'facultyId': student.faculty_id,
            'department': department_name,
            'departmentId': student.department_id,
            'major': major_name,
            'majorId': student.major_id,
            'cet4_score': student.cet4_score,
            'cet6_score': student.cet6_score,
            'gpa': student.gpa,
            'academic_score': student.academic_score,
                    'academic_specialty_total': student.academic_specialty_total,
            'comprehensive_performance_total': student.comprehensive_performance_total,
            'total_score': student.total_score,
            'comprehensive_score': student.comprehensive_score,
            'major_ranking': student.major_ranking,
            'total_students': student.total_students
        }
        student_list.append(student_data)
    
    # 返回分页数据
    return jsonify({
        'students': student_list,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200

# 获取单个学生信息接口
@user_bp.route('/admin/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({'message': '学生不存在'}), 404
    
    # 获取学院、系和专业名称
    faculty_name = Faculty.query.get(student.faculty_id).name if student.faculty_id else ''
    department_name = Department.query.get(student.department_id).name if student.department_id else ''
    major_name = Major.query.get(student.major_id).name if student.major_id else ''
    
    student_data = {
        'id': student.id,
        'student_id': student.student_id,
        'student_name': student.student_name,
        'gender': student.gender,
        'faculty': faculty_name,
        'facultyId': student.faculty_id,
        'department': department_name,
        'departmentId': student.department_id,
        'major': major_name,
        'majorId': student.major_id,
        'cet4_score': student.cet4_score,
        'cet6_score': student.cet6_score,
        'gpa': student.gpa,
        'academic_score': student.academic_score,
                    'academic_specialty_total': student.academic_specialty_total,
        'comprehensive_performance_total': student.comprehensive_performance_total,
        'total_score': student.total_score,
        'comprehensive_score': student.comprehensive_score,
        'major_ranking': student.major_ranking,
        'total_students': student.total_students
    }
    
    return jsonify({'student': student_data}), 200

# 创建学生信息接口
@user_bp.route('/admin/students', methods=['POST'])
def create_student():
    data = request.get_json()
    
    # 检查必要参数
    if not data.get('student_id') or not data.get('student_name') or not data.get('department_id') or not data.get('major_id'):
        return jsonify({'message': '缺少必要参数（学号、姓名、系ID、专业ID）'}), 400
    
    # 检查学号是否已存在
    existing_student = Student.query.filter_by(student_id=data['student_id']).first()
    if existing_student:
        return jsonify({'message': '学号已存在'}), 400
    
    # 创建新学生
    new_student = Student(
        student_id=data['student_id'],
        student_name=data['student_name'],
        gender=data.get('gender'),
        faculty_id=data.get('facultyId'),
        department_id=data.get('department_id'),
        major_id=data.get('major_id'),
        cet4_score=data.get('cet4_score'),
        cet6_score=data.get('cet6_score'),
        gpa=data.get('gpa'),
        academic_score=data.get('academic_score')
    )
    
    # 检查是否已存在对应的User记录
    existing_user = User.query.filter_by(username=data['student_id'], role='student').first()
    if existing_user:
        # 如果存在，建立关联
        existing_user.student_id = data['student_id']
        
    db.session.add(new_student)
    db.session.commit()
    
    return jsonify({'message': '学生创建成功', 'student_id': new_student.id}), 201

# 更新学生信息接口
@user_bp.route('/admin/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({'message': '学生不存在'}), 404
    
    data = request.get_json()
    
    # 更新学生信息
    if 'student_name' in data:
        student.student_name = data['student_name']
    if 'gender' in data:
        student.gender = data['gender']
    if 'facultyId' in data:
        student.faculty_id = data['facultyId']
    if 'department_id' in data:
        student.department_id = data['department_id']
    if 'major_id' in data:
        student.major_id = data['major_id']
    if 'cet4_score' in data:
        student.cet4_score = data['cet4_score']
    if 'cet6_score' in data:
        student.cet6_score = data['cet6_score']
    if 'gpa' in data:
        student.gpa = data['gpa']
    if 'academic_score' in data:
        student.academic_score = data['academic_score']
    # academic_weighted字段已移除，由academic_score自动计算
    if 'academic_specialty_total' in data:
        student.academic_specialty_total = data['academic_specialty_total']
    if 'comprehensive_performance_total' in data:
        student.comprehensive_performance_total = data['comprehensive_performance_total']
    if 'total_score' in data:
        student.total_score = data['total_score']
    if 'comprehensive_score' in data:
        student.comprehensive_score = data['comprehensive_score']
    if 'major_ranking' in data:
        student.major_ranking = data['major_ranking']
    if 'total_students' in data:
        student.total_students = data['total_students']
    
    db.session.commit()
    
    return jsonify({'message': '学生信息更新成功'}), 200

# 删除学生信息接口
@user_bp.route('/admin/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({'message': '学生不存在'}), 404
    
    # 先将关联的User记录的student_id设置为None
    user = User.query.filter_by(student_id=student.student_id).first()
    if user:
        user.student_id = None
    
    db.session.delete(student)
    db.session.commit()
    
    return jsonify({'message': '学生删除成功'}), 200