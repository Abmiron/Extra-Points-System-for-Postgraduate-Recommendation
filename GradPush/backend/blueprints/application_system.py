# -*- coding: utf-8 -*-
"""
申请系统模块

该模块包含系统相关功能，如健康检查、重新计算等
"""

from flask import request, jsonify, current_app
from models import Application, Student, Rule, Department, Major, SystemSettings
from datetime import datetime, timedelta
import pytz
import json
import os
import traceback
from extensions import db
from .application_utils import update_student_statistics
from . import application_bp


@application_bp.route("/applications/health", methods=["GET"])
def health_check():
    """
    健康检查接口
    """
    try:
        # 检查数据库连接
        db.session.execute("SELECT 1")
        
        # 检查上传目录
        upload_folder = current_app.config.get("UPLOAD_FOLDER", "")
        file_folder = current_app.config.get("FILE_FOLDER", "")
        upload_folder_exists = os.path.exists(upload_folder) if upload_folder else False
        file_folder_exists = os.path.exists(file_folder) if file_folder else False
        
        # 检查系统设置
        settings = SystemSettings.query.first()
        settings_available = settings is not None
        
        # 返回健康状态
        health_status = {
            "status": "healthy",
            "database": "connected",
            "uploadFolder": {
                "exists": upload_folder_exists,
                "path": upload_folder
            },
            "fileFolder": {
                "exists": file_folder_exists,
                "path": file_folder
            },
            "systemSettings": {
                "available": settings_available
            },
            "timestamp": datetime.now(pytz.timezone("Asia/Shanghai")).isoformat()
        }
        
        return jsonify(health_status), 200
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(pytz.timezone("Asia/Shanghai")).isoformat()
        }), 500


@application_bp.route("/applications/recalculate-scores", methods=["POST"])
def recalculate_comprehensive_scores():
    """
    重新计算所有学生的综合成绩
    """
    try:
        # 获取所有学生
        students = Student.query.all()
        
        # 记录处理结果
        processed_count = 0
        failed_count = 0
        failed_students = []
        
        # 逐个重新计算学生的统计数据
        for student in students:
            try:
                update_student_statistics(student.student_id)
                processed_count += 1
            except Exception as e:
                failed_count += 1
                failed_students.append({
                    "studentId": student.student_id,
                    "studentName": student.name,
                    "error": str(e)
                })
        
        # 返回重新计算结果
        result = {
            "totalStudents": len(students),
            "processedCount": processed_count,
            "failedCount": failed_count,
            "failedStudents": failed_students,
            "timestamp": datetime.now(pytz.timezone("Asia/Shanghai")).isoformat()
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "error": f"重新计算失败: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500


@application_bp.route("/applications/recalculate-score/<string:student_id>", methods=["POST"])
def recalculate_student_score(student_id):
    """
    重新计算单个学生的综合成绩
    """
    try:
        # 检查学生是否存在
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            return jsonify({"error": "学生不存在"}), 404
        
        # 重新计算学生的统计数据
        update_student_statistics(student_id)
        
        # 返回成功结果
        result = {
            "studentId": student_id,
            "studentName": student.name,
            "message": "综合成绩重新计算成功",
            "timestamp": datetime.now(pytz.timezone("Asia/Shanghai")).isoformat()
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "error": f"重新计算学生成绩失败: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500


@application_bp.route("/applications/export-data", methods=["GET"])
def export_application_data():
    """
    导出申请数据
    """
    try:
        # 获取查询参数
        export_format = request.args.get("format", "json")  # 默认JSON格式
        status = request.args.get("status")
        application_type = request.args.get("applicationType")
        
        # 构建查询
        query = Application.query
        
        # 应用筛选条件
        if status:
            query = query.filter_by(status=status)
        
        if application_type:
            query = query.filter_by(application_type=application_type)
        
        # 执行查询
        applications = query.all()
        
        # 构建导出数据
        export_data = []
        
        for app in applications:
            # 获取系和专业信息
            department = Department.query.get(app.department_id) if app.department_id else None
            major = Major.query.get(app.major_id) if app.major_id else None
            
            app_data = {
                "申请ID": app.id,
                "学号": app.student_id,
                "学生姓名": app.student_name,
                "系": department.name if department else "未知",
                "专业": major.name if major else "未知",
                "申请类型": "学术专长" if app.application_type == "academic" else "综合表现" if app.application_type == "performance" else "其他",
                "申请时间": app.applied_at.isoformat() if app.applied_at else "",
                "自评分数": app.self_score or "",
                "最终分数": app.final_score or "",
                "状态": "待审核" if app.status == "pending" else "已批准" if app.status == "approved" else "已拒绝" if app.status == "rejected" else "其他",
                "审核意见": app.review_comment or "",
                "审核时间": app.reviewed_at.isoformat() if app.reviewed_at else "",
                "审核人": app.reviewed_by or "",
                "项目名称": app.project_name or "",
                "获奖日期": app.award_date.isoformat() if app.award_date else "",
                "获奖级别": app.award_level or "",
                "获奖类型": app.award_type or "",
                "描述": app.description or "",
            }
            
            # 根据申请类型添加相应字段
            if app.application_type == "academic":
                app_data.update({
                    "学术类型": app.academic_type or "",
                    "研究类型": app.research_type or "",
                    "创新级别": app.innovation_level or "",
                    "创新角色": app.innovation_role or "",
                    "获奖等级": app.award_grade or "",
                    "获奖类别": app.award_category or "",
                    "作者排序类型": app.author_rank_type or "",
                    "作者顺序": app.author_order or "",
                })
            elif app.application_type == "performance":
                app_data.update({
                    "表现类型": app.performance_type or "",
                    "表现级别": app.performance_level or "",
                    "表现参与度": app.performance_participation or "",
                    "团队角色": app.team_role or "",
                })
            
            export_data.append(app_data)
        
        # 根据格式返回数据
        if export_format.lower() == "json":
            return jsonify({
                "exportedAt": datetime.now(pytz.timezone("Asia/Shanghai")).isoformat(),
                "totalRecords": len(export_data),
                "data": export_data
            }), 200
        else:
            return jsonify({"error": "不支持的导出格式"}), 400
        
    except Exception as e:
        return jsonify({
            "error": f"导出数据失败: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500


@application_bp.route("/applications/cleanup-expired", methods=["POST"])
def cleanup_expired_applications():
    """
    清理过期的申请数据（可选功能）
    """
    try:
        # 获取系统设置中的保留期限
        settings = SystemSettings.query.first()
        if not settings or not hasattr(settings, 'application_retention_days'):
            retention_days = 365  # 默认保留1年
        else:
            retention_days = settings.application_retention_days
        
        # 计算过期日期
        expired_date = datetime.now(pytz.timezone("Asia/Shanghai")) - timedelta(days=retention_days)
        
        # 查询过期的已完成申请（已批准或已拒绝）
        expired_applications = Application.query.filter(
            Application.status.in_(["approved", "rejected"]),
            Application.reviewed_at <= expired_date
        ).all()
        
        # 记录要删除的文件
        files_to_delete = []
        for app in expired_applications:
            if app.files:
                for file in app.files:
                    if "path" in file and os.path.exists(file["path"]):
                        files_to_delete.append(file["path"])
        
        # 删除申请记录
        deleted_count = len(expired_applications)
        for app in expired_applications:
            db.session.delete(app)
        
        # 提交删除操作
        db.session.commit()
        
        # 删除相关文件
        deleted_files_count = 0
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                deleted_files_count += 1
            except Exception as e:
                # 记录文件删除失败但继续处理其他文件
                print(f"删除文件失败: {file_path}, 错误: {str(e)}")
        
        # 返回清理结果
        result = {
            "deletedApplications": deleted_count,
            "deletedFiles": deleted_files_count,
            "retentionDays": retention_days,
            "expiredBefore": expired_date.isoformat(),
            "timestamp": datetime.now(pytz.timezone("Asia/Shanghai")).isoformat()
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        # 记录详细错误信息
        db.session.rollback()
        return jsonify({
            "error": f"清理过期数据失败: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500


@application_bp.route("/applications/cache/clear", methods=["POST"])
def clear_application_cache():
    """
    清除申请缓存（如果有缓存机制）
    """
    try:
        # 这里可以实现缓存清除逻辑
        # 例如，如果使用Redis或其他缓存系统
        # cache.delete_pattern("applications:*")
        
        return jsonify({
            "message": "缓存已清除",
            "timestamp": datetime.now(pytz.timezone("Asia/Shanghai")).isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"清除缓存失败: {str(e)}"
        }), 500


@application_bp.route("/applications/batch-update", methods=["POST"])
def batch_update_applications():
    """
    批量更新申请信息
    """
    try:
        # 获取更新数据
        data = request.get_json()
        application_ids = data.get("applicationIds", [])
        update_data = data.get("updateData", {})
        
        if not application_ids:
            return jsonify({"error": "未提供要更新的申请ID"}), 400
        
        # 字段名转换：将前端的驼峰式命名转换为后端的下划线命名
        field_mapping = {
            "studentId": "student_id",
            "studentName": "student_name",
            "departmentId": "department_id",
            "majorId": "major_id",
            "applicationType": "application_type",
            "status": "status",
            "reviewComment": "review_comment",
            "reviewedBy": "reviewed_by",
        }
        
        # 转换更新数据字段
        transformed_update_data = {}
        for key, value in update_data.items():
            new_key = field_mapping.get(key, key)
            transformed_update_data[new_key] = value
        
        # 更新时间字段
        transformed_update_data["updated_at"] = datetime.now(pytz.timezone("Asia/Shanghai"))
        
        # 执行批量更新
        result = Application.query.filter(
            Application.id.in_(application_ids)
        ).update(transformed_update_data, synchronize_session=False)
        
        # 提交更新
        db.session.commit()
        
        # 找出需要更新统计数据的学生ID
        updated_applications = Application.query.filter(
            Application.id.in_(application_ids),
            Application.status == "approved"
        ).all()
        
        student_ids_to_update = {app.student_id for app in updated_applications}
        
        # 更新相关学生的统计数据
        for student_id in student_ids_to_update:
            try:
                update_student_statistics(student_id)
            except Exception as e:
                # 记录更新统计失败但不回滚批量更新操作
                print(f"更新学生统计数据失败: {str(e)}")
        
        return jsonify({
            "updatedCount": result,
            "message": f"成功更新{result}个申请"
        }), 200
        
    except Exception as e:
        # 记录详细错误信息
        db.session.rollback()
        return jsonify({
            "error": f"批量更新失败: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500