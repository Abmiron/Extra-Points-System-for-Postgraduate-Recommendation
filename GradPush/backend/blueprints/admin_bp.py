# -*- coding: utf-8 -*-
"""
管理员管理蓝图

该文件负责处理管理员相关的API端点，包括：
- 学院管理（增删改查）
- 系管理（增删改查）
- 专业管理（增删改查）
"""

from flask import Blueprint, request, jsonify, make_response
from models import Faculty, Department, Major, User, SystemSettings
from datetime import datetime
from extensions import db

# 创建蓝图实例
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# CORS已在app.py中全局配置，无需在此处重复设置

# 学院管理API

# 获取所有学院
@admin_bp.route('/faculties', methods=['GET'])
def get_faculties():
    faculties = Faculty.query.all()
    result = []
    for faculty in faculties:
        result.append({
            'id': faculty.id,
            'name': faculty.name,
            'description': faculty.description,
            'created_at': faculty.created_at.isoformat(),
            'updated_at': faculty.updated_at.isoformat()
        })
    return make_response(jsonify({'faculties': result}), 200)

# 创建学院
@admin_bp.route('/faculties', methods=['POST'])
def create_faculty():
    data = request.get_json()
    
    # 检查学院是否已存在
    existing_faculty = Faculty.query.filter_by(name=data['name']).first()
    if existing_faculty:
        return jsonify({'message': '学院已存在'}), 400
    
    # 创建新学院
    new_faculty = Faculty(
        name=data['name'],
        description=data.get('description', '')
    )
    
    db.session.add(new_faculty)
    db.session.commit()
    
    return jsonify({'message': '学院创建成功', 'faculty': {
        'id': new_faculty.id,
        'name': new_faculty.name,
        'description': new_faculty.description
    }}), 201

# 更新学院
@admin_bp.route('/faculties/<int:faculty_id>', methods=['PUT'])
def update_faculty(faculty_id):
    data = request.get_json()
    faculty = Faculty.query.get(faculty_id)
    
    if not faculty:
        return jsonify({'message': '学院不存在'}), 404
    
    # 检查学院名称是否已被其他学院使用
    existing_faculty = Faculty.query.filter_by(name=data['name']).filter(Faculty.id != faculty_id).first()
    if existing_faculty:
        return jsonify({'message': '学院名称已存在'}), 400
    
    faculty.name = data['name']
    faculty.description = data.get('description', '')
    
    db.session.commit()
    
    return jsonify({'message': '学院更新成功', 'faculty': {
        'id': faculty.id,
        'name': faculty.name,
        'description': faculty.description
    }}), 200

# 删除学院
@admin_bp.route('/faculties/<int:faculty_id>', methods=['DELETE'])
def delete_faculty(faculty_id):
    faculty = Faculty.query.get(faculty_id)
    
    if not faculty:
        return jsonify({'message': '学院不存在'}), 404
    
    # 检查是否有系关联到该学院
    if faculty.departments:
        return jsonify({'message': '该学院下存在系，无法删除'}), 400
    
    db.session.delete(faculty)
    db.session.commit()
    
    return jsonify({'message': '学院删除成功'}), 200

# 系管理API

# 获取所有系（可按学院筛选）
@admin_bp.route('/departments', methods=['GET'])
def get_departments():
    faculty_id = request.args.get('faculty_id')
    
    if faculty_id:
        departments = Department.query.filter_by(faculty_id=faculty_id).all()
    else:
        departments = Department.query.all()
    
    result = []
    # 获取所有相关学院信息以避免N+1查询问题
    faculty_ids = {dept.faculty_id for dept in departments}
    faculties = Faculty.query.filter(Faculty.id.in_(faculty_ids)).all()
    faculty_dict = {f.id: f.name for f in faculties}
    
    result = []
    for department in departments:
        result.append({
            'id': department.id,
            'name': department.name,
            'faculty_id': department.faculty_id,
            'faculty_name': faculty_dict.get(department.faculty_id, '未知学院'),
            'description': department.description,
            'created_at': department.created_at.isoformat(),
            'updated_at': department.updated_at.isoformat()
        })
    return make_response(jsonify({'departments': result}), 200)

# 创建系
@admin_bp.route('/departments', methods=['POST'])
def create_department():
    data = request.get_json()
    
    # 检查系是否已存在于同一学院
    existing_department = Department.query.filter_by(
        name=data['name'], 
        faculty_id=data['faculty_id']
    ).first()
    if existing_department:
        return jsonify({'message': '该学院下已存在同名系'}), 400
    
    # 创建新系
    new_department = Department(
        name=data['name'],
        faculty_id=data['faculty_id'],
        description=data.get('description', '')
    )
    
    db.session.add(new_department)
    db.session.commit()
    
    return jsonify({'message': '系创建成功', 'department': {
        'id': new_department.id,
        'name': new_department.name,
        'faculty_id': new_department.faculty_id,
        'description': new_department.description
    }}), 201

# 更新系
@admin_bp.route('/departments/<int:department_id>', methods=['PUT'])
def update_department(department_id):
    data = request.get_json()
    department = Department.query.get(department_id)
    
    if not department:
        return jsonify({'message': '系不存在'}), 404
    
    # 检查系名称是否已被同一学院的其他系使用
    existing_department = Department.query.filter_by(
        name=data['name'], 
        faculty_id=data['faculty_id']
    ).filter(Department.id != department_id).first()
    if existing_department:
        return jsonify({'message': '该学院下已存在同名系'}), 400
    
    department.name = data['name']
    department.faculty_id = data['faculty_id']
    department.description = data.get('description', '')
    
    db.session.commit()
    
    return jsonify({'message': '系更新成功', 'department': {
        'id': department.id,
        'name': department.name,
        'faculty_id': department.faculty_id,
        'description': department.description
    }}), 200

# 删除系
@admin_bp.route('/departments/<int:department_id>', methods=['DELETE'])
def delete_department(department_id):
    department = Department.query.get(department_id)
    
    if not department:
        return jsonify({'message': '系不存在'}), 404
    
    # 检查是否有专业关联到该系
    if department.majors:
        return jsonify({'message': '该系下存在专业，无法删除'}), 400
    
    db.session.delete(department)
    db.session.commit()
    
    return jsonify({'message': '系删除成功'}), 200

# 专业管理API

# 获取所有专业（可按学院或系筛选）
@admin_bp.route('/majors', methods=['GET'])
def get_majors():
    department_id = request.args.get('department_id')
    faculty_id = request.args.get('faculty_id')
    
    if department_id:
        majors = Major.query.filter_by(department_id=department_id).all()
    elif faculty_id:
        # 按学院筛选专业（通过系表关联）
        majors = Major.query.join(Department).filter(Department.faculty_id == faculty_id).all()
    else:
        majors = Major.query.all()
    
    result = []
    # 获取所有相关系和学院信息以避免N+1查询问题
    department_ids = {maj.department_id for maj in majors}
    departments = Department.query.filter(Department.id.in_(department_ids)).all()
    department_dict = {d.id: d.name for d in departments}
    
    faculty_ids = {d.faculty_id for d in departments}
    faculties = Faculty.query.filter(Faculty.id.in_(faculty_ids)).all()
    faculty_dict = {f.id: f.name for f in faculties}
    faculty_id_map = {d.id: d.faculty_id for d in departments}
    
    result = []
    for major in majors:
        dept_id = major.department_id
        result.append({
            'id': major.id,
            'name': major.name,
            'department_id': dept_id,
            'department_name': department_dict.get(dept_id, '未知系'),
            'faculty_id': faculty_id_map.get(dept_id, 0),
            'faculty_name': faculty_dict.get(faculty_id_map.get(dept_id), '未知学院'),
            'description': major.description,
            'created_at': major.created_at.isoformat(),
            'updated_at': major.updated_at.isoformat()
        })
    return make_response(jsonify({'majors': result}), 200)

# 创建专业
@admin_bp.route('/majors', methods=['POST'])
def create_major():
    data = request.get_json()
    
    # 检查专业是否已存在于同系
    existing_major = Major.query.filter_by(
        name=data['name'], 
        department_id=data['department_id']
    ).first()
    if existing_major:
        return jsonify({'message': '该系下已存在同名专业'}), 400
    
    # 创建新专业
    new_major = Major(
        name=data['name'],
        department_id=data['department_id'],
        description=data.get('description', '')
    )
    
    db.session.add(new_major)
    db.session.commit()
    
    return jsonify({'message': '专业创建成功', 'major': {
        'id': new_major.id,
        'name': new_major.name,
        'department_id': new_major.department_id,
        'description': new_major.description
    }}), 201

# 更新专业
@admin_bp.route('/majors/<int:major_id>', methods=['PUT'])
def update_major(major_id):
    data = request.get_json()
    major = Major.query.get(major_id)
    
    if not major:
        return jsonify({'message': '专业不存在'}), 404
    
    # 检查专业名称是否已被同系的其他专业使用
    existing_major = Major.query.filter_by(
        name=data['name'], 
        department_id=data['department_id']
    ).filter(Major.id != major_id).first()
    if existing_major:
        return jsonify({'message': '该系下已存在同名专业'}), 400
    
    major.name = data['name']
    major.department_id = data['department_id']
    major.description = data.get('description', '')
    
    db.session.commit()
    
    return jsonify({'message': '专业更新成功', 'major': {
        'id': major.id,
        'name': major.name,
        'department_id': major.department_id,
        'description': major.description
    }}), 200

# 删除专业
@admin_bp.route('/majors/<int:major_id>', methods=['DELETE'])
def delete_major(major_id):
    major = Major.query.get(major_id)
    
    if not major:
        return jsonify({'message': '专业不存在'}), 404
    
    db.session.delete(major)
    db.session.commit()
    
    return jsonify({'message': '专业删除成功'}), 200

# 系统设置API

# 获取系统设置
@admin_bp.route('/system-settings', methods=['GET'])
def get_system_settings():
    # 获取唯一的系统设置记录，如果不存在则创建默认记录
    settings = SystemSettings.query.first()
    if not settings:
        # 创建默认设置
        settings = SystemSettings()
        db.session.add(settings)
        db.session.commit()
    
    # 转换为JSON格式
    settings_data = {
        'academicYear': settings.academic_year,
        'applicationStart': settings.application_start.isoformat() if settings.application_start else None,
        'applicationEnd': settings.application_end.isoformat() if settings.application_end else None,
        'fileSizeLimit': settings.file_size_limit,
        'allowedFileTypes': settings.allowed_file_types,
        'academicScoreWeight': settings.academic_score_weight,
        'specialtyScoreWeight': settings.specialty_score_weight,
        'performanceScoreWeight': settings.performance_score_weight,
        'systemStatus': settings.system_status,
        'lastBackup': settings.last_backup.isoformat() if settings.last_backup else None
    }
    
    return jsonify({'settings': settings_data}), 200

# 更新系统设置
@admin_bp.route('/system-settings', methods=['PUT'])
def update_system_settings():
    data = request.get_json()
    
    # 获取唯一的系统设置记录，如果不存在则创建
    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings()
        db.session.add(settings)
    
    # 更新设置
    if 'academicYear' in data:
        settings.academic_year = data['academicYear']
    
    if 'applicationStart' in data and data['applicationStart']:
        settings.application_start = datetime.fromisoformat(data['applicationStart']).date()
    
    if 'applicationEnd' in data and data['applicationEnd']:
        settings.application_end = datetime.fromisoformat(data['applicationEnd']).date()
    
    if 'fileSizeLimit' in data:
        settings.file_size_limit = data['fileSizeLimit']
    
    if 'allowedFileTypes' in data:
        settings.allowed_file_types = data['allowedFileTypes']
    
    if 'academicScoreWeight' in data:
        settings.academic_score_weight = data['academicScoreWeight']
    
    if 'specialtyScoreWeight' in data:
        settings.specialty_score_weight = data['specialtyScoreWeight']
    
    if 'performanceScoreWeight' in data:
        settings.performance_score_weight = data['performanceScoreWeight']
    
    if 'systemStatus' in data:
        settings.system_status = data['systemStatus']
    
    if 'lastBackup' in data and data['lastBackup']:
        settings.last_backup = datetime.fromisoformat(data['lastBackup'])
    
    db.session.commit()
    
    # 返回更新后的设置
    updated_settings = {
        'academicYear': settings.academic_year,
        'applicationStart': settings.application_start.isoformat() if settings.application_start else None,
        'applicationEnd': settings.application_end.isoformat() if settings.application_end else None,
        'fileSizeLimit': settings.file_size_limit,
        'allowedFileTypes': settings.allowed_file_types,
        'academicScoreWeight': settings.academic_score_weight,
        'specialtyScoreWeight': settings.specialty_score_weight,
        'performanceScoreWeight': settings.performance_score_weight,
        'systemStatus': settings.system_status,
        'lastBackup': settings.last_backup.isoformat() if settings.last_backup else None
    }
    
    return jsonify({'message': '系统设置更新成功', 'settings': updated_settings}), 200