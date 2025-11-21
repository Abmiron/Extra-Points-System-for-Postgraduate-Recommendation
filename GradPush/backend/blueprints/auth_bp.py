# -*- coding: utf-8 -*-
"""
用户认证蓝图

该文件负责处理用户认证相关的API端点，包括：
- 登录
- 注册
- 密码重置
"""

from flask import Blueprint, request, jsonify, make_response, session
from models import User, Faculty, Department, Major, Student
from datetime import datetime, timedelta
import pytz
from extensions import db
from utils.captcha import generate_captcha
import base64
from io import BytesIO
import uuid
import threading

# 用于存储验证码的临时字典
# 使用token作为键，值为(验证码文本, 生成时间)的元组
captcha_store = {}
# 用于线程安全的锁
captcha_lock = threading.Lock()

# 清理过期验证码的函数
def cleanup_expired_captchas():
    current_time = datetime.now()
    with captcha_lock:
        # 找出所有过期的验证码（超过5分钟）
        expired_tokens = [
            token for token, (_, timestamp) in captcha_store.items()
            if (current_time - timestamp).total_seconds() > 300
        ]
        # 删除过期的验证码
        for token in expired_tokens:
            del captcha_store[token]
        if expired_tokens:
            print(f"清理了{len(expired_tokens)}个过期验证码")

# 创建蓝图
auth_bp = Blueprint('auth', __name__, url_prefix="/api")


# 验证码生成接口
@auth_bp.route("/generate-captcha", methods=["GET"])
def get_captcha():
    try:
        # 先清理过期的验证码
        cleanup_expired_captchas()
        
        # 生成验证码图片和文本
        # 注意：根据captcha.py的实现，返回值顺序是 (captcha_image, captcha_text)
        captcha_image, captcha_text = generate_captcha()
        
        print(f"生成验证码: {captcha_text}")
        
        # 生成唯一的token
        captcha_token = str(uuid.uuid4())
        
        # 存储验证码和生成时间
        with captcha_lock:
            captcha_store[captcha_token] = (captcha_text.lower(), datetime.now())
        print(f"验证码已存储，token: {captcha_token}")
        
        # 将图片转换为base64字符串
        buffer = BytesIO()
        captcha_image.save(buffer, format='PNG')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'image': img_str,
            'token': captcha_token
        }), 200
    except Exception as e:
        print(f"验证码生成错误: {str(e)}")
        return jsonify({"message": "验证码生成失败"}), 500


# 登录接口 - OPTIONS请求处理
@auth_bp.route("/login", methods=["OPTIONS"])
def login_options():
    response = make_response()
    return response


# 登录接口 - POST请求处理
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    captcha_input = data.get("captcha")
    captcha_token = data.get("captchaToken")
    
    if not username or not password:
        return jsonify({"message": "用户名和密码不能为空"}), 400
    
    if not captcha_input:
        return jsonify({"message": "验证码不能为空"}), 400
    
    if not captcha_token:
        return jsonify({"message": "验证码token不能为空"}), 400
    
    # 验证验证码
    print(f"验证验证码: 输入={captcha_input.lower()}, token={captcha_token}")
    
    # 检查验证码是否存在
    with captcha_lock:
        if captcha_token not in captcha_store:
            print("验证码验证失败：未找到对应的验证码")
            return jsonify({"message": "验证码不存在，请刷新页面获取验证码"}), 400
        
        # 获取存储的验证码和时间
        stored_captcha, captcha_timestamp = captcha_store[captcha_token]
    
    # 检查验证码是否过期（5分钟过期）
    current_time = datetime.now()
    time_diff = (current_time - captcha_timestamp).total_seconds()
    print(f"验证码时间差: {time_diff}秒")
    
    # 设置5分钟（300秒）的过期时间
    if time_diff > 300:
        print("验证码已过期")
        # 清除过期的验证码
        with captcha_lock:
            captcha_store.pop(captcha_token, None)
        return jsonify({"message": "验证码已过期，请刷新页面获取新验证码"}), 400
    
    # 验证验证码内容
    if captcha_input.lower() != stored_captcha:
        print(f"验证码不匹配：输入={captcha_input.lower()}, 存储={stored_captcha}")
        return jsonify({"message": "验证码错误"}), 400
    
    # 验证成功后删除验证码
    with captcha_lock:
        captcha_store.pop(captcha_token, None)
    
    print("验证码验证成功")

    # 查找用户
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "用户不存在"}), 401

    if user.status == "disabled":
        return jsonify({"message": "账户已被禁用"}), 401

    # 验证密码
    if not user.check_password(password):
        return jsonify({"message": "密码错误"}), 401
    
    # 验证码已在验证成功后删除

    # 更新最后登录时间
    user.last_login = datetime.now(pytz.timezone("Asia/Shanghai"))
    db.session.commit()

    # 获取学院、系和专业名称

    # 安全获取关联对象的名称
    faculty = Faculty.query.get(user.faculty_id) if user.faculty_id else None
    faculty_name = faculty.name if faculty else ""

    department = (
        Department.query.get(user.department_id) if user.department_id else None
    )
    department_name = department.name if department else ""

    major = Major.query.get(user.major_id) if user.major_id else None
    major_name = major.name if major else ""

    # 返回用户信息（不包含密码）
    user_data = {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "role": user.role,
        "avatar": user.avatar,
        "faculty": faculty_name,
        "facultyId": user.faculty_id,
        "department": department_name,
        "departmentId": user.department_id,
        "major": major_name,
        "majorId": user.major_id,
        "studentId": user.student_id,
        "email": user.email,
        "phone": user.phone,
        "roleName": user.role_name,
        "lastLogin": user.last_login.isoformat() if user.last_login else None,
    }

    # 返回用户信息（不包含密码）
    return jsonify({"user": user_data, "message": "登录成功"}), 200


# 注册接口
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # 基本数据验证
    if not data:
        return jsonify({"message": "请求数据不能为空"}), 400
    
    # 验证码验证
    captcha_input = data.get("captcha")
    captcha_token = data.get("captchaToken")
    
    if not captcha_input:
        return jsonify({"message": "验证码不能为空"}), 400
    
    if not captcha_token:
        return jsonify({"message": "验证码token不能为空"}), 400
    
    # 验证验证码
    print(f"验证验证码: 输入={captcha_input.lower()}, token={captcha_token}")
    
    # 检查验证码是否存在
    with captcha_lock:
        if captcha_token not in captcha_store:
            print("验证码验证失败：未找到对应的验证码")
            return jsonify({"message": "验证码不存在，请刷新页面获取验证码"}), 400
        
        # 获取存储的验证码和时间
        stored_captcha, captcha_timestamp = captcha_store[captcha_token]
    
    # 检查验证码是否过期（5分钟过期）
    current_time = datetime.now()
    time_diff = (current_time - captcha_timestamp).total_seconds()
    print(f"验证码时间差: {time_diff}秒")
    
    # 设置5分钟（300秒）的过期时间
    if time_diff > 300:
        print("验证码已过期")
        # 清除过期的验证码
        with captcha_lock:
            captcha_store.pop(captcha_token, None)
        return jsonify({"message": "验证码已过期，请刷新页面获取新验证码"}), 400
    
    # 验证验证码内容
    if captcha_input.lower() != stored_captcha:
        print(f"验证码不匹配：输入={captcha_input.lower()}, 存储={stored_captcha}")
        return jsonify({"message": "验证码错误"}), 400
    
    # 验证成功后删除验证码
    with captcha_lock:
        captcha_store.pop(captcha_token, None)
    
    print("验证码验证成功")

    required_fields = ["username", "name", "role", "password"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"message": f"{field}是必填字段"}), 400

    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=data["username"]).first()
    if existing_user:
        return jsonify({"message": "用户名已存在"}), 400

    # 获取关联ID
    faculty_id = data.get("facultyId")
    department_id = data.get("departmentId")
    major_id = data.get("majorId")

    # 学生角色验证
    if data["role"] == "student":
        # 验证学生必填的关联字段
        if not faculty_id or not department_id or not major_id:
            return jsonify({"message": "学生注册必须选择学院、系和专业"}), 400

        # 验证关联ID是否存在
        faculty = Faculty.query.get(faculty_id)
        department = Department.query.get(department_id)
        major = Major.query.get(major_id)

        if not faculty:
            return jsonify({"message": "学院不存在"}), 400
        if not department:
            return jsonify({"message": "系不存在"}), 400
        if not major:
            return jsonify({"message": "专业不存在"}), 400

    try:
        # 学生角色需要先处理Student记录
        student_id = None
        if data["role"] == "student":
            # 检查是否已存在对应的Student记录
            existing_student = Student.query.filter_by(
                student_id=data["username"]
            ).first()
            if not existing_student:
                # 如果不存在，创建新的Student记录
                new_student = Student(
                    student_id=data["username"],
                    student_name=data["name"],
                    faculty_id=faculty_id,
                    department_id=department_id,
                    major_id=major_id,
                )
                db.session.add(new_student)
                db.session.flush()  # 立即刷新以确保学生记录已创建
            student_id = data["username"]

        # 创建新用户
        new_user = User(
            username=data["username"],
            name=data["name"],
            role=data["role"],
            avatar="/images/default-avatar.jpg",  # 统一使用默认头像
            faculty_id=faculty_id,
            department_id=department_id if data["role"] == "student" else None,
            major_id=major_id if data["role"] == "student" else None,
            student_id=student_id,
            email="",  # 默认值
            phone="",  # 默认值
            role_name="审核员" if data["role"] == "teacher" else None,  # 默认值
        )

        # 设置密码（哈希）- 如果没有提供密码，使用默认密码
        new_user.set_password(data.get("password", "123456"))

        db.session.add(new_user)

        # 提交事务
        db.session.commit()

        return jsonify({"message": "注册成功"}), 201
    except Exception as e:
        # 发生异常时回滚事务
        db.session.rollback()
        return jsonify({"message": f"注册失败: {str(e)}"}), 500


# 密码重置接口
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    
    # 验证码验证
    captcha_input = data.get("captcha")
    captcha_token = data.get("captchaToken")
    
    if not captcha_input:
        return jsonify({"message": "验证码不能为空"}), 400
    
    if not captcha_token:
        return jsonify({"message": "验证码token不能为空"}), 400
    
    # 验证验证码
    print(f"验证验证码: 输入={captcha_input.lower()}, token={captcha_token}")
    
    # 检查验证码是否存在
    with captcha_lock:
        if captcha_token not in captcha_store:
            print("验证码验证失败：未找到对应的验证码")
            return jsonify({"message": "验证码不存在，请刷新页面获取验证码"}), 400
        
        # 获取存储的验证码和时间
        stored_captcha, captcha_timestamp = captcha_store[captcha_token]
    
    # 检查验证码是否过期（5分钟过期）
    current_time = datetime.now()
    time_diff = (current_time - captcha_timestamp).total_seconds()
    print(f"验证码时间差: {time_diff}秒")
    
    # 设置5分钟（300秒）的过期时间
    if time_diff > 300:
        print("验证码已过期")
        # 清除过期的验证码
        with captcha_lock:
            captcha_store.pop(captcha_token, None)
        return jsonify({"message": "验证码已过期，请刷新页面获取新验证码"}), 400
    
    # 验证验证码内容
    if captcha_input.lower() != stored_captcha:
        print(f"验证码不匹配：输入={captcha_input.lower()}, 存储={stored_captcha}")
        return jsonify({"message": "验证码错误"}), 400
    
    # 验证成功后删除验证码
    with captcha_lock:
        captcha_store.pop(captcha_token, None)
    
    print("验证码验证成功")
    
    username = data.get("username")
    new_password = data.get("newPassword")

    # 查找用户
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "用户不存在"}), 404

    # 设置新密码
    user.set_password(new_password)

    db.session.commit()

    return jsonify({"message": "密码重置成功"}), 200


# 获取所有学院（用于注册选择）
@auth_bp.route("/faculties", methods=["GET"])
def get_faculties():
    faculties = Faculty.query.all()
    result = []
    for faculty in faculties:
        result.append({"id": faculty.id, "name": faculty.name})
    return jsonify({"faculties": result}), 200


# 根据学院ID获取系列表（用于注册选择）
@auth_bp.route("/departments/<int:faculty_id>", methods=["GET"])
def get_departments_by_faculty(faculty_id):
    departments = Department.query.filter_by(faculty_id=faculty_id).all()
    result = []
    for department in departments:
        result.append({"id": department.id, "name": department.name})
    return jsonify({"departments": result}), 200


# 获取所有专业列表
@auth_bp.route("/majors", methods=["GET"])
def get_all_majors():
    majors = Major.query.all()
    result = []
    for major in majors:
        result.append({"id": major.id, "name": major.name})
    return jsonify({"majors": result}), 200


# 根据系ID获取专业列表（用于注册选择）
@auth_bp.route("/majors/<int:department_id>", methods=["GET"])
def get_majors_by_department(department_id):
    majors = Major.query.filter_by(department_id=department_id).all()
    result = []
    for major in majors:
        result.append({"id": major.id, "name": major.name})
    return jsonify({"majors": result}), 200
