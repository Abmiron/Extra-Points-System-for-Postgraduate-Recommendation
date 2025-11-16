# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为application表添加rule_id字段
"""

from app import app
from models import db
from sqlalchemy import text

with app.app_context():
    try:
        # 连接到数据库
        conn = db.engine.connect()
        
        # 检查并添加rule_id字段
        conn.execute(text("""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'application' AND column_name = 'rule_id') THEN
                    ALTER TABLE application ADD COLUMN rule_id INTEGER;
                    ALTER TABLE application ADD CONSTRAINT fk_application_rule FOREIGN KEY (rule_id) REFERENCES rule(id) ON DELETE SET NULL;
                END IF;
            END $$;
        """))
        
        # 提交事务
        conn.execute(text("COMMIT"))
        
        print("为application表添加rule_id字段成功")
    except Exception as e:
        print(f"添加rule_id字段失败: {e}")