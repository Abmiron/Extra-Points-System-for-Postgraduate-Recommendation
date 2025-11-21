# -*- coding: utf-8 -*-
"""
测试时间数据存储脚本 - 完整模拟API调用流程
包括模拟前端ISO格式时间字符串的处理和存储
"""

import sys
sys.path.append('.')

from extensions import db
from models import SystemSettings
from app import app
from datetime import datetime
import pytz

# 设置上海时区
shanghai_tz = pytz.timezone("Asia/Shanghai")

# 模拟前端prepareDateTimeForApi函数
def simulate_frontend_prepare_datetime(date_time_obj):
    """模拟前端将日期对象转换为ISO格式字符串"""
    return date_time_obj.isoformat()

# 模拟后端处理函数（从admin_bp.py复制）
def simulate_backend_process(settings, iso_start_str, iso_end_str):
    """模拟后端处理ISO格式时间字符串的过程"""
    if iso_start_str:
        settings.application_start = datetime.fromisoformat(iso_start_str)
    
    if iso_end_str:
        settings.application_end = datetime.fromisoformat(iso_end_str)
    
    db.session.commit()
    print("✅ 后端处理完成并提交到数据库")

with app.app_context():
    try:
        # 获取或创建系统设置
        settings = SystemSettings.query.first()
        if not settings:
            settings = SystemSettings()
            db.session.add(settings)
            db.session.commit()
        
        print("=== 测试开始: 完整模拟API调用流程 ===")
        
        # 步骤1: 创建带有时分的测试时间（模拟前端用户输入）
        test_start_time = datetime.now(shanghai_tz).replace(hour=10, minute=15, second=0, microsecond=0)
        test_end_time = datetime.now(shanghai_tz).replace(hour=16, minute=30, second=0, microsecond=0)
        
        print(f"\n📱 模拟前端: 创建测试时间")
        print(f"开始时间: {test_start_time} (类型: {type(test_start_time)})")
        print(f"结束时间: {test_end_time} (类型: {type(test_end_time)})")
        
        # 步骤2: 前端转换为ISO格式字符串（模拟前端prepareDateTimeForApi）
        iso_start_str = simulate_frontend_prepare_datetime(test_start_time)
        iso_end_str = simulate_frontend_prepare_datetime(test_end_time)
        
        print(f"\n📱 模拟前端: 转换为ISO格式字符串")
        print(f"开始时间ISO字符串: {iso_start_str} (类型: {type(iso_start_str)})")
        print(f"结束时间ISO字符串: {iso_end_str} (类型: {type(iso_end_str)})")
        
        # 步骤3: 后端接收并处理（模拟admin_bp.py中的update_system_settings）
        print(f"\n⚙️ 模拟后端: 接收ISO字符串并解析")
        simulate_backend_process(settings, iso_start_str, iso_end_str)
        
        # 步骤4: 重新查询数据库，验证存储结果
        settings = SystemSettings.query.first()
        
        print(f"\n💾 验证数据库存储结果")
        print(f"申请开始时间类型: {type(settings.application_start)}")
        print(f"申请开始时间值: {settings.application_start}")
        print(f"申请截止时间类型: {type(settings.application_end)}")
        print(f"申请截止时间值: {settings.application_end}")
        
        # 详细检查时分信息
        if settings.application_start and settings.application_start.hour is not None:
            print(f"\n✅ 时间精度检查成功: 包含时分信息")
            print(f"开始时间小时: {settings.application_start.hour}")
            print(f"开始时间分钟: {settings.application_start.minute}")
            print(f"结束时间小时: {settings.application_end.hour}")
            print(f"结束时间分钟: {settings.application_end.minute}")
            
            # 验证是否与原始值匹配
            if (settings.application_start.hour == test_start_time.hour and 
                settings.application_start.minute == test_start_time.minute and
                settings.application_end.hour == test_end_time.hour and 
                settings.application_end.minute == test_end_time.minute):
                print("\n🎉 完全匹配: 数据库中存储的时分与原始输入一致!")
            else:
                print("\n❌ 不匹配: 数据库中存储的时分与原始输入不一致!")
        else:
            print(f"\n❌ 时间精度检查失败: 不包含时分信息")
            
        print("\n=== 测试完成 ===")
            
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.session.close()