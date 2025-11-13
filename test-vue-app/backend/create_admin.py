from app import app, db
from models import User

with app.app_context():
    # 检查是否已有管理员用户
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        # 创建管理员用户
        admin = User(
            username='admin',
            password='admin123',  # 密码将在模型中自动哈希
            role='admin',
            status='active',
            name='系统管理员'
        )
        db.session.add(admin)
        db.session.commit()
        print('管理员用户创建成功')
    else:
        print('管理员用户已存在')