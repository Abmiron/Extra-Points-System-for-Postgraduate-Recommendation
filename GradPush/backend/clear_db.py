# -*- coding: utf-8 -*-
"""
清理数据库数据的脚本
"""

from app import app
from extensions import db
from models import *  # 导入所有模型

print("正在清理数据库数据...")

with app.app_context():
    try:
        # 按依赖关系顺序删除数据，避免外键约束错误
        # 先删除没有外键依赖的数据
        PerformanceDetail.query.delete()
        Application.query.delete()
        Rule.query.delete()
        Student.query.delete()
        User.query.delete()
        Major.query.delete()
        Department.query.delete()
        Faculty.query.delete()
        
        # 提交事务
        db.session.commit()
        print("数据库数据清理完成！")
    except Exception as e:
        db.session.rollback()
        print(f"清理数据时发生错误：{str(e)}")
        import traceback
        traceback.print_exc()