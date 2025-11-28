# -*- coding: utf-8 -*-
"""
组织信息管理蓝图

该文件负责处理学院、系、专业等组织信息的通用查询API，
提供可被其他蓝图共享的组织信息查询功能。
"""

from flask import Blueprint, request, jsonify
from models import Faculty, Department, Major

# 创建蓝图实例
organization_bp = Blueprint("organization", __name__, url_prefix="/api/organization")


# 通用辅助函数：将模型对象转换为字典
def model_to_dict(model, detailed=False, extra_fields=None):
    """
    将模型对象转换为字典

    Args:
        model: 数据库模型对象
        detailed: 是否返回详细信息
        extra_fields: 额外需要添加的字段字典

    Returns:
        包含模型信息的字典
    """
    # 基本信息
    result = {"id": model.id, "name": model.name}

    # 详细信息（如果需要）
    if (
        detailed
        and hasattr(model, "description")
        and hasattr(model, "created_at")
        and hasattr(model, "updated_at")
    ):
        result.update(
            {
                "description": model.description,
                "created_at": model.created_at.isoformat(),
                "updated_at": model.updated_at.isoformat(),
            }
        )

    # 添加额外字段
    if extra_fields:
        result.update(extra_fields)

    return result


# 通用函数：获取学院列表
def get_all_faculties(detailed=False):
    """
    获取所有学院信息

    Args:
        detailed: 是否返回详细信息（包含描述、创建时间等）

    Returns:
        学院信息列表
    """
    faculties = Faculty.query.all()
    return [model_to_dict(faculty, detailed) for faculty in faculties]


# 通用函数：根据学院ID获取系列表
def get_departments_by_faculty_id(faculty_id, detailed=False):
    """
    根据学院ID获取系列表

    Args:
        faculty_id: 学院ID
        detailed: 是否返回详细信息

    Returns:
        系列表
    """
    departments = Department.query.filter_by(faculty_id=faculty_id).all()

    result = []
    for dept in departments:
        extra_fields = {"faculty_id": dept.faculty_id} if detailed else None
        result.append(model_to_dict(dept, detailed, extra_fields))

    return result


# 通用函数：获取所有系列表
def get_all_departments(detailed=False):
    """
    获取所有系信息列表

    Args:
        detailed: 是否返回详细信息

    Returns:
        系列表
    """
    departments = Department.query.all()

    if not detailed:
        return [model_to_dict(dept, detailed) for dept in departments]

    # 预加载所有相关的学院信息以避免N+1查询
    faculty_ids = {dept.faculty_id for dept in departments}
    faculties = {
        f.id: f for f in Faculty.query.filter(Faculty.id.in_(faculty_ids)).all()
    }

    result = []
    for dept in departments:
        faculty = faculties.get(dept.faculty_id)
        extra_fields = {
            "faculty_id": dept.faculty_id,
            "faculty_name": faculty.name if faculty else "未知学院",
        }
        result.append(model_to_dict(dept, detailed, extra_fields))

    return result


# 通用函数：获取所有专业列表
def get_all_majors(detailed=False):
    """
    获取所有专业列表

    Args:
        detailed: 是否返回详细信息

    Returns:
        专业列表
    """
    majors = Major.query.all()

    if not detailed:
        return [model_to_dict(major, detailed) for major in majors]

    # 预加载所有相关的系和学院信息以避免N+1查询
    major_ids = [major.id for major in majors]
    department_ids = {major.department_id for major in majors}

    departments = {
        d.id: d
        for d in Department.query.filter(Department.id.in_(department_ids)).all()
    }
    faculty_ids = {d.faculty_id for d in departments.values()}
    faculties = {
        f.id: f for f in Faculty.query.filter(Faculty.id.in_(faculty_ids)).all()
    }

    result = []
    for major in majors:
        department = departments.get(major.department_id)
        faculty = faculties.get(department.faculty_id) if department else None

        extra_fields = {
            "department_id": major.department_id,
            "department_name": department.name if department else "未知系",
            "faculty_id": faculty.id if faculty else None,
            "faculty_name": faculty.name if faculty else "未知学院",
        }

        result.append(model_to_dict(major, detailed, extra_fields))

    return result


# 通用函数：根据学院ID获取专业列表
def get_majors_by_faculty_id(faculty_id, detailed=False):
    """
    根据学院ID获取专业列表

    Args:
        faculty_id: 学院ID
        detailed: 是否返回详细信息

    Returns:
        专业列表
    """
    # 通过系表关联查询学院下的所有专业
    majors = (
        Major.query.join(Department).filter(Department.faculty_id == faculty_id).all()
    )

    if not detailed:
        return [model_to_dict(major, detailed) for major in majors]

    # 预加载所有相关的系和学院信息以避免N+1查询
    department_ids = {major.department_id for major in majors}
    departments = {
        d.id: d
        for d in Department.query.filter(Department.id.in_(department_ids)).all()
    }

    # 预加载学院信息
    faculty = Faculty.query.filter_by(id=faculty_id).first()
    faculty_name = faculty.name if faculty else "未知学院"

    result = []
    for major in majors:
        department = departments.get(major.department_id)
        extra_fields = {
            "department_id": major.department_id,
            "department_name": department.name if department else "未知系",
            "faculty_id": faculty_id,
            "faculty_name": faculty_name,
        }
        result.append(model_to_dict(major, detailed, extra_fields))

    return result


# 通用函数：根据系ID获取专业列表
def get_majors_by_department_id(department_id, detailed=False):
    """
    根据系ID获取专业列表

    Args:
        department_id: 系ID
        detailed: 是否返回详细信息

    Returns:
        专业列表
    """
    majors = Major.query.filter_by(department_id=department_id).all()

    if not detailed:
        return [model_to_dict(major, detailed) for major in majors]

    # 预加载所有相关的系和学院信息以避免N+1查询
    departments = {
        d.id: d for d in Department.query.filter(Department.id == department_id).all()
    }
    faculty_ids = {d.faculty_id for d in departments.values()}
    faculties = {
        f.id: f for f in Faculty.query.filter(Faculty.id.in_(faculty_ids)).all()
    }

    result = []
    for major in majors:
        department = departments.get(major.department_id)
        faculty = faculties.get(department.faculty_id) if department else None

        extra_fields = {
            "department_id": major.department_id,
            "department_name": department.name if department else "未知系",
            "faculty_id": faculty.id if faculty else None,
            "faculty_name": faculty.name if faculty else "未知学院",
        }
        result.append(model_to_dict(major, detailed, extra_fields))

    return result


# API端点：获取所有学院
@organization_bp.route("/faculties", methods=["GET"])
def get_faculties():
    """
    获取所有学院信息的API端点
    可选参数：detailed=true 返回详细信息
    """
    detailed = request.args.get("detailed", "false").lower() == "true"
    faculties = get_all_faculties(detailed)
    return jsonify({"faculties": faculties}), 200


# API端点：根据学院ID获取系列表
@organization_bp.route("/departments/<int:faculty_id>", methods=["GET"])
def get_departments(faculty_id):
    """
    根据学院ID获取系列表的API端点
    可选参数：detailed=true 返回详细信息
    """
    detailed = request.args.get("detailed", "false").lower() == "true"
    departments = get_departments_by_faculty_id(faculty_id, detailed)
    return jsonify({"departments": departments}), 200


# API端点：获取所有专业列表
@organization_bp.route("/majors", methods=["GET"])
def get_majors():
    """
    获取所有专业列表的API端点
    可选参数：detailed=true 返回详细信息
    """
    detailed = request.args.get("detailed", "false").lower() == "true"
    majors = get_all_majors(detailed)
    return jsonify({"majors": majors}), 200


# API端点：根据系ID获取专业列表
@organization_bp.route("/majors/department/<int:department_id>", methods=["GET"])
def get_majors_by_department(department_id):
    """
    根据系ID获取专业列表的API端点
    可选参数：detailed=true 返回详细信息
    """
    detailed = request.args.get("detailed", "false").lower() == "true"
    majors = get_majors_by_department_id(department_id, detailed)
    return jsonify({"majors": majors}), 200
