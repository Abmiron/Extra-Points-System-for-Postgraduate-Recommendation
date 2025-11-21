# -*- coding: utf-8 -*-
"""
申请审核模块

该模块包含申请的审核、拒绝等相关操作
"""

from flask import request, jsonify, current_app
from models import Application, Student, Rule, Department, Major, SystemSettings
from datetime import datetime
import pytz
import json
import os
import traceback
from extensions import db
from .application_utils import update_student_statistics
from . import application_bp


@application_bp.route("/applications/<int:id>/review", methods=["POST"])
def review_application(id):
    """
    审核申请
    """
    try:
        # 获取申请对象
        application = Application.query.get_or_404(id)
        
        # 检查申请状态
        if application.status != "pending":
            return jsonify({"error": "只能审核待审核状态的申请"}), 400
        
        # 获取审核数据
        data = request.get_json()
        
        # 获取审核结果和分数
        approval = data.get("approval")
        final_score = data.get("finalScore")
        review_comment = data.get("comment", "")
        reviewer = data.get("reviewer", "")
        
        # 字段名转换：将前端的驼峰式命名转换为后端的下划线命名
        field_mapping = {
            "approval": "approval",
            "finalScore": "final_score",
            "comment": "review_comment",
            "reviewer": "reviewed_by",
            "final_comprehensive_score": "final_comprehensive_score",
        }
        
        # 转换数据字段
        transformed_data = {}
        for key, value in data.items():
            # 使用映射的字段名，如果没有映射则使用原字段名
            new_key = field_mapping.get(key, key)
            transformed_data[new_key] = value
        
        # 使用转换后的数据
        data = transformed_data
        
        # 更新申请状态和审核信息
        if data.get("approval") is True:  # 明确检查是否为True
            application.status = "approved"
            application.final_score = data.get("final_score")
        else:
            application.status = "rejected"
            # 被拒绝的申请最终分数为0
            application.final_score = 0
        
        application.review_comment = data.get("review_comment", "")
        application.reviewed_by = data.get("reviewed_by", "")
        application.reviewed_at = datetime.now(pytz.timezone("Asia/Shanghai"))
        application.updated_at = datetime.now(pytz.timezone("Asia/Shanghai"))
        
        # 保存审核结果
        db.session.commit()
        
        # 如果申请被批准，更新学生统计数据
        if application.status == "approved":
            try:
                update_student_statistics(application.student_id)
            except Exception as e:
                # 记录更新统计失败但不回滚审核操作
                print(f"更新学生统计数据失败: {str(e)}")
        
        return jsonify({
            "id": application.id,
            "status": application.status,
            "message": "审核完成"
        }), 200
        
    except Exception as e:
        # 记录详细错误信息
        db.session.rollback()
        return jsonify({
            "error": f"审核申请失败: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500


@application_bp.route("/applications/<int:id>/reject", methods=["POST"])
def reject_application(id):
    """
    拒绝申请
    """
    try:
        # 获取申请对象
        application = Application.query.get_or_404(id)
        
        # 检查申请状态
        if application.status != "pending":
            return jsonify({"error": "只能拒绝待审核状态的申请"}), 400
        
        # 获取拒绝理由
        data = request.get_json()
        reason = data.get("reason", "")
        reviewer = data.get("reviewer", "")
        
        # 更新申请状态和拒绝信息
        application.status = "rejected"
        application.final_score = 0
        application.review_comment = reason
        application.reviewed_by = reviewer
        application.reviewed_at = datetime.now(pytz.timezone("Asia/Shanghai"))
        application.updated_at = datetime.now(pytz.timezone("Asia/Shanghai"))
        
        # 保存拒绝结果
        db.session.commit()
        
        return jsonify({
            "id": application.id,
            "status": application.status,
            "message": "申请已拒绝"
        }), 200
        
    except Exception as e:
        # 记录详细错误信息
        db.session.rollback()
        return jsonify({
            "error": f"拒绝申请失败: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500


@application_bp.route("/applications/<int:id>/approve", methods=["POST"])
def approve_application(id):
    """
    批准申请
    """
    try:
        # 获取申请对象
        application = Application.query.get_or_404(id)
        
        # 检查申请状态
        if application.status != "pending":
            return jsonify({"error": "只能批准待审核状态的申请"}), 400
        
        # 获取批准数据
        data = request.get_json()
        
        # 字段名转换：将前端的驼峰式命名转换为后端的下划线命名
        field_mapping = {
            "finalScore": "final_score",
            "comment": "review_comment",
            "reviewer": "reviewed_by",
            "ruleId": "rule_id",
        }
        
        # 转换数据字段
        transformed_data = {}
        for key, value in data.items():
            # 使用映射的字段名，如果没有映射则使用原字段名
            new_key = field_mapping.get(key, key)
            transformed_data[new_key] = value
        
        # 使用转换后的数据
        data = transformed_data
        
        # 更新申请状态和批准信息
        application.status = "approved"
        application.final_score = data.get("final_score")
        application.review_comment = data.get("review_comment", "")
        application.reviewed_by = data.get("reviewed_by", "")
        if "rule_id" in data:
            application.rule_id = data["rule_id"]
        application.reviewed_at = datetime.now(pytz.timezone("Asia/Shanghai"))
        application.updated_at = datetime.now(pytz.timezone("Asia/Shanghai"))
        
        # 保存批准结果
        db.session.commit()
        
        # 更新学生统计数据
        try:
            update_student_statistics(application.student_id)
        except Exception as e:
            # 记录更新统计失败但不回滚批准操作
            print(f"更新学生统计数据失败: {str(e)}")
        
        return jsonify({
            "id": application.id,
            "status": application.status,
            "message": "申请已批准"
        }), 200
        
    except Exception as e:
        # 记录详细错误信息
        db.session.rollback()
        return jsonify({
            "error": f"批准申请失败: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500


@application_bp.route("/applications/<int:id>/resubmit", methods=["POST"])
def resubmit_application(id):
    """
    重新提交申请
    """
    try:
        # 获取申请对象
        application = Application.query.get_or_404(id)
        
        # 检查申请状态
        if application.status != "rejected":
            return jsonify({"error": "只能重新提交已拒绝的申请"}), 400
        
        # 重置申请状态
        application.status = "pending"
        application.final_score = None
        application.review_comment = None
        application.reviewed_by = None
        application.reviewed_at = None
        application.updated_at = datetime.now(pytz.timezone("Asia/Shanghai"))
        
        # 保存重置结果
        db.session.commit()
        
        return jsonify({
            "id": application.id,
            "status": application.status,
            "message": "申请已重新提交"
        }), 200
        
    except Exception as e:
        # 记录详细错误信息
        db.session.rollback()
        return jsonify({
            "error": f"重新提交申请失败: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500


@application_bp.route("/applications/batch-review", methods=["POST"])
def batch_review_applications():
    """
    批量审核申请
    """
    try:
        # 获取审核数据
        data = request.get_json()
        application_ids = data.get("applicationIds", [])
        action = data.get("action")  # "approve" 或 "reject"
        comment = data.get("comment", "")
        reviewer = data.get("reviewer", "")
        scores = data.get("scores", {})  # 字典，键为申请ID，值为分数
        
        if not application_ids:
            return jsonify({"error": "未提供要审核的申请ID"}), 400
        
        if action not in ["approve", "reject"]:
            return jsonify({"error": "无效的操作类型"}), 400
        
        # 获取所有申请对象
        applications = Application.query.filter(Application.id.in_(application_ids)).all()
        
        # 检查是否所有申请都存在且状态为待审核
        invalid_applications = []
        for app in applications:
            if app.status != "pending":
                invalid_applications.append(app.id)
        
        if invalid_applications:
            return jsonify({
                "error": f"以下申请不是待审核状态: {invalid_applications}"
            }), 400
        
        # 需要更新统计数据的学生ID集合
        student_ids_to_update = set()
        
        # 更新申请状态
        for app in applications:
            if action == "approve":
                app.status = "approved"
                # 使用scores字典中的分数，如果没有则使用默认值
                app.final_score = scores.get(str(app.id)) or 0
                student_ids_to_update.add(app.student_id)
            else:  # reject
                app.status = "rejected"
                app.final_score = 0
            
            app.review_comment = comment
            app.reviewed_by = reviewer
            app.reviewed_at = datetime.now(pytz.timezone("Asia/Shanghai"))
            app.updated_at = datetime.now(pytz.timezone("Asia/Shanghai"))
        
        # 保存批量审核结果
        db.session.commit()
        
        # 更新相关学生的统计数据
        for student_id in student_ids_to_update:
            try:
                update_student_statistics(student_id)
            except Exception as e:
                # 记录更新统计失败但不回滚批量审核操作
                print(f"更新学生统计数据失败: {str(e)}")
        
        return jsonify({
            "approved": action == "approve",
            "count": len(applications),
            "message": f"已成功{action} {len(applications)}个申请"
        }), 200
        
    except Exception as e:
        # 记录详细错误信息
        db.session.rollback()
        return jsonify({
            "error": f"批量审核失败: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500


@application_bp.route("/applications/feedback", methods=["POST"])
def submit_feedback():
    """
    提交审核反馈（供学生查看审核意见）
    """
    try:
        # 获取反馈数据
        data = request.get_json()
        application_id = data.get("applicationId")
        feedback = data.get("feedback")
        
        # 获取申请对象
        application = Application.query.get_or_404(application_id)
        
        # 更新反馈信息
        # 注意：这里假设Application模型有一个feedback字段
        # 如果没有，可能需要修改数据库模型
        # application.feedback = feedback
        # 或者将反馈添加到review_comment中
        if application.review_comment:
            application.review_comment += f"\n\n学生反馈: {feedback}"
        else:
            application.review_comment = f"学生反馈: {feedback}"
        
        application.updated_at = datetime.now(pytz.timezone("Asia/Shanghai"))
        
        # 保存反馈
        db.session.commit()
        
        return jsonify({
            "id": application.id,
            "message": "反馈提交成功"
        }), 200
        
    except Exception as e:
        # 记录详细错误信息
        db.session.rollback()
        return jsonify({
            "error": f"提交反馈失败: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500