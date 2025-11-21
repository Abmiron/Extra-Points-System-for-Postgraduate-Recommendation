# -*- coding: utf-8 -*-
"""
申请管理辅助函数模块

该模块包含申请管理相关的辅助函数
"""

from models import Application, Student, SystemSettings
from extensions import db


def update_student_statistics(student_id):
    """
    辅助函数：更新学生的统计数据
    
    Args:
        student_id: 学生ID
        
    Returns:
        dict: 更新后的学生统计数据
    """
    # 查询学生的所有已通过申请
    applications = Application.query.filter_by(
        student_id=student_id, status="approved"
    ).all()

    # 按申请类型分类统计
    academic_score_calculated = sum(
        app.final_score
        for app in applications
        if app.final_score is not None and app.application_type == "academic"
    )
    comprehensive_score = sum(
        app.final_score
        for app in applications
        if app.final_score is not None and app.application_type == "comprehensive"
    )

    # 获取学生对象
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return None

    # 更新学生统计数据
    student.academic_specialty_total = academic_score_calculated  # 学术专长总分
    student.comprehensive_performance_total = comprehensive_score  # 综合表现总分

    # 获取系统设置
    system_settings = SystemSettings.query.first()
    if system_settings:
        # 计算综合成绩：学业成绩 * 学业成绩权重 / 100 + 学术专长总分 + 综合表现总分
        academic_score = student.academic_score or 0.0
        specialty_total = student.academic_specialty_total or 0.0
        performance_total = student.comprehensive_performance_total or 0.0

        calculated_score = (
            (academic_score * system_settings.academic_score_weight / 100)
            + specialty_total
            + performance_total
        )

        # 更新综合成绩，保留四位小数
        student.comprehensive_score = round(calculated_score, 4)

    # 保存更改到数据库
    db.session.commit()

    return {
        "academic_specialty_total": student.academic_specialty_total,
        "comprehensive_performance_total": student.comprehensive_performance_total,
        "comprehensive_score": student.comprehensive_score,
    }