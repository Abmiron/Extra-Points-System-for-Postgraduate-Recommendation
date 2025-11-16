# -*- coding: utf-8 -*-
"""
初始化Rule表脚本
"""

from app import app
from models import db, Rule
from sqlalchemy import inspect

with app.app_context():
    try:
        # 创建所有模型对应的表（仅创建不存在的表）
        db.create_all()
        print("Rule表创建成功")
    except Exception as e:
        print(f"创建Rule表失败: {e}")