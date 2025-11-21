# -*- coding: utf-8 -*-
"""
申请管理CRUD操作模块

该模块包含申请的创建、读取、更新、删除等基本操作
"""

from flask import request, jsonify, current_app
from models import Application, Student, Rule, Department, Major, SystemSettings
from datetime import datetime
import pytz
import json
import os
import traceback
import uuid
from extensions import db
from .application_utils import update_student_statistics
from . import application_bp


@application_bp.route("/applications", methods=["GET"])
def get_applications():
    """
    获取所有申请
    支持多种筛选条件
    """
    # 获取查询参数
    student_id = request.args.get("studentId")
    student_name = request.args.get("studentName")
    status = request.args.get("status")
    application_type = request.args.get("applicationType")
    reviewed_by = request.args.get("reviewedBy")
    reviewed_start_date = request.args.get("reviewedStartDate")
    reviewed_end_date = request.args.get("reviewedEndDate")
    faculty_id = request.args.get("facultyId")
    department_id = request.args.get("departmentId")
    major_id = request.args.get("majorId")
    department_name = request.args.get("department")
    major_name = request.args.get("major")

    # 构建查询
    query = Application.query

    # 按学院筛选
    if faculty_id:
        query = query.filter_by(faculty_id=faculty_id)

    if student_id:
        query = query.filter_by(student_id=student_id)

    if student_name:
        query = query.filter(Application.student_name.like(f"%{student_name}%"))

    if status:
        query = query.filter_by(status=status)

    if application_type:
        query = query.filter_by(application_type=application_type)

    if reviewed_by:
        query = query.filter(Application.reviewed_by.like(f"%{reviewed_by}%"))

    if department_id:
        query = query.filter_by(department_id=department_id)
    elif department_name:
        # 按系名称筛选（支持部分匹配）
        departments = Department.query.filter(
            Department.name.like(f"%{department_name}%")
        ).all()
        if departments:
            department_ids = [dept.id for dept in departments]
            query = query.filter(Application.department_id.in_(department_ids))

    if major_id:
        query = query.filter_by(major_id=major_id)
    elif major_name:
        # 按专业名称筛选（支持部分匹配）
        majors = Major.query.filter(Major.name.like(f"%{major_name}%")).all()
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
            end_date = end_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            query = query.filter(Application.reviewed_at <= end_date)
        except (ValueError, TypeError):
            # 如果日期格式无效，忽略该筛选条件
            pass

    applications = query.all()
    app_list = []

    # 获取所有相关系、专业和规则信息以避免N+1查询问题
    department_ids = {app.department_id for app in applications}
    departments = Department.query.filter(Department.id.in_(department_ids)).all()
    department_dict = {d.id: d.name for d in departments}

    major_ids = {app.major_id for app in applications}
    majors = Major.query.filter(Major.id.in_(major_ids)).all()
    major_dict = {m.id: m.name for m in majors}

    # 获取所有规则信息
    rule_ids = {app.rule_id for app in applications if app.rule_id}
    rules = Rule.query.filter(Rule.id.in_(rule_ids)).all()
    rule_dict = {
        r.id: {
            "id": r.id,
            "name": r.name,
            "score": r.score,
            "description": r.description,
        }
        for r in rules
    }

    for app in applications:
        # 转换文件路径格式
        processed_files = []
        if app.files:
            for file in app.files:
                # 确保processed_file是字典类型以便处理
                if isinstance(file, dict):
                    processed_file = file.copy()
                    # 保留原文件的size字段
                    if "size" in file:
                        processed_file["size"] = file["size"]

                    # 如果是本地绝对路径，转换为相对URL
                    if "path" in processed_file and os.path.isabs(
                        processed_file["path"]
                    ):
                        # 从绝对路径中提取文件名和子文件夹
                        filename = os.path.basename(processed_file["path"])
                        # 判断文件应该属于哪个子文件夹
                        if "avatars" in processed_file["path"]:
                            processed_file["path"] = f"/uploads/avatars/{filename}"
                        else:
                            # 默认将其他文件归类到files文件夹
                            processed_file["path"] = f"/uploads/files/{filename}"
                else:
                    # 如果file不是字典类型，尝试将其转换为字典
                    try:
                        processed_file = dict(file)
                    except:
                        # 如果转换失败，使用默认空字典
                        processed_file = {}
                processed_files.append(processed_file)

        app_data = {
            "id": app.id,
            "studentId": app.student_id,
            "studentName": app.student_name,
            "facultyId": app.faculty_id,
            "departmentId": app.department_id,
            "department": department_dict.get(app.department_id, "未知系"),
            "majorId": app.major_id,
            "major": major_dict.get(app.major_id, "未知专业"),
            "applicationType": app.application_type,
            "appliedAt": app.applied_at.isoformat() if app.applied_at else None,
            "selfScore": app.self_score,
            "finalScore": app.final_score,
            "status": app.status,
            "reviewComment": app.review_comment,
            "reviewedAt": app.reviewed_at.isoformat() if app.reviewed_at else None,
            "reviewedBy": app.reviewed_by,
            "projectName": app.project_name,
            "awardDate": app.award_date.isoformat() if app.award_date else None,
            "awardLevel": app.award_level,
            "awardType": app.award_type,
            "description": app.description,
            "files": processed_files,
            # 学术专长相关字段
            "academicType": app.academic_type,
            "researchType": app.research_type,
            "innovationLevel": app.innovation_level,
            "innovationRole": app.innovation_role,
            "awardGrade": app.award_grade,
            "awardCategory": app.award_category,
            "authorRankType": app.author_rank_type,
            "authorOrder": app.author_order,
            # 综合表现相关字段
            "performanceType": app.performance_type,
            "performanceLevel": app.performance_level,
            "performanceParticipation": app.performance_participation,
            "teamRole": app.team_role,
            # 规则相关字段
            "ruleId": app.rule_id,
            "rule": rule_dict.get(app.rule_id) if app.rule_id else None,
        }
        app_list.append(app_data)

    return jsonify(app_list), 200


@application_bp.route("/applications/<int:id>", methods=["GET"])
def get_application(id):
    """
    获取单个申请详情
    """
    app = Application.query.get_or_404(id)

    # 转换文件路径格式
    processed_files = []
    if app.files:
        for file in app.files:
            # 确保processed_file是字典类型以便处理
            if isinstance(file, dict):
                processed_file = file.copy()
                # 保留原文件的size字段
                if "size" in file:
                    processed_file["size"] = file["size"]

                # 如果是本地绝对路径，转换为相对URL
                if "path" in processed_file and os.path.isabs(processed_file["path"]):
                    # 从绝对路径中提取文件名和子文件夹
                    filename = os.path.basename(processed_file["path"])
                    # 判断文件应该属于哪个子文件夹
                    if "avatars" in processed_file["path"]:
                        processed_file["path"] = f"/uploads/avatars/{filename}"
                    else:
                        # 默认将其他文件归类到files文件夹
                        processed_file["path"] = f"/uploads/files/{filename}"
            else:
                # 如果file不是字典类型，尝试将其转换为字典
                try:
                    processed_file = dict(file)
                except:
                    # 如果转换失败，使用默认空字典
                    processed_file = {}
            processed_files.append(processed_file)

    # 安全获取系和专业名称
    department = Department.query.get(app.department_id) if app.department_id else None
    department_name = department.name if department else "未知系"

    major = Major.query.get(app.major_id) if app.major_id else None
    major_name = major.name if major else "未知专业"

    # 获取规则信息
    rule_info = None
    if app.rule_id:
        rule = Rule.query.get(app.rule_id)
        if rule:
            rule_info = {
                "id": rule.id,
                "name": rule.name,
                "score": rule.score,
                "description": rule.description,
            }

    app_data = {
        "id": app.id,
        "studentId": app.student_id,
        "studentName": app.student_name,
        "departmentId": app.department_id,
        "department": department_name,
        "majorId": app.major_id,
        "major": major_name,
        "applicationType": app.application_type,
        "appliedAt": app.applied_at.isoformat() if app.applied_at else None,
        "selfScore": app.self_score,
        "status": app.status,
        "projectName": app.project_name,
        "awardDate": app.award_date.isoformat() if app.award_date else None,
        "awardLevel": app.award_level,
        "awardType": app.award_type,
        "description": app.description,
        "files": processed_files,
        "finalScore": app.final_score,
        "reviewComment": app.review_comment,
        "reviewedAt": app.reviewed_at.isoformat() if app.reviewed_at else None,
        "reviewedBy": app.reviewed_by,
        # 学术专长相关字段
        "academicType": app.academic_type,
        "researchType": app.research_type,
        "innovationLevel": app.innovation_level,
        "innovationRole": app.innovation_role,
        "awardGrade": app.award_grade,
        "awardCategory": app.award_category,
        "authorRankType": app.author_rank_type,
        "authorOrder": app.author_order,
        # 综合表现相关字段
        "performanceType": app.performance_type,
        "performanceLevel": app.performance_level,
        "performanceParticipation": app.performance_participation,
        "teamRole": app.team_role,
        # 规则相关字段
        "ruleId": app.rule_id,
        "rule": rule_info,
    }

    return jsonify(app_data), 200


@application_bp.route("/applications", methods=["POST"])
def create_application():
    """
    创建新申请
    """
    try:
        # 解析申请数据
        if "application" in request.form:
            data = json.loads(request.form["application"])
        else:
            data = request.get_json()

        # 字段名转换：将前端的驼峰式命名转换为后端的下划线命名
        field_mapping = {
            "studentId": "student_id",
            "studentName": "student_name",
            "name": "student_name",  # 兼容前端可能使用的name字段
            "facultyId": "faculty_id",
            "departmentId": "department_id",
            "majorId": "major_id",
            "applicationType": "application_type",
            "selfScore": "self_score",
            "projectName": "project_name",
            "awardDate": "award_date",
            "awardLevel": "award_level",
            "awardType": "award_type",
            "academicType": "academic_type",
            "researchType": "research_type",
            "innovationLevel": "innovation_level",
            "innovationRole": "innovation_role",
            "awardGrade": "award_grade",
            "awardCategory": "award_category",
            "authorRankType": "author_rank_type",
            "authorOrder": "author_order",
            "performanceType": "performance_type",
            "performanceLevel": "performance_level",
            "performanceParticipation": "performance_participation",
            "teamRole": "team_role",
            "ruleId": "rule_id",
            "finalScore": "final_score",
            "reviewComment": "review_comment",
            "reviewedAt": "reviewed_at",
            "reviewedBy": "reviewed_by",
            "appliedAt": "applied_at",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        }

        # 转换数据字段
        transformed_data = {}
        for key, value in data.items():
            # 使用映射的字段名，如果没有映射则使用原字段名
            new_key = field_mapping.get(key, key)
            # 处理数值类型字段：将空字符串转换为None
            numeric_fields = ["author_order", "self_score", "final_score", "rule_id"]
            if new_key in numeric_fields and value == "":
                transformed_data[new_key] = None
            else:
                transformed_data[new_key] = value

        # 使用转换后的数据
        data = transformed_data

        # 处理文件上传
        files = []
        if request.files:
            # 获取系统设置中的文件大小限制和允许的文件类型
            settings = SystemSettings.query.first()
            if not settings:
                return jsonify({"error": "系统设置未配置"}), 500

            single_file_size_limit = (
                settings.single_file_size_limit * 1024 * 1024
            )  # 转换为字节
            total_file_size_limit = (
                settings.total_file_size_limit * 1024 * 1024
            )  # 转换为字节
            allowed_file_types = settings.allowed_file_types

            # 创建上传目录（如果不存在）
            if not os.path.exists(current_app.config["UPLOAD_FOLDER"]):
                os.makedirs(current_app.config["UPLOAD_FOLDER"])

            # 确保文件上传目录存在
            if not os.path.exists(current_app.config["FILE_FOLDER"]):
                os.makedirs(current_app.config["FILE_FOLDER"])

            total_upload_size = 0
            # 保存文件并记录信息
            for file in request.files.getlist("files"):
                if file and file.filename:
                    # 检查文件类型
                    file_ext = os.path.splitext(file.filename)[1].lower()
                    if file_ext not in allowed_file_types:
                        return (
                            jsonify(
                                {
                                    "error": f"文件类型不允许: {file.filename}，仅支持{allowed_file_types}"
                                }
                            ),
                            400,
                        )

                    # 检查单个文件大小
                    file.seek(0, 2)  # 移动到文件末尾
                    file_size = file.tell()  # 获取文件大小
                    file.seek(0)  # 重置文件指针到开头

                    if file_size > single_file_size_limit:
                        return (
                            jsonify(
                                {
                                    "error": f"单个文件大小超过限制: {file.filename}，最大允许{settings.single_file_size_limit}MB"
                                }
                            ),
                            400,
                        )

                    # 检查总文件大小
                    total_upload_size += file_size
                    if total_upload_size > total_file_size_limit:
                        return (
                            jsonify(
                                {
                                    "error": f"总文件大小超过限制，最大允许{settings.total_file_size_limit}MB"
                                }
                            ),
                            400,
                        )

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
                        timestamp = datetime.now(
                            pytz.timezone("Asia/Shanghai")
                        ).strftime("%Y%m%d%H%M%S")
                        # 保留原始文件名，仅移除路径分隔符防止目录遍历
                        safe_name = name.replace("/", "_").replace("\\", "_")
                        return f"{safe_name}_{timestamp}_{unique_id}{ext}"

                    # 生成安全文件名
                    filename = generate_safe_filename(file.filename)
                    # 文件保存路径
                    file_path = os.path.join(
                        current_app.config["FILE_FOLDER"], filename
                    )

                    # 保存文件
                    file.save(file_path)

                    # 记录文件信息
                    files.append(
                        {
                            "name": filename,
                            "path": file_path,
                            "size": file_size,
                        }
                    )

        # 创建申请对象
        new_application = Application(
            student_id=data.get("student_id"),
            student_name=data.get("student_name"),
            faculty_id=data.get("faculty_id"),
            department_id=data.get("department_id"),
            major_id=data.get("major_id"),
            application_type=data.get("application_type"),
            self_score=data.get("self_score"),
            status="pending",  # 默认为待审核状态
            project_name=data.get("project_name"),
            award_date=(
                datetime.fromisoformat(data["award_date"])
                if data.get("award_date")
                else None
            ),
            award_level=data.get("award_level"),
            award_type=data.get("award_type"),
            description=data.get("description"),
            files=files,
            academic_type=data.get("academic_type"),
            research_type=data.get("research_type"),
            innovation_level=data.get("innovation_level"),
            innovation_role=data.get("innovation_role"),
            award_grade=data.get("award_grade"),
            award_category=data.get("award_category"),
            author_rank_type=data.get("author_rank_type"),
            author_order=data.get("author_order"),
            performance_type=data.get("performance_type"),
            performance_level=data.get("performance_level"),
            performance_participation=data.get("performance_participation"),
            team_role=data.get("team_role"),
            rule_id=data.get("rule_id"),
            applied_at=datetime.now(pytz.timezone("Asia/Shanghai")),
            created_at=datetime.now(pytz.timezone("Asia/Shanghai")),
            updated_at=datetime.now(pytz.timezone("Asia/Shanghai")),
        )

        # 保存到数据库
        db.session.add(new_application)
        db.session.commit()

        # 返回创建的申请信息
        return jsonify({"id": new_application.id, "message": "申请创建成功"}), 201

    except Exception as e:
        # 记录详细错误信息
        db.session.rollback()
        return (
            jsonify(
                {
                    "error": f"创建申请失败: {str(e)}",
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )


@application_bp.route("/applications/<int:id>", methods=["PUT"])
def update_application(id):
    """
    更新申请信息
    """
    try:
        # 获取申请对象
        application = Application.query.get_or_404(id)

        # 解析请求数据
        if "application" in request.form:
            data = json.loads(request.form["application"])
        else:
            data = request.get_json()

        # 字段名转换：将前端的驼峰式命名转换为后端的下划线命名
        field_mapping = {
            "studentId": "student_id",
            "studentName": "student_name",
            "facultyId": "faculty_id",
            "departmentId": "department_id",
            "majorId": "major_id",
            "applicationType": "application_type",
            "selfScore": "self_score",
            "projectName": "project_name",
            "awardDate": "award_date",
            "awardLevel": "award_level",
            "awardType": "award_type",
            "description": "description",
            "academicType": "academic_type",
            "researchType": "research_type",
            "innovationLevel": "innovation_level",
            "innovationRole": "innovation_role",
            "awardGrade": "award_grade",
            "awardCategory": "award_category",
            "authorRankType": "author_rank_type",
            "authorOrder": "author_order",
            "performanceType": "performance_type",
            "performanceLevel": "performance_level",
            "performanceParticipation": "performance_participation",
            "teamRole": "team_role",
            "ruleId": "rule_id",
        }

        # 转换数据字段
        transformed_data = {}
        for key, value in data.items():
            # 使用映射的字段名，如果没有映射则使用原字段名
            new_key = field_mapping.get(key, key)
            # 处理数值类型字段：将空字符串转换为None
            numeric_fields = ["author_order", "self_score", "rule_id"]
            if new_key in numeric_fields and value == "":
                transformed_data[new_key] = None
            else:
                transformed_data[new_key] = value

        # 使用转换后的数据
        data = transformed_data

        # 更新申请信息
        if "student_id" in data:
            application.student_id = data["student_id"]
        if "student_name" in data:
            application.student_name = data["student_name"]
        if "faculty_id" in data:
            application.faculty_id = data["faculty_id"]
        if "department_id" in data:
            application.department_id = data["department_id"]
        if "major_id" in data:
            application.major_id = data["major_id"]
        if "application_type" in data:
            application.application_type = data["application_type"]
        if "self_score" in data:
            application.self_score = data["self_score"]
        if "project_name" in data:
            application.project_name = data["project_name"]
        if "award_date" in data:
            application.award_date = (
                datetime.fromisoformat(data["award_date"])
                if data["award_date"]
                else None
            )
        if "award_level" in data:
            application.award_level = data["award_level"]
        if "award_type" in data:
            application.award_type = data["award_type"]
        if "description" in data:
            application.description = data["description"]
        if "academic_type" in data:
            application.academic_type = data["academic_type"]
        if "research_type" in data:
            application.research_type = data["research_type"]
        if "innovation_level" in data:
            application.innovation_level = data["innovation_level"]
        if "innovation_role" in data:
            application.innovation_role = data["innovation_role"]
        if "award_grade" in data:
            application.award_grade = data["award_grade"]
        if "award_category" in data:
            application.award_category = data["award_category"]
        if "author_rank_type" in data:
            application.author_rank_type = data["author_rank_type"]
        if "author_order" in data:
            application.author_order = data["author_order"]
        if "performance_type" in data:
            application.performance_type = data["performance_type"]
        if "performance_level" in data:
            application.performance_level = data["performance_level"]
        if "performance_participation" in data:
            application.performance_participation = data["performance_participation"]
        if "team_role" in data:
            application.team_role = data["team_role"]
        if "rule_id" in data:
            application.rule_id = data["rule_id"]

        # 处理文件上传
        if request.files:
            # 获取系统设置中的文件大小限制和允许的文件类型
            settings = SystemSettings.query.first()
            if not settings:
                return jsonify({"error": "系统设置未配置"}), 500

            single_file_size_limit = (
                settings.single_file_size_limit * 1024 * 1024
            )  # 转换为字节
            total_file_size_limit = (
                settings.total_file_size_limit * 1024 * 1024
            )  # 转换为字节
            allowed_file_types = settings.allowed_file_types

            # 确保文件上传目录存在
            if not os.path.exists(current_app.config["FILE_FOLDER"]):
                os.makedirs(current_app.config["FILE_FOLDER"])

            # 处理新上传的文件
            new_files = []
            if application.files:
                new_files = application.files.copy()

            total_upload_size = sum(file.get("size", 0) for file in new_files)

            # 保存新文件并记录信息
            for file in request.files.getlist("files"):
                if file and file.filename:
                    # 检查文件类型
                    file_ext = os.path.splitext(file.filename)[1].lower()
                    if file_ext not in allowed_file_types:
                        return (
                            jsonify(
                                {
                                    "error": f"文件类型不允许: {file.filename}，仅支持{allowed_file_types}"
                                }
                            ),
                            400,
                        )

                    # 检查单个文件大小
                    file.seek(0, 2)  # 移动到文件末尾
                    file_size = file.tell()  # 获取文件大小
                    file.seek(0)  # 重置文件指针到开头

                    if file_size > single_file_size_limit:
                        return (
                            jsonify(
                                {
                                    "error": f"单个文件大小超过限制: {file.filename}，最大允许{settings.single_file_size_limit}MB"
                                }
                            ),
                            400,
                        )

                    # 检查总文件大小
                    total_upload_size += file_size
                    if total_upload_size > total_file_size_limit:
                        return (
                            jsonify(
                                {
                                    "error": f"总文件大小超过限制，最大允许{settings.total_file_size_limit}MB"
                                }
                            ),
                            400,
                        )

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
                        timestamp = datetime.now(
                            pytz.timezone("Asia/Shanghai")
                        ).strftime("%Y%m%d%H%M%S")
                        # 保留原始文件名，仅移除路径分隔符防止目录遍历
                        safe_name = name.replace("/", "_").replace("\\", "_")
                        return f"{safe_name}_{timestamp}_{unique_id}{ext}"

                    # 生成安全文件名
                    filename = generate_safe_filename(file.filename)
                    # 文件保存路径
                    file_path = os.path.join(
                        current_app.config["FILE_FOLDER"], filename
                    )

                    # 保存文件
                    file.save(file_path)

                    # 记录文件信息
                    new_files.append(
                        {
                            "name": filename,
                            "path": file_path,
                            "size": file_size,
                        }
                    )

            # 更新文件列表
            application.files = new_files

        # 更新修改时间
        application.updated_at = datetime.now(pytz.timezone("Asia/Shanghai"))

        # 保存到数据库
        db.session.commit()

        return jsonify({"id": application.id, "message": "申请更新成功"}), 200

    except Exception as e:
        # 记录详细错误信息
        db.session.rollback()
        return (
            jsonify(
                {
                    "error": f"更新申请失败: {str(e)}",
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )


@application_bp.route("/applications/<int:id>", methods=["DELETE"])
def delete_application(id):
    """
    删除申请
    """
    try:
        # 获取申请对象
        application = Application.query.get_or_404(id)

        # 删除相关文件
        if application.files:
            for file in application.files:
                if "path" in file and os.path.exists(file["path"]):
                    try:
                        os.remove(file["path"])
                    except Exception as e:
                        # 记录文件删除失败但继续删除申请
                        print(f"删除文件失败: {file['path']}, 错误: {str(e)}")

        # 从数据库中删除
        db.session.delete(application)
        db.session.commit()

        return jsonify({"message": "申请删除成功"}), 200

    except Exception as e:
        # 记录详细错误信息
        db.session.rollback()
        return (
            jsonify(
                {
                    "error": f"删除申请失败: {str(e)}",
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )
