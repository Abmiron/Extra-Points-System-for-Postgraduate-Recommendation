# -*- coding: utf-8 -*-
"""
初始化数据库的脚本
"""

from app import app
from extensions import db
from models import *  # 导入所有模型

print("正在初始化数据库...")

with app.app_context():
    # 创建所有表
    db.create_all()
    
    # 检查表是否创建成功
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"\n成功创建 {len(tables)} 个表:")
    for table in tables:
        print(f"- {table}")
        
        # 获取表结构
        columns = inspector.get_columns(table)
        for column in columns:
            print(f"  - {column['name']} ({column['type']})")

print("\n数据库初始化完成！")