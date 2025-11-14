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
    # 获取查询参数
    student_id = request.args.get('studentId')
    status = request.args.get('status')
    application_type = request.args.get('applicationType')
    
    # 构建查询
    query = Application.query
    
    if student_id:
        query = query.filter_by(student_id=student_id)
    
    if status:
        query = query.filter_by(status=status)
    
    if application_type:
        query = query.filter_by(application_type=application_type)
    
    applications = query.all()
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
            'reviewedBy': app.reviewed_by,
            # 学术专长相关字段
            'academicType': app.academic_type,
            'researchType': app.research_type,
            'innovationLevel': app.innovation_level,
            'innovationRole': app.innovation_role,
            'awardGrade': app.award_grade,
            'awardCategory': app.award_category,
            'authorRankType': app.author_rank_type,
            'authorOrder': app.author_order,
            # 综合表现相关字段
            'performanceType': app.performance_type,
            'performanceLevel': app.performance_level,
            'performanceParticipation': app.performance_participation,
            'teamRole': app.team_role
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
        'reviewedBy': app.reviewed_by,
        # 学术专长相关字段
        'academicType': app.academic_type,
        'researchType': app.research_type,
        'innovationLevel': app.innovation_level,
        'innovationRole': app.innovation_role,
        'awardGrade': app.award_grade,
        'awardCategory': app.award_category,
        'authorRankType': app.author_rank_type,
        'authorOrder': app.author_order,
        # 综合表现相关字段
        'performanceType': app.performance_type,
        'performanceLevel': app.performance_level,
        'performanceParticipation': app.performance_participation,
        'teamRole': app.team_role
    }
    
    return jsonify(app_data), 200

# 创建申请
@app.route('/api/applications', methods=['POST'])
def create_application():
    import json
    import os
    from werkzeug.utils import secure_filename
    from flask import abort
    
    try:
        # 解析申请数据
        if 'application' in request.form:
            data = json.loads(request.form['application'])
        else:
            data = request.get_json()
    
        # 字段名转换：将前端的驼峰式命名转换为后端的下划线命名
        field_mapping = {
            'studentId': 'student_id',
            'studentName': 'student_name',
            'name': 'student_name',  # 兼容前端可能使用的name字段
            'department': 'department',
            'major': 'major',
            'applicationType': 'application_type',
            'selfScore': 'self_score',
            'projectName': 'project_name',
            'awardDate': 'award_date',
            'awardLevel': 'award_level',
            'awardType': 'award_type',
            'academicType': 'academic_type',
            'researchType': 'research_type',
            'innovationLevel': 'innovation_level',
            'innovationRole': 'innovation_role',
            'awardGrade': 'award_grade',
            'awardCategory': 'award_category',
            'authorRankType': 'author_rank_type',
            'authorOrder': 'author_order',
            'performanceType': 'performance_type',
            'performanceLevel': 'performance_level',
            'performanceParticipation': 'performance_participation',
            'teamRole': 'team_role',
            'finalScore': 'final_score',
            'reviewComment': 'review_comment',
            'reviewedAt': 'reviewed_at',
            'reviewedBy': 'reviewed_by',
            'appliedAt': 'applied_at',
            'createdAt': 'created_at',
            'updatedAt': 'updated_at'
        }
        
        # 转换数据字段
        transformed_data = {}
        for key, value in data.items():
            # 使用映射的字段名，如果没有映射则使用原字段名
            new_key = field_mapping.get(key, key)
            transformed_data[new_key] = value
        
        # 使用转换后的数据
        data = transformed_data
        
        # 处理文件上传
        files = []
        if request.files:
            # 创建上传目录（如果不存在）
            upload_dir = os.path.join(os.getcwd(), 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # 保存文件并记录信息
            for key, file in request.files.items():
                if file and file.filename:
                    # 安全地保存文件
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(upload_dir, filename)
                    file.save(filepath)
                    
                    # 记录文件信息
                    files.append({
                        'name': filename,
                        'path': filepath,
                        'size': file.content_length,
                        'type': file.content_type
                    })
        
        new_application = Application(
            student_id=data['student_id'],
            student_name=data['student_name'],
            department=data['department'],
            major=data['major'],
            application_type=data['application_type'],
            applied_at=datetime.utcnow(),
            self_score=data['self_score'],
            status=data.get('status', 'pending'),
            project_name=data['project_name'],
            award_date=datetime.fromisoformat(data['award_date']).date(),
            award_level=data.get('award_level'),
            award_type=data.get('award_type'),
            description=data['description'],
            files=files,
            # 学术专长相关字段
            academic_type=data.get('academic_type'),
            research_type=data.get('research_type'),
            innovation_level=data.get('innovation_level'),
            innovation_role=data.get('innovation_role'),
            award_grade=data.get('award_grade'),
            award_category=data.get('award_category'),
            author_rank_type=data.get('author_rank_type'),
            author_order=data.get('author_order'),
            # 综合表现相关字段
            performance_type=data.get('performance_type'),
            performance_level=data.get('performance_level'),
            performance_participation=data.get('performance_participation'),
            team_role=data.get('team_role')
        )
        
        db.session.add(new_application)
        db.session.commit()
        
        return jsonify({'message': '申请创建成功', 'id': new_application.id}), 201
    except json.JSONDecodeError as e:
        return jsonify({'error': '无效的JSON格式', 'details': str(e)}), 400
    except KeyError as e:
        return jsonify({'error': f'缺少必要字段: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': f'数据格式错误: {str(e)}'}), 400
    except Exception as e:
        import traceback
        error_msg = f"发生未预期的错误: {str(e)}"
        traceback_str = traceback.format_exc()
        print(error_msg)
        print("详细错误堆栈:")
        print(traceback_str)
        print("请求数据:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return jsonify({'error': '服务器内部错误', 'details': str(e), 'traceback': traceback_str}), 500

# 更新申请
@app.route('/api/applications/<int:id>', methods=['PUT'])
def update_application(id):
    app = Application.query.get_or_404(id)
    data = request.get_json()
    
    # 更新基本信息
    app.self_score = data.get('selfScore', app.self_score)
    app.status = data.get('status', app.status)
    app.project_name = data.get('projectName', app.project_name)
    app.award_date = datetime.fromisoformat(data['awardDate']).date() if 'awardDate' in data else app.award_date
    app.award_level = data.get('awardLevel', app.award_level)
    app.award_type = data.get('awardType', app.award_type)
    app.description = data.get('description', app.description)
    app.files = data.get('files', app.files)
    
    # 更新学术专长相关字段
    app.academic_type = data.get('academicType', app.academic_type)
    app.research_type = data.get('researchType', app.research_type)
    app.innovation_level = data.get('innovationLevel', app.innovation_level)
    app.innovation_role = data.get('innovationRole', app.innovation_role)
    app.award_grade = data.get('awardGrade', app.award_grade)
    app.award_category = data.get('awardCategory', app.award_category)
    app.author_rank_type = data.get('authorRankType', app.author_rank_type)
    app.author_order = data.get('authorOrder', app.author_order)
    
    # 更新综合表现相关字段
    app.performance_type = data.get('performanceType', app.performance_type)
    app.performance_level = data.get('performanceLevel', app.performance_level)
    app.performance_participation = data.get('performanceParticipation', app.performance_participation)
    app.team_role = data.get('teamRole', app.team_role)
    
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
    # 获取查询参数
    department = request.args.get('department')
    major = request.args.get('major')
    application_type = request.args.get('applicationType')
    
    # 构建查询
    query = Application.query.filter_by(status='pending')
    
    if department:
        query = query.filter_by(department=department)
    
    if major:
        query = query.filter_by(major=major)
    
    if application_type:
        query = query.filter_by(application_type=application_type)
    
    applications = query.all()
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
            # 学术专长相关字段
            'academicType': app.academic_type,
            'researchType': app.research_type,
            'innovationLevel': app.innovation_level,
            'innovationRole': app.innovation_role,
            'awardGrade': app.award_grade,
            'awardCategory': app.award_category,
            'authorRankType': app.author_rank_type,
            'authorOrder': app.author_order,
            # 综合表现相关字段
            'performanceType': app.performance_type,
            'performanceLevel': app.performance_level,
            'performanceParticipation': app.performance_participation,
            'teamRole': app.team_role
        }
        app_list.append(app_data)
    
    return jsonify(app_list), 200

# 健康检查接口
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200