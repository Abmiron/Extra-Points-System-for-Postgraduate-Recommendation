from app import app, db
from models import Application
from sqlalchemy import inspect

with app.app_context():
    try:
        # 获取数据库检查器
        inspector = inspect(db.engine)
        
        # 检查application表是否存在
        if inspector.has_table('application'):
            # 获取当前表的列
            columns = inspector.get_columns('application')
            column_names = [col['name'] for col in columns]
            
            print("当前表结构列名:")
            print(column_names)
            
            # 检查需要添加的列
            columns_to_add = []
            
            # 检查final_score列
            if 'final_score' not in column_names:
                columns_to_add.append('final_score')
            
            # 检查review_comment列
            if 'review_comment' not in column_names:
                columns_to_add.append('review_comment')
            
            # 检查reviewed_at列
            if 'reviewed_at' not in column_names:
                columns_to_add.append('reviewed_at')
            
            # 检查reviewed_by列
            if 'reviewed_by' not in column_names:
                columns_to_add.append('reviewed_by')
            
            if columns_to_add:
                print(f"需要添加的列: {columns_to_add}")
                
                # 手动添加缺失的列
                with db.engine.connect() as conn:
                    if 'final_score' not in column_names:
                        conn.execute(db.text('ALTER TABLE application ADD COLUMN final_score FLOAT'))
                    if 'review_comment' not in column_names:
                        conn.execute(db.text('ALTER TABLE application ADD COLUMN review_comment TEXT'))
                    if 'reviewed_at' not in column_names:
                        conn.execute(db.text('ALTER TABLE application ADD COLUMN reviewed_at TIMESTAMP WITHOUT TIME ZONE'))
                    if 'reviewed_by' not in column_names:
                        conn.execute(db.text('ALTER TABLE application ADD COLUMN reviewed_by VARCHAR(100)'))
                    conn.commit()
                    print("列添加成功!")
            else:
                print("所有必要的列已存在")
        else:
            # 如果表不存在，创建所有表
            print("表不存在，正在创建...")
            db.create_all()
            print("表创建成功!")
            
    except Exception as e:
        print(f"错误: {e}")