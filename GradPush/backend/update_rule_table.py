# -*- coding: utf-8 -*-
"""
更新Rule表结构脚本
"""

from app import app
from models import db
from sqlalchemy import text

with app.app_context():
    try:
        # 连接到数据库
        conn = db.engine.connect()
        
        # 检查并添加category字段
        conn.execute(text("""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'rule' AND column_name = 'category') THEN
                    ALTER TABLE rule ADD COLUMN category VARCHAR(50);
                END IF;
            END $$;
        """))
        
        # 检查并添加participation_type字段
        conn.execute(text("""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'rule' AND column_name = 'participation_type') THEN
                    ALTER TABLE rule ADD COLUMN participation_type VARCHAR(50) DEFAULT 'individual';
                END IF;
            END $$;
        """))
        
        # 检查并添加team_role字段
        conn.execute(text("""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'rule' AND column_name = 'team_role') THEN
                    ALTER TABLE rule ADD COLUMN team_role VARCHAR(50);
                END IF;
            END $$;
        """))
        
        # 检查并添加author_rank_type字段
        conn.execute(text("""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'rule' AND column_name = 'author_rank_type') THEN
                    ALTER TABLE rule ADD COLUMN author_rank_type VARCHAR(50) DEFAULT 'unranked';
                END IF;
            END $$;
        """))
        
        # 检查并添加author_rank字段
        conn.execute(text("""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'rule' AND column_name = 'author_rank') THEN
                    ALTER TABLE rule ADD COLUMN author_rank INTEGER;
                END IF;
            END $$;
        """))
        
        # 提交事务
        conn.execute(text("COMMIT"))
        
        print("Rule表结构更新成功")
    except Exception as e:
        print(f"更新Rule表结构失败: {e}")