from app import app, db
from sqlalchemy import inspect

with app.app_context():
    try:
        # 检查application表是否存在
        inspector = inspect(db.engine)
        table_exists = inspector.has_table('application')
        print(f'Application table exists: {table_exists}')
        
        # 如果表不存在，尝试创建所有表
        if not table_exists:
            print('Creating database tables...')
            db.create_all()
            print('Tables created successfully!')
        else:
            # 查询表中的记录数
            from models import Application
            count = Application.query.count()
            print(f'Number of application records: {count}')
    except Exception as e:
        print(f'Error: {e}')
        print('Database configuration might be incorrect.')