from flask import request, jsonify
from app import app, db
from models import User, Application
from datetime import datetime
import bcrypt

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
    
    # 验证密码（实际应用中应该使用bcrypt加密）
    if user.password != password:
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
        password=data['password'],  # 实际应用中应该使用bcrypt加密
        name=data['name'],
        role=data['role'],
        avatar='/images/头像1.jpg' if data['role'] == 'student' else '/images/头像2.jpg',
        faculty='信息学院',  # 默认值
        email='',  # 默认值
        phone=''   # 默认值
    )
    
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
    
    # 更新密码
    user.password = new_password  # 实际应用中应该使用bcrypt加密
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