# -*- coding: utf-8 -*-
"""
数据库初始化脚本

该脚本用于初始化数据库表结构
"""

import sys
import os

# 添加当前目录的父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Application, AcademicSpecialtyDetail, ComprehensivePerformanceDetail, StudentEvaluation, Student

with app.app_context():
    try:
        print("开始创建数据库表结构...")
        # 直接创建所有表
        db.create_all()
        print("表结构创建完成!")
        
        # 列出所有创建的表
        tables = db.inspect(db.engine).get_table_names()
        print(f"已创建的表: {tables}")
            
    except Exception as e:
        print(f"数据库操作失败: {e}")