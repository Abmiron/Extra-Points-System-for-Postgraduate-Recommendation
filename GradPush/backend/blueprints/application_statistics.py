# -*- coding: utf-8 -*-
"""
申请统计模块

该模块包含各种统计功能，如教师统计、学生统计等
"""

from flask import request, jsonify
from models import Application, Student, Department, Major, SystemSettings
from datetime import datetime, timedelta
import pytz
from extensions import db
from . import application_bp


@application_bp.route("/applications/teacher-statistics", methods=["GET"])
def get_teacher_statistics():
    """
    获取教师审核统计数据
    """
    try:
        # 验证必要参数
        teacher_name = request.args.get("teacherName")
        if not teacher_name:
            return jsonify({"error": "教师名称不能为空"}), 400
        
        # 查询该教师审核的申请
        reviewed_applications = Application.query.filter(
            Application.reviewed_by.like(f"%{teacher_name}%")
        ).all()
        
        # 查询该教师待审核的申请
        pending_applications = Application.query.filter_by(
            status="pending"
        ).all()
        
        # 计算本月审核数量
        current_month = datetime.now(pytz.timezone("Asia/Shanghai")).month
        current_year = datetime.now(pytz.timezone("Asia/Shanghai")).year
        
        month_reviewed = Application.query.filter(
            Application.reviewed_by.like(f"%{teacher_name}%"),
            db.extract('month', Application.reviewed_at) == current_month,
            db.extract('year', Application.reviewed_at) == current_year
        ).count()
        
        # 计算平均审核时间
        total_review_time = 0
        reviewed_count = 0
        
        for app in reviewed_applications:
            if app.applied_at and app.reviewed_at:
                review_time = (app.reviewed_at - app.applied_at).total_seconds() / 3600  # 转换为小时
                total_review_time += review_time
                reviewed_count += 1
        
        avg_review_time = total_review_time / reviewed_count if reviewed_count > 0 else 0
        
        # 返回统计数据
        statistics = {
            "teacherName": teacher_name,
            "totalReviewed": len(reviewed_applications),
            "pendingReview": len(pending_applications),
            "monthReviewed": month_reviewed,
            "avgReviewTimeHours": round(avg_review_time, 2),
        }
        
        return jsonify(statistics), 200
        
    except Exception as e:
        return jsonify({
            "error": f"获取教师统计数据失败: {str(e)}"
        }), 500


@application_bp.route("/applications/statistics/overview", methods=["GET"])
def get_statistics_overview():
    """
    获取申请统计概览
    """
    try:
        # 获取所有申请
        all_applications = Application.query.count()
        
        # 按状态统计
        pending_count = Application.query.filter_by(status="pending").count()
        approved_count = Application.query.filter_by(status="approved").count()
        rejected_count = Application.query.filter_by(status="rejected").count()
        
        # 按类型统计
        academic_count = Application.query.filter_by(application_type="academic").count()
        performance_count = Application.query.filter_by(application_type="performance").count()
        
        # 本月申请数
        current_month = datetime.now(pytz.timezone("Asia/Shanghai")).month
        current_year = datetime.now(pytz.timezone("Asia/Shanghai")).year
        
        month_applications = Application.query.filter(
            db.extract('month', Application.applied_at) == current_month,
            db.extract('year', Application.applied_at) == current_year
        ).count()
        
        # 本月审核数
        month_reviews = Application.query.filter(
            db.extract('month', Application.reviewed_at) == current_month,
            db.extract('year', Application.reviewed_at) == current_year
        ).count()
        
        # 返回统计概览
        overview = {
            "totalApplications": all_applications,
            "statusBreakdown": {
                "pending": pending_count,
                "approved": approved_count,
                "rejected": rejected_count
            },
            "typeBreakdown": {
                "academic": academic_count,
                "performance": performance_count
            },
            "monthlyStats": {
                "applications": month_applications,
                "reviews": month_reviews
            }
        }
        
        return jsonify(overview), 200
        
    except Exception as e:
        return jsonify({
            "error": f"获取统计概览失败: {str(e)}"
        }), 500


@application_bp.route("/applications/statistics/department", methods=["GET"])
def get_department_statistics():
    """
    获取各系的申请统计数据
    """
    try:
        # 获取所有系
        departments = Department.query.all()
        
        department_stats = []
        
        for dept in departments:
            # 统计该系的申请数
            total_applications = Application.query.filter_by(
                department_id=dept.id
            ).count()
            
            # 按状态统计
            approved_count = Application.query.filter_by(
                department_id=dept.id,
                status="approved"
            ).count()
            
            rejected_count = Application.query.filter_by(
                department_id=dept.id,
                status="rejected"
            ).count()
            
            pending_count = Application.query.filter_by(
                department_id=dept.id,
                status="pending"
            ).count()
            
            # 计算通过率
            pass_rate = (approved_count / total_applications * 100) if total_applications > 0 else 0
            
            department_stats.append({
                "departmentId": dept.id,
                "departmentName": dept.name,
                "totalApplications": total_applications,
                "approvedCount": approved_count,
                "rejectedCount": rejected_count,
                "pendingCount": pending_count,
                "passRate": round(pass_rate, 2)
            })
        
        # 按申请总数排序
        department_stats.sort(key=lambda x: x["totalApplications"], reverse=True)
        
        return jsonify(department_stats), 200
        
    except Exception as e:
        return jsonify({
            "error": f"获取系统计数据失败: {str(e)}"
        }), 500


@application_bp.route("/applications/statistics/student/<string:student_id>", methods=["GET"])
def get_student_statistics(student_id):
    """
    获取单个学生的申请统计数据
    """
    try:
        # 查询学生信息
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            # 如果学生不存在，仍尝试获取其申请数据
            student_name = "未知学生"
        else:
            student_name = student.name
        
        # 查询该学生的所有申请
        applications = Application.query.filter_by(student_id=student_id).all()
        
        # 按状态统计
        approved_applications = [app for app in applications if app.status == "approved"]
        rejected_applications = [app for app in applications if app.status == "rejected"]
        pending_applications = [app for app in applications if app.status == "pending"]
        
        # 按类型统计
        academic_applications = [app for app in applications if app.application_type == "academic"]
        performance_applications = [app for app in applications if app.application_type == "performance"]
        
        # 计算总分
        total_score = sum(app.final_score or 0 for app in approved_applications)
        
        # 计算平均分数
        avg_score = (total_score / len(approved_applications)) if approved_applications else 0
        
        # 获取最近的申请
        recent_applications = sorted(
            applications,
            key=lambda x: x.applied_at or datetime.min,
            reverse=True
        )[:5]  # 最多5个
        
        # 格式化最近申请数据
        formatted_recent = [
            {
                "id": app.id,
                "type": app.application_type,
                "status": app.status,
                "appliedAt": app.applied_at.isoformat() if app.applied_at else None,
                "score": app.final_score
            }
            for app in recent_applications
        ]
        
        statistics = {
            "studentId": student_id,
            "studentName": student_name,
            "totalApplications": len(applications),
            "statusBreakdown": {
                "approved": len(approved_applications),
                "rejected": len(rejected_applications),
                "pending": len(pending_applications)
            },
            "typeBreakdown": {
                "academic": len(academic_applications),
                "performance": len(performance_applications)
            },
            "scoreStats": {
                "totalScore": total_score,
                "averageScore": round(avg_score, 2) if avg_score else 0,
                "approvedCount": len(approved_applications)
            },
            "recentApplications": formatted_recent
        }
        
        return jsonify(statistics), 200
        
    except Exception as e:
        return jsonify({
            "error": f"获取学生统计数据失败: {str(e)}"
        }), 500


@application_bp.route("/applications/statistics/trend", methods=["GET"])
def get_application_trend():
    """
    获取申请趋势统计
    """
    try:
        # 获取时间范围参数
        months = request.args.get("months", 6, type=int)  # 默认6个月
        
        # 获取当前日期
        now = datetime.now(pytz.timezone("Asia/Shanghai"))
        
        # 计算开始日期
        start_date = now - timedelta(days=months * 30)
        start_date = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # 按月统计
        trend_data = []
        current_date = start_date
        
        while current_date <= now:
            # 计算该月的结束日期
            if current_date.month == 12:
                next_month = current_date.replace(year=current_date.year + 1, month=1)
            else:
                next_month = current_date.replace(month=current_date.month + 1)
            
            # 统计该月的申请数
            month_applications = Application.query.filter(
                Application.applied_at >= current_date,
                Application.applied_at < next_month
            ).count()
            
            # 统计该月的审核数
            month_reviews = Application.query.filter(
                Application.reviewed_at >= current_date,
                Application.reviewed_at < next_month
            ).count()
            
            # 统计该月的批准数
            month_approvals = Application.query.filter(
                Application.status == "approved",
                Application.reviewed_at >= current_date,
                Application.reviewed_at < next_month
            ).count()
            
            # 添加到趋势数据
            trend_data.append({
                "month": current_date.strftime("%Y-%m"),
                "applications": month_applications,
                "reviews": month_reviews,
                "approvals": month_approvals
            })
            
            # 移动到下一个月
            current_date = next_month
        
        return jsonify(trend_data), 200
        
    except Exception as e:
        return jsonify({
            "error": f"获取申请趋势失败: {str(e)}"
        }), 500


@application_bp.route("/applications/statistics/type-distribution", methods=["GET"])
def get_type_distribution():
    """
    获取申请类型分布统计
    """
    try:
        # 按申请类型分组统计
        academic_count = Application.query.filter_by(application_type="academic").count()
        performance_count = Application.query.filter_by(application_type="performance").count()
        
        # 学术专长内部类型统计
        academic_type_stats = db.session.query(
            Application.academic_type,
            db.func.count(Application.id)
        ).filter(
            Application.application_type == "academic",
            Application.academic_type.isnot(None)
        ).group_by(
            Application.academic_type
        ).all()
        
        # 综合表现内部类型统计
        performance_type_stats = db.session.query(
            Application.performance_type,
            db.func.count(Application.id)
        ).filter(
            Application.application_type == "performance",
            Application.performance_type.isnot(None)
        ).group_by(
            Application.performance_type
        ).all()
        
        # 构建响应数据
        distribution = {
            "mainTypes": {
                "academic": academic_count,
                "performance": performance_count
            },
            "academicSubtypes": {
                stat[0]: stat[1] for stat in academic_type_stats
            },
            "performanceSubtypes": {
                stat[0]: stat[1] for stat in performance_type_stats
            }
        }
        
        return jsonify(distribution), 200
        
    except Exception as e:
        return jsonify({
            "error": f"获取类型分布失败: {str(e)}"
        }), 500