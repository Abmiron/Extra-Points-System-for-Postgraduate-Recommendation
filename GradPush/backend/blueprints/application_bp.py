# -*- coding: utf-8 -*-
"""
申请管理蓝图

该文件负责处理申请管理相关的API端点，包括：
- 获取所有申请
- 获取单个申请
- 创建申请
- 更新申请
- 审核申请
- 删除申请
- 获取待审核申请
"""

from flask import Blueprint, request, jsonify, abort, current_app
from models import Application, Student, PerformanceDetail, Rule
from datetime import datetime
import json
import os
import traceback
import uuid
from werkzeug.utils import secure_filename
# 不再直接导入app，而是使用current_app

# 创建蓝图实例
application_bp = Blueprint('application', __name__, url_prefix='/api')

# 获取所有申请
@application_bp.route('/applications', methods=['GET'])
def get_applications():
    # 获取查询参数
    student_id = request.args.get('studentId')
    student_name = request.args.get('studentName')
    status = request.args.get('status')
    application_type = request.args.get('applicationType')
    reviewed_by = request.args.get('reviewedBy')
    reviewed_start_date = request.args.get('reviewedStartDate')
    reviewed_end_date = request.args.get('reviewedEndDate')
    department_id = request.args.get('departmentId')
    major_id = request.args.get('majorId')
    department_name = request.args.get('department')
    major_name = request.args.get('major')
    
    # 构建查询
    query = Application.query
    
    if student_id:
        query = query.filter(Application.student_id.like(f'%{student_id}%'))
    
    if student_name:
        query = query.filter(Application.student_name.like(f'%{student_name}%'))
    
    if status:
        query = query.filter_by(status=status)
    
    if application_type:
        query = query.filter_by(application_type=application_type)
    
    if reviewed_by:
        query = query.filter(Application.reviewed_by.like(f'%{reviewed_by}%'))
    
    if department_id:
        query = query.filter_by(department_id=department_id)
    elif department_name:
        # 按系名称筛选（支持部分匹配）
        from models import Department
        # 先根据名称获取所有匹配的系ID
        departments = Department.query.filter(Department.name.like(f'%{department_name}%')).all()
        if departments:
            department_ids = [dept.id for dept in departments]
            query = query.filter(Application.department_id.in_(department_ids))
    
    if major_id:
        query = query.filter_by(major_id=major_id)
    elif major_name:
        # 按专业名称筛选（支持部分匹配）
        from models import Major
        # 先根据名称获取所有匹配的专业ID
        majors = Major.query.filter(Major.name.like(f'%{major_name}%')).all()
        if majors:
            major_ids = [major.id for major in majors]
            query = query.filter(Application.major_id.in_(major_ids))
    
    # 审核时间筛选
    if reviewed_start_date:
        try:
            # 转换为datetime对象
            start_date = datetime.fromisoformat(reviewed_start_date)
            query = query.filter(Application.reviewed_at >= start_date)
        except (ValueError, TypeError):
            # 如果日期格式无效，忽略该筛选条件
            pass
    
    if reviewed_end_date:
        try:
            # 转换为datetime对象，并设置为当天结束时间
            end_date = datetime.fromisoformat(reviewed_end_date)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(Application.reviewed_at <= end_date)
        except (ValueError, TypeError):
            # 如果日期格式无效，忽略该筛选条件
            pass
    
    applications = query.all()
    app_list = []
    
    # 获取所有相关系、专业和规则信息以避免N+1查询问题
    from models import Department, Major, Rule
    
    department_ids = {app.department_id for app in applications}
    departments = Department.query.filter(Department.id.in_(department_ids)).all()
    department_dict = {d.id: d.name for d in departments}
    
    major_ids = {app.major_id for app in applications}
    majors = Major.query.filter(Major.id.in_(major_ids)).all()
    major_dict = {m.id: m.name for m in majors}
    
    # 获取所有规则信息
    rule_ids = {app.rule_id for app in applications if app.rule_id}
    rules = Rule.query.filter(Rule.id.in_(rule_ids)).all()
    rule_dict = {r.id: {'id': r.id, 'name': r.name, 'score': r.score} for r in rules}
    
    for app in applications:
        # 转换文件路径格式
        processed_files = []
        if app.files:
            for file in app.files:
                # 确保processed_file是字典类型以便处理
                if isinstance(file, dict):
                    processed_file = file.copy()
                    # 保留原文件的size字段
                    if 'size' in file:
                        processed_file['size'] = file['size']
                    
                    # 如果是本地绝对路径，转换为相对URL
                    if 'path' in processed_file and os.path.isabs(processed_file['path']):
                        # 从绝对路径中提取文件名和子文件夹
                        filename = os.path.basename(processed_file['path'])
                        # 判断文件应该属于哪个子文件夹
                        if 'avatars' in processed_file['path']:
                            processed_file['path'] = f'/uploads/avatars/{filename}'
                        else:
                            # 默认将其他文件归类到files文件夹
                            processed_file['path'] = f'/uploads/files/{filename}'
                else:
                    # 如果file不是字典类型，尝试将其转换为字典
                    try:
                        processed_file = dict(file)
                    except:
                        # 如果转换失败，使用默认空字典
                        processed_file = {}
                processed_files.append(processed_file)
        
        app_data = {
            'id': app.id,
            'studentId': app.student_id,
            'studentName': app.student_name,
            'departmentId': app.department_id,
            'department': department_dict.get(app.department_id, '未知系'),
            'majorId': app.major_id,
            'major': major_dict.get(app.major_id, '未知专业'),
            'applicationType': app.application_type,
            'appliedAt': app.applied_at.isoformat() if app.applied_at else None,
            'selfScore': app.self_score,
            'finalScore': app.final_score,
            'status': app.status,
            'reviewComment': app.review_comment,
            'reviewedAt': app.reviewed_at.isoformat() if app.reviewed_at else None,
            'reviewedBy': app.reviewed_by,
            'projectName': app.project_name,
            'awardDate': app.award_date.isoformat() if app.award_date else None,
            'awardLevel': app.award_level,
            'awardType': app.award_type,
            'description': app.description,
            'files': processed_files,
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
            'teamRole': app.team_role,
            # 规则相关字段
            'ruleId': app.rule_id,
            'rule': rule_dict.get(app.rule_id) if app.rule_id else None
        }
        app_list.append(app_data)
    
    return jsonify(app_list), 200

# 获取单个申请
@application_bp.route('/applications/<int:id>', methods=['GET'])
def get_application(id):
    app = Application.query.get_or_404(id)
    
    # 转换文件路径格式
    processed_files = []
    if app.files:
        for file in app.files:
            # 确保processed_file是字典类型以便处理
            if isinstance(file, dict):
                processed_file = file.copy()
                # 保留原文件的size字段
                if 'size' in file:
                    processed_file['size'] = file['size']
                
                # 如果是本地绝对路径，转换为相对URL
                if 'path' in processed_file and os.path.isabs(processed_file['path']):
                        # 从绝对路径中提取文件名和子文件夹
                        filename = os.path.basename(processed_file['path'])
                        # 判断文件应该属于哪个子文件夹
                        if 'avatars' in processed_file['path']:
                            processed_file['path'] = f'/uploads/avatars/{filename}'
                        else:
                            # 默认将其他文件归类到files文件夹
                            processed_file['path'] = f'/uploads/files/{filename}'
            else:
                # 如果file不是字典类型，尝试将其转换为字典
                try:
                    processed_file = dict(file)
                except:
                    # 如果转换失败，使用默认空字典
                    processed_file = {}
            processed_files.append(processed_file)
    
    # 获取相关系、专业和规则信息
    from models import Department, Major, Rule
    
    # 安全获取系和专业名称
    department = Department.query.get(app.department_id) if app.department_id else None
    department_name = department.name if department else '未知系'
    
    major = Major.query.get(app.major_id) if app.major_id else None
    major_name = major.name if major else '未知专业'
    
    # 获取规则信息
    rule_info = None
    if app.rule_id:
        rule = Rule.query.get(app.rule_id)
        if rule:
            rule_info = {
                'id': rule.id,
                'name': rule.name,
                'score': rule.score
            }
    
    app_data = {
        'id': app.id,
        'studentId': app.student_id,
        'studentName': app.student_name,
        'departmentId': app.department_id,
        'department': department_name,
        'majorId': app.major_id,
        'major': major_name,
        'applicationType': app.application_type,
        'appliedAt': app.applied_at.isoformat() if app.applied_at else None,
        'selfScore': app.self_score,
        'status': app.status,
        'projectName': app.project_name,
        'awardDate': app.award_date.isoformat() if app.award_date else None,
        'awardLevel': app.award_level,
        'awardType': app.award_type,
        'description': app.description,
        'files': processed_files,
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
        'teamRole': app.team_role,
        # 规则相关字段
        'ruleId': app.rule_id,
        'rule': rule_info
    }
    
    return jsonify(app_data), 200

# 创建申请
@application_bp.route('/applications', methods=['POST'])
def create_application():
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
            'departmentId': 'department_id',
            'majorId': 'major_id',
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
            'ruleId': 'rule_id',
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
            # 处理数值类型字段：将空字符串转换为None
            numeric_fields = ['author_order', 'self_score', 'final_score', 'rule_id']
            if new_key in numeric_fields and value == '':
                transformed_data[new_key] = None
            else:
                transformed_data[new_key] = value
        
        # 使用转换后的数据
        data = transformed_data
        
        # 处理文件上传
        files = []
        if request.files:
            # 导入Flask应用实例以访问配置
            from app import app as flask_app
            
            # 创建上传目录（如果不存在）
            if not os.path.exists(flask_app.config['UPLOAD_FOLDER']):
                os.makedirs(flask_app.config['UPLOAD_FOLDER'])
            
            # 确保文件上传目录存在
            if not os.path.exists(flask_app.config['FILE_FOLDER']):
                os.makedirs(flask_app.config['FILE_FOLDER'])
            
            # 保存文件并记录信息
            for file in request.files.getlist('files'):
                if file and file.filename:
                    # 生成安全且保留中文的文件名
                    def generate_safe_filename(original_filename):
                        """
                        生成安全的文件名，保留中文等非ASCII字符，确保唯一性
                        """
                        # 分离文件名和扩展名
                        name, ext = os.path.splitext(original_filename)
                        # 生成唯一标识符
                        unique_id = uuid.uuid4().hex[:8]
                        # 使用时间戳和唯一ID确保文件名唯一性
                        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                        # 保留原始文件名，仅移除路径分隔符防止目录遍历
                        safe_name = name.replace('/', '').replace('\\', '')
                        # 构建最终文件名
                        return f"{safe_name}_{timestamp}_{unique_id}{ext}"
                    
                    # 使用自定义函数生成文件名
                    filename = generate_safe_filename(file.filename)
                    filepath = os.path.join(flask_app.config['FILE_FOLDER'], filename)
                    file.save(filepath)
                    
                    # 获取实际文件大小（比file.content_length更可靠）
                    actual_size = os.path.getsize(filepath)
                    
                    # 记录文件信息（存储相对URL而不是本地路径）
                    files.append({
                        'name': filename,
                        'path': f'/uploads/files/{filename}',
                        'size': actual_size,
                        'type': file.content_type
                    })
        
        from app import db
        # 处理日期字段，允许为空
        award_date_value = None
        if data.get('award_date'):
            award_date_value = datetime.fromisoformat(data['award_date']).date()
        
        new_application = Application(
            student_id=data.get('student_id'),
            student_name=data.get('student_name'),
            department_id=data.get('department_id'),
            major_id=data.get('major_id'),
            application_type=data.get('application_type'),
            applied_at=datetime.utcnow(),
            self_score=data.get('self_score'),
            status=data.get('status', 'pending'),
            project_name=data.get('project_name'),
            award_date=award_date_value,
            award_level=data.get('award_level'),
            award_type=data.get('award_type'),
            description=data.get('description'),
            files=files,
            rule_id=data.get('rule_id'),
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
        
        # 构建完整的响应数据
        app_data = {
            'id': new_application.id,
            'studentId': new_application.student_id,
            'studentName': new_application.student_name,
            'departmentId': new_application.department_id,
            'department': new_application.department.name,
            'majorId': new_application.major_id,
            'major': new_application.major.name,
            'applicationType': new_application.application_type,
            'appliedAt': new_application.applied_at.isoformat() if new_application.applied_at else None,
            'selfScore': new_application.self_score,
            'status': new_application.status,
            'projectName': new_application.project_name,
            'awardDate': new_application.award_date.isoformat() if new_application.award_date else None,
            'awardLevel': new_application.award_level,
            'awardType': new_application.award_type,
            'description': new_application.description,
            'files': new_application.files,
            'ruleId': new_application.rule_id,
            'message': '申请创建成功'
        }
        
        return jsonify(app_data), 201
    except json.JSONDecodeError as e:
        return jsonify({'error': '无效的JSON格式', 'details': str(e)}), 400
    except KeyError as e:
        return jsonify({'error': f'缺少必要字段: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': f'数据格式错误: {str(e)}'}), 400
    except Exception as e:
        error_msg = f"发生未预期的错误: {str(e)}"
        traceback_str = traceback.format_exc()
        print(error_msg)
        print("详细错误堆栈:")
        print(traceback_str)
        print("请求数据:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return jsonify({'error': '服务器内部错误', 'details': str(e), 'traceback': traceback_str}), 500

# 更新申请
@application_bp.route('/applications/<int:id>', methods=['PUT'])
def update_application(id):
    try:
        application = Application.query.get_or_404(id)
        
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
            'departmentId': 'department_id',
            'majorId': 'major_id',
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
            'ruleId': 'rule_id',
            'finalScore': 'final_score',
            'reviewComment': 'review_comment',
            'reviewedAt': 'reviewed_at',
            'reviewedBy': 'reviewed_by',
            'appliedAt': 'applied_at',
            'createdAt': 'created_at',
            'updatedAt': 'updated_at'
        }
        
        # 转换数据字段
        transformed_data = {}  # 使用新的变量名，避免与原始data冲突
        for key, value in data.items():
            # 使用映射的字段名，如果没有映射则使用原字段名
            new_key = field_mapping.get(key, key)
            # 处理数值类型字段：将空字符串转换为None
            numeric_fields = ['author_order', 'self_score', 'final_score', 'rule_id']
            if new_key in numeric_fields and value == '':
                transformed_data[new_key] = None
            else:
                transformed_data[new_key] = value
        
        # 使用转换后的数据
        data = transformed_data
        
        # 处理文件上传
        files = []
        if request.files:
            # 导入Flask应用实例以访问配置
            from app import app as flask_app
            
            # 创建上传目录（如果不存在）
            if not os.path.exists(flask_app.config['UPLOAD_FOLDER']):
                os.makedirs(flask_app.config['UPLOAD_FOLDER'])
            
            # 确保文件上传目录存在
            if not os.path.exists(flask_app.config['FILE_FOLDER']):
                os.makedirs(flask_app.config['FILE_FOLDER'])
            
            # 保存文件并记录信息
            for key, file in request.files.items():
                if file and file.filename:
                    # 生成安全且保留中文的文件名
                    def generate_safe_filename(original_filename):
                        """
                        生成安全的文件名，保留中文等非ASCII字符，确保唯一性
                        """
                        # 分离文件名和扩展名
                        name, ext = os.path.splitext(original_filename)
                        # 生成唯一标识符
                        unique_id = uuid.uuid4().hex[:8]
                        # 使用时间戳和唯一ID确保文件名唯一性
                        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                        # 保留原始文件名，仅移除路径分隔符防止目录遍历
                        safe_name = name.replace('/', '').replace('\\', '')
                        # 构建最终文件名
                        return f"{safe_name}_{timestamp}_{unique_id}{ext}"
                    
                    # 使用自定义函数生成文件名
                    filename = generate_safe_filename(file.filename)
                    filepath = os.path.join(flask_app.config['FILE_FOLDER'], filename)
                    file.save(filepath)
                    
                    # 获取实际文件大小（比file.content_length更可靠）
                    actual_size = os.path.getsize(filepath)
                    
                    # 记录文件信息（存储相对URL而不是本地路径）
                    files.append({
                        'name': filename,
                        'path': f'/uploads/files/{filename}',
                        'size': actual_size,
                        'type': file.content_type
                    })
        
        # 更新基本信息
        application.self_score = data.get('self_score', application.self_score)
        application.status = data.get('status', application.status)
        application.final_score = data.get('final_score', application.final_score)
        application.review_comment = data.get('review_comment', application.review_comment)
        application.reviewed_at = datetime.fromisoformat(data['reviewed_at']) if 'reviewed_at' in data and isinstance(data['reviewed_at'], str) else application.reviewed_at
        application.reviewed_by = data.get('reviewed_by', application.reviewed_by)
        application.project_name = data.get('project_name', application.project_name)
        application.award_date = datetime.fromisoformat(data['award_date']).date() if 'award_date' in data and isinstance(data['award_date'], str) else application.award_date
        application.award_level = data.get('award_level', application.award_level)
        application.award_type = data.get('award_type', application.award_type)
        application.description = data.get('description', application.description)
        application.student_id = data.get('student_id', application.student_id)
        application.student_name = data.get('student_name', application.student_name)
        application.department_id = data.get('department_id', application.department_id)
        application.major_id = data.get('major_id', application.major_id)
        application.application_type = data.get('application_type', application.application_type)
        application.rule_id = data.get('rule_id', application.rule_id)
        
        # 只有当有新文件上传时才更新文件列表
        if files:
            application.files = files
        elif 'files' in data:
            # 保留原有文件的size字段
            existing_files = application.files or []
            new_files = data['files'] or []
            
            # 创建一个字典映射文件路径到size
            file_size_map = {}
            for file in existing_files:
                if 'path' in file and 'size' in file:
                    file_size_map[file['path']] = file['size']
            
            # 更新新文件列表中的size字段
            updated_files = []
            for file in new_files:
                updated_file = file.copy()
                if 'path' in updated_file and updated_file['path'] in file_size_map:
                    updated_file['size'] = file_size_map[updated_file['path']]
                updated_files.append(updated_file)
            
            application.files = updated_files
        
        # 更新学术专长相关字段
        application.academic_type = data.get('academic_type', application.academic_type)
        application.research_type = data.get('research_type', application.research_type)
        application.innovation_level = data.get('innovation_level', application.innovation_level)
        application.innovation_role = data.get('innovation_role', application.innovation_role)
        application.award_grade = data.get('award_grade', application.award_grade)
        application.award_category = data.get('award_category', application.award_category)
        application.author_rank_type = data.get('author_rank_type', application.author_rank_type)
        application.author_order = data.get('author_order', application.author_order)
        
        # 更新综合表现相关字段
        application.performance_type = data.get('performance_type', application.performance_type)
        application.performance_level = data.get('performance_level', application.performance_level)
        application.performance_participation = data.get('performance_participation', application.performance_participation)
        application.team_role = data.get('team_role', application.team_role)
        
        from app import db
        db.session.commit()
        
        return jsonify({'message': '申请更新成功'}), 200
    except Exception as e:
        # 记录详细错误信息
        traceback_str = traceback.format_exc()
        print("更新申请时发生错误:")
        print(str(e))
        print("详细错误堆栈:")
        print(traceback_str)
        return jsonify({'error': '服务器内部错误', 'details': str(e), 'traceback': traceback_str}), 500

# 审核申请
@application_bp.route('/applications/<int:id>/review', methods=['POST'])
def review_application(id):
    application = Application.query.get_or_404(id)
    data = request.get_json()
    
    application.status = data['status']
    
    # 获取教师输入的分数，如果有的话优先使用
    teacher_final_score = data.get('finalScore')
    
    # 如果教师输入了分数，直接使用教师输入的分数
    if teacher_final_score is not None:
        application.final_score = teacher_final_score
    elif application.application_type == 'academic' and application.status == 'approved':
        # 教师未输入分数，自动计算最终分数（仅适用于学术专长申请）
        matched_rule = None
        
        # 1. 首先检查学生是否已经选择了规则
        if application.rule_id:
            matched_rule = Rule.query.get(application.rule_id)
        
        # 2. 如果学生没有选择规则，先检查是否有匹配的特殊规则
        if not matched_rule:
            special_rule_query = Rule.query.filter_by(
                type='academic',
                sub_type=application.academic_type,
                is_special=True,
                status='active'
            )
            
            if application.academic_type == 'research':
                special_rule_query = special_rule_query.filter_by(research_type=application.research_type)
            elif application.academic_type == 'competition':
                special_rule_query = special_rule_query.filter_by(
                    level=application.award_level,
                    grade=application.award_grade,
                    category=application.award_category
                )
            elif application.academic_type == 'innovation':
                special_rule_query = special_rule_query.filter_by(level=application.innovation_level)
            
            matched_rule = special_rule_query.first()
        
        # 3. 如果没有特殊规则，查找普通规则
        if not matched_rule:
            regular_rule_query = Rule.query.filter_by(
                type='academic',
                sub_type=application.academic_type,
                is_special=False,
                status='active'
            )
            
            if application.academic_type == 'research':
                regular_rule_query = regular_rule_query.filter_by(research_type=application.research_type)
            elif application.academic_type == 'competition':
                regular_rule_query = regular_rule_query.filter_by(
                    level=application.award_level,
                    grade=application.award_grade,
                    category=application.award_category
                )
            elif application.academic_type == 'innovation':
                regular_rule_query = regular_rule_query.filter_by(level=application.innovation_level)
            
            matched_rule = regular_rule_query.first()
        
        if matched_rule:
            # 3. 检查最大项目数量限制
            max_count_exceeded = False
            if matched_rule.max_count:
                # 统计该学生已通过的同类型项目数量（排除当前项目）
                approved_count = Application.query.filter(
                    Application.student_id == application.student_id,
                    Application.application_type == 'academic',
                    Application.academic_type == application.academic_type,
                    Application.status == 'approved',
                    Application.id != application.id  # 排除当前正在审核的项目
                ).count()
                
                if approved_count >= matched_rule.max_count:
                    max_count_exceeded = True
            
            if max_count_exceeded:
                # 超过最大项目数量限制，不给予加分
                application.final_score = 0
            else:
                # 计算基础分数
                final_score = matched_rule.score
                
                # 应用作者排序比例（如果适用）
                if application.author_rank_type == 'ranked' and application.author_order:
                    # 根据作者排序位置应用不同比例
                    if application.author_order == 1:
                        # 第一作者，使用规则中的比例
                        if matched_rule.author_rank_ratio:
                            final_score *= matched_rule.author_rank_ratio
                    else:
                        # 非第一作者，分数递减
                        # 这里可以根据实际需求调整递减规则
                        final_score *= (1 - (application.author_order - 1) * 0.1)
                        
                        # 最低不低于原分数的30%
                        final_score = max(final_score, matched_rule.score * 0.3)
                
                # 应用最大分数限制（如果有）
                if matched_rule.max_score:
                    final_score = min(final_score, matched_rule.max_score)
                
                # 设置最终分数
                application.final_score = final_score
        else:
            # 如果没有匹配的规则，设置为0分
            application.final_score = 0
    else:
        # 非学术专长申请或未通过，教师未输入分数，设置为0分
        application.final_score = 0
    
    application.review_comment = data.get('reviewComment')
    application.reviewed_at = datetime.utcnow()
    application.reviewed_by = data.get('reviewedBy')
    
    from app import db
    db.session.commit()
    
    return jsonify({'message': '申请审核成功'}), 200

# 删除申请
@application_bp.route('/applications/<int:id>', methods=['DELETE'])
def delete_application(id):
    application = Application.query.get_or_404(id)
    
    from app import db
    db.session.delete(application)
    db.session.commit()
    
    return jsonify({'message': '申请删除成功'}), 200

# 获取待审核申请
@application_bp.route('/applications/pending', methods=['GET'])
def get_pending_applications():
    # 获取查询参数
    department_id = request.args.get('departmentId')
    major_id = request.args.get('majorId')
    application_type = request.args.get('applicationType')
    student_id = request.args.get('studentId')
    student_name = request.args.get('studentName')
    
    # 构建查询
    query = Application.query.filter_by(status='pending')
    
    if department_id:
        query = query.filter_by(department_id=department_id)
    
    if major_id:
        query = query.filter_by(major_id=major_id)
    
    if application_type:
        query = query.filter_by(application_type=application_type)
    
    if student_id:
        query = query.filter(Application.student_id.like(f'%{student_id}%'))
    
    if student_name:
        query = query.filter(Application.student_name.like(f'%{student_name}%'))
    
    applications = query.all()
    app_list = []
    
    # 获取所有相关系、专业和规则信息以避免N+1查询问题
    from models import Department, Major, Rule
    
    department_ids = {app.department_id for app in applications}
    departments = Department.query.filter(Department.id.in_(department_ids)).all()
    department_dict = {d.id: d.name for d in departments}
    
    major_ids = {app.major_id for app in applications}
    majors = Major.query.filter(Major.id.in_(major_ids)).all()
    major_dict = {m.id: m.name for m in majors}
    
    # 批量获取规则信息
    rule_ids = {app.rule_id for app in applications if app.rule_id}
    rules = Rule.query.filter(Rule.id.in_(rule_ids)).all() if rule_ids else []
    rule_dict = {rule.id: {'id': rule.id, 'name': rule.name, 'score': rule.score} for rule in rules}
    
    for app in applications:
        # 转换文件路径格式
        processed_files = []
        if app.files:
            for file in app.files:
                processed_file = file.copy() if isinstance(file, dict) else file
                if isinstance(processed_file, dict) and 'path' in processed_file:
                    # 如果是本地绝对路径，转换为相对URL
                    if os.path.isabs(processed_file['path']):
                        # 从绝对路径中提取文件名和子文件夹
                        filename = os.path.basename(processed_file['path'])
                        # 判断文件应该属于哪个子文件夹
                        if 'avatars' in processed_file['path']:
                            processed_file['path'] = f'/uploads/avatars/{filename}'
                        else:
                            # 默认将其他文件归类到files文件夹
                            processed_file['path'] = f'/uploads/files/{filename}'
                processed_files.append(processed_file)
        
        app_data = {
            'id': app.id,
            'studentId': app.student_id,
            'studentName': app.student_name,
            'departmentId': app.department_id,
            'department': department_dict.get(app.department_id, '未知系'),
            'majorId': app.major_id,
            'major': major_dict.get(app.major_id, '未知专业'),
            'applicationType': app.application_type,
            'appliedAt': app.applied_at.isoformat() if app.applied_at else None,
            'selfScore': app.self_score,
            'status': app.status,
            'projectName': app.project_name,
            'awardDate': app.award_date.isoformat() if app.award_date else None,
            'awardLevel': app.award_level,
            'awardType': app.award_type,
            'description': app.description,
            'files': processed_files,
            # 规则信息
            'ruleId': app.rule_id,
            'rule': rule_dict.get(app.rule_id) if app.rule_id else None,
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

# 获取学生加分统计
@application_bp.route('/applications/statistics', methods=['GET'])
def get_application_statistics():
    # 获取查询参数
    student_id = request.args.get('studentId')
    if not student_id:
        return jsonify({'error': '缺少学生ID参数'}), 400
    
    # 查询学生的所有已通过申请
    applications = Application.query.filter_by(
        student_id=student_id,
        status='approved'
    ).all()
    
    # 按申请类型分类统计
    academic_score_calculated = sum(app.final_score for app in applications if app.final_score is not None and app.application_type == 'academic')
    comprehensive_score = sum(app.final_score for app in applications if app.final_score is not None and app.application_type == 'comprehensive')
    
    # 计算学术专长总分（对应前端的specialtyScore）
    specialty_score = academic_score_calculated
    
    # 学业综合成绩和推免综合成绩暂时设置为0（根据需求）
    academic_score = 0.0
    total_score = 0.0
    
    # 构建响应数据
    # 注意：这里使用下划线命名以匹配前端期望的格式
    statistics_data = {
        'student_id': student_id,
        'total_score': round(total_score, 2),
        'academic_score': round(academic_score, 2),
        'gpa': 0.0,  # 暂时硬编码，后续可从数据库获取
        'specialty_score': round(specialty_score, 2),
        'comprehensive_score': round(comprehensive_score, 2),
        'ranking': '-',  # 暂时硬编码，后续可从数据库获取
        'approved_count': len(applications)
    }
    
    return jsonify(statistics_data), 200

# 获取教师审核统计信息接口
@application_bp.route('/applications/teacher-statistics', methods=['GET'])
def get_teacher_statistics():
    # 获取查询参数
    teacher_id = request.args.get('teacherId')
    if not teacher_id:
        return jsonify({'error': '缺少教师ID参数'}), 400
    
    # 查询教师审核的所有申请
    reviewed_applications = Application.query.filter_by(reviewed_by=teacher_id).all()
    
    # 查询教师待审核的所有申请
    pending_applications = Application.query.filter_by(status='pending', reviewed_by=teacher_id).all()
    
    # 计算本月审核数量
    from datetime import datetime, timezone
    # 使用当前时区的时间而不是UTC时间
    current_date = datetime.now(timezone.utc).astimezone()
    current_month = current_date.month
    current_year = current_date.year
    reviewed_this_month = [
        app for app in reviewed_applications 
        if app.reviewed_at and app.reviewed_at.month == current_month and app.reviewed_at.year == current_year
    ]
    
    # 计算平均审核时间（以天为单位）
    total_review_time = 0
    valid_applications = 0
    for app in reviewed_applications:
        if app.reviewed_at and app.created_at:
            review_time = (app.reviewed_at - app.created_at).total_seconds() / (24 * 3600)  # 转换为天
            total_review_time += review_time
            valid_applications += 1
    
    avg_review_time = round(total_review_time / valid_applications, 1) if valid_applications > 0 else 0
    
    # 构建响应数据
    statistics_data = {
        'teacher_id': teacher_id,
        'pending_count': len(pending_applications),
        'reviewed_this_month': len(reviewed_this_month),
        'total_reviewed': len(reviewed_applications),
        'avg_review_time': avg_review_time
    }
    
    return jsonify(statistics_data), 200

# 健康检查接口
@application_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

# 获取学生推免成绩排名API
@application_bp.route('/applications/students-ranking', methods=['GET'])
def get_students_ranking():
    try:
        # 获取查询参数
        faculty_id = request.args.get('facultyId')
        department_id = request.args.get('departmentId')
        major_id = request.args.get('majorId')
    
        # 构建查询条件 - 使用合并后的Student模型
        query = Student.query
    
        # 应用筛选条件 - 添加类型检查和转换
        if faculty_id and faculty_id != 'all':
            try:
                faculty_id = int(faculty_id)
                query = query.filter_by(faculty_id=faculty_id)
            except ValueError:
                # 如果参数不是有效整数，忽略该筛选条件
                pass

        if department_id and department_id != 'all':
            try:
                department_id = int(department_id)
                query = query.filter_by(department_id=department_id)
            except ValueError:
                # 如果参数不是有效整数，忽略该筛选条件
                pass

        if major_id and major_id != 'all':
            try:
                major_id = int(major_id)
                query = query.filter_by(major_id=major_id)
            except ValueError:
                # 如果参数不是有效整数，忽略该筛选条件
                pass
    
        # 获取所有符合条件的学生数据
        students = query.all()
    
        # 按学生ID分组统计
        student_stats = {}
    
        # 从Student模型获取基本数据
        for student in students:
            student_id = student.id
            student_stats[student_id] = {
                'student_id': student.student_id,
                'student_name': student.student_name,
                'departmentId': student.department_id,
                'department': student.department.name if student.department else '未知系别',
                'majorId': student.major_id,
                'major': student.major.name if student.major else '未知专业',
                'facultyId': student.faculty_id,  # 添加学院ID
                'faculty': student.faculty.name if student.faculty else '未知学院',  # 添加学院名称，处理空值情况
                'gender': student.gender,
                'cet4_score': student.cet4_score,
                'cet6_score': student.cet6_score,
                'gpa': student.gpa,
                'academic_score': student.academic_score,
                'academic_weighted': student.academic_weighted,
                'academic_specialty_total': student.academic_specialty_total,
                'comprehensive_performance_total': student.comprehensive_performance_total,
                'total_score': student.total_score,
                'major_ranking': student.major_ranking,
                'major_total_students': student.total_students,
                'specialty_score': student.academic_specialty_total or 0.0,
                'comprehensive_score': student.comprehensive_performance_total or 0.0,
                'total_comprehensive_score': student.total_score or 0.0,
                'final_comprehensive_score': student.comprehensive_score or 0.0,
                'sequence': 0
            }
    
        # 获取学术专长详情 - 使用PerformanceDetail模型，type='academic'
        for student_id in student_stats:
            # 使用学生学号(字符串)而不是学生ID(整数)进行查询
            student_number = student_stats[student_id]['student_id']
            # 确保student_number是字符串类型
            student_number_str = str(student_number)
            academic_details = PerformanceDetail.query.filter_by(student_id=student_number_str, type='academic').all()
            academic_items = []
            for detail in academic_details:
                academic_items.append({
                    'project_name': detail.project_name,
                    'award_time': detail.award_date.strftime('%Y-%m-%d') if detail.award_date else '',
                    'award_level': detail.award_level,
                    'individual_collective': detail.award_type,
                    'author_order': detail.author_order,
                    'self_eval_score': detail.self_score,
                    'score_basis': detail.score_basis,
                    'college_approved_score': detail.approved_score,
                    'total_score': detail.approved_score or 0.0
                })
            student_stats[student_id]['academic_items'] = academic_items
    
        # 获取综合表现详情 - 使用PerformanceDetail模型，type='comprehensive'
        for student_id in student_stats:
            # 使用学生学号(字符串)而不是学生ID(整数)进行查询
            student_number = student_stats[student_id]['student_id']
            # 确保student_number是字符串类型
            student_number_str = str(student_number)
            comprehensive_details = PerformanceDetail.query.filter_by(student_id=student_number_str, type='comprehensive').all()
            comprehensive_items = []
            for detail in comprehensive_details:
                comprehensive_items.append({
                    'project_name': detail.project_name,
                    'award_time': detail.award_date.strftime('%Y-%m-%d') if detail.award_date else '',
                    'award_level': detail.award_level,
                    'individual_collective': detail.award_type,
                    'author_order': detail.author_order,
                    'self_eval_score': detail.self_score,
                    'score_basis': detail.score_basis,
                    'college_approved_score': detail.approved_score,
                    'total_score': detail.approved_score or 0.0
                })
            student_stats[student_id]['comprehensive_items'] = comprehensive_items
    
        # 如果Student模型没有数据，回退到Application模型并生成模拟数据
        if not students:
            # 构建查询条件
            app_query = Application.query.filter_by(status='approved')
            
            # 应用筛选条件
            if department_id and department_id != 'all':
                try:
                    department_id = int(department_id)
                    app_query = app_query.filter_by(department_id=department_id)
                except ValueError:
                    # 如果参数不是有效整数，忽略该筛选条件
                    pass
            
            if major_id and major_id != 'all':
                try:
                    major_id = int(major_id)
                    app_query = app_query.filter_by(major_id=major_id)
                except ValueError:
                    # 如果参数不是有效整数，忽略该筛选条件
                    pass
            
            # 获取所有符合条件的申请
            applications = app_query.all()
            
            # 按学生ID分组统计
            for app in applications:
                student_id = app.student_id
                if student_id not in student_stats:
                    student_stats[student_id] = {
                        'student_id': app.student_id,
                        'student_name': app.student_name,
                        'departmentId': app.department_id,
                        'department': app.department.name,
                        'majorId': app.major_id,
                        'major': app.major.name,
                        'specialty_score': 0.0,
                        'comprehensive_score': 0.0,
                        'total_score': 0.0,
                        'academic_weighted': 0.0,  # 学业综合成绩（80%）
                        'total_comprehensive_score': 0.0,  # 考核综合成绩总分
                        'cet4_score': None,  # CET4成绩
                        'cet6_score': None,  # CET6成绩
                        'gpa': None,  # 推免绩点
                        'academic_score': None,  # 换算后的学业成绩
                        'major_ranking': None,  # 专业成绩排名
                        'major_total_students': None  # 排名人数
                    }
                
                # 累加学术专长分数
                if app.application_type == 'academic' and app.final_score is not None:
                    student_stats[student_id]['specialty_score'] += app.final_score
                
                # 累加综合表现分数
                if app.application_type == 'comprehensive' and app.final_score is not None:
                    student_stats[student_id]['comprehensive_score'] += app.final_score
            
            # 为了演示，添加一些模拟数据
            for student_id in student_stats:
                stats = student_stats[student_id]
                # A-H: 学生基本信息
                stats['sequence'] = int(student_id[-2:]) % 50 + 1  # A: 序号（每专业独立）
                stats['gender'] = '男' if int(student_id[-1:]) % 2 == 0 else '女'  # F: 性别
                stats['cet4_score'] = 500 + int(student_id[-2:]) % 100  # G: CET4成绩
                # H: CET6成绩（部分为空或标注"通过学术专长答辩"）
                if int(student_id[-2:]) % 3 == 0:
                    stats['cet6_score'] = '通过学术专长答辩'
                else:
                    stats['cet6_score'] = 450 + int(student_id[-2:]) % 100
                
                # I-J: 学业综合成绩（占总分80%）
                stats['gpa'] = 3.5 + (int(student_id[-2:]) % 10) * 0.1  # I: 推免绩点(满分4分)
                stats['academic_score'] = 85 + (int(student_id[-2:]) % 15)  # J: 换算后的成绩(满分100分)
                stats['academic_weighted'] = stats['academic_score'] * 0.8  # 学业综合成绩（80%）
                
                # K-S: 学术专长成绩（占总分12%）
                # 学术专长项目数组
                stats['academic_items'] = [{
                    'project_name': '全国大学生计算机设计大赛',  # K: 项目
                    'award_time': '2023-12-15',  # L: 获奖时间
                    'award_level': '国家级',  # M: 奖项级别
                    'individual_collective': '个人',  # N: 个人或集体奖项
                    'author_order': '第一作者',  # O: 集体奖项中第几作者/参赛者
                    'self_eval_score': 12.0,  # P: 自评加分
                    'score_basis': '国家级A类一等奖',  # Q: 加分依据
                    'college_approved_score': 12.0,  # R: 学院核定加分
                    'total_score': stats['specialty_score']  # S: 学院核定总分
                }]
                
                # T-AB: 综合表现加分（占总分8%）
                # 综合表现项目数组
                stats['comprehensive_items'] = [{
                    'project_name': '优秀学生干部',  # T: 项目
                    'award_time': '2024-03-10',  # U: 获奖时间
                    'award_level': '校级',  # V: 奖项级别
                    'individual_collective': '个人',  # W: 个人或集体奖项
                    'author_order': '',  # X: 集体奖项中第几作者/参赛者
                    'self_eval_score': 8.0,  # Y: 自评加分
                    'score_basis': '连续两年担任班长',  # Z: 加分依据
                    'college_approved_score': 8.0,  # AA: 学院核定加分
                    'total_score': stats['comprehensive_score']  # AB: 学院核定总分
                }]
                
                # AC-AF: 总分与排名
                stats['total_comprehensive_score'] = stats['specialty_score'] + stats['comprehensive_score']  # AC: 考核综合成绩总分
                stats['final_score'] = stats['academic_weighted'] + stats['total_comprehensive_score']  # AD: 综合成绩
                # 处理专业排名和排名人数，确保student_id的最后两位是数字
                try:
                    stats['major_ranking'] = int(student_id[-2:]) % 20 + 1  # AE: 专业成绩排名
                except ValueError:
                    stats['major_ranking'] = 1
                try:
                    stats['major_total_students'] = 100 + int(student_id[-1:]) * 20  # AF: 排名人数
                except ValueError:
                    stats['major_total_students'] = 100
                stats['final_comprehensive_score'] = stats['final_score']
    
        # 计算总分并转换为列表
        students_list = []
        for student_id, stats in student_stats.items():
            students_list.append(stats)
    
        # 按总分降序排序
        students_list.sort(key=lambda x: x['final_comprehensive_score'], reverse=True)
    
        # 为每个学生分配序号
        for idx, student in enumerate(students_list):
            student['sequence'] = idx + 1
    
        # 构建响应数据
        response = {
            'total_students': len(students_list),
            'students': students_list
        }
    
        return jsonify(response), 200
    except Exception as e:
        # 记录详细错误信息
        current_app.logger.error(f"Error in get_students_ranking: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': '服务器内部错误', 'details': str(e)}), 500