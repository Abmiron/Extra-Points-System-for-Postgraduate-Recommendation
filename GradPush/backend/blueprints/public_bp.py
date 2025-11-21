# -*- coding: utf-8 -*-
"""
公开接口蓝图
包含无需登录即可访问的接口
"""
from flask import Blueprint, jsonify
from datetime import datetime, time

# 导入模型和扩展
# 由于app.py在backend目录下运行，Python路径已经包含backend目录
from models import SystemSettings
from extensions import db

# 创建公开接口蓝图
public_bp = Blueprint('public', __name__, url_prefix='/public')


@public_bp.route('/system-info', methods=['GET'])
def get_system_info():
    """
    获取公开的系统信息，包括推免申请开放时间
    此接口无需登录权限即可访问
    """
    try:
        # 从数据库中获取系统设置
        system_settings = SystemSettings.query.first()
        
        # 如果数据库中没有系统设置，则使用默认值
        if system_settings:
            # 直接使用数据库中存储的完整日期时间
            if system_settings.application_start:
                start_datetime = system_settings.application_start
            else:
                start_datetime = datetime(2025, 9, 1, 10, 0, 0)  # 默认开始时间设置为10:00
            
            if system_settings.application_end:
                end_datetime = system_settings.application_end
            else:
                end_datetime = datetime(2025, 9, 30, 17, 0, 0)  # 默认结束时间设置为17:00
            
            system_status = system_settings.system_status if system_settings.system_status else "online"
        else:
            # 默认值
            start_datetime = datetime(2025, 9, 1, 0, 0, 0)
            end_datetime = datetime(2025, 9, 30, 23, 59, 59)
            system_status = "online"
        
        # 构建系统信息响应
        system_info = {
            "applicationStartTime": start_datetime.isoformat(),
            "applicationEndTime": end_datetime.isoformat(),
            "systemName": "研究生推免系统",
            "version": "1.0.0",
            "status": "正常运行" if system_status == "online" else "维护中"
        }
        
        return jsonify({
            "code": 200,
            "message": "获取系统信息成功",
            "data": system_info
        })
    
    except Exception as e:
        # 记录错误日志
        print(f"获取系统信息异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取系统信息失败: {str(e)}",
            "data": None
        })