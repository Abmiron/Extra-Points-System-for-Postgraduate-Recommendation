# -*- coding: utf-8 -*-
"""
检查数据库编码脚本
"""

from app import app
from models import db

with app.app_context():
    try:
        # 检查数据库连接和编码
        connection = db.engine.connect()
        result = connection.execute(db.text("SHOW client_encoding"))
        client_encoding = result.scalar()
        
        result = connection.execute(db.text("SHOW server_encoding"))
        server_encoding = result.scalar()
        
        print(f"Client Encoding: {client_encoding}")
        print(f"Server Encoding: {server_encoding}")
        
        # 尝试直接插入中文数据
        connection.execute(db.text("INSERT INTO rule (name, type, level, score) VALUES ('测试规则', 'academic', 'A', 10.0)"))
        connection.commit()
        
        # 查询所有规则
        result = connection.execute(db.text("SELECT * FROM rule"))
        rules = result.fetchall()
        print("\n所有规则:")
        for rule in rules:
            print(f"ID: {rule[0]}, Name: {rule[1]}, Type: {rule[2]}, Level: {rule[3]}, Score: {rule[6]}")
        
        connection.close()
        
        print("\n中文数据测试成功！")
        
    except Exception as e:
        print(f"检查失败: {e}")