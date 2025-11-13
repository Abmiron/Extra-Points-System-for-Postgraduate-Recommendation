from app import app, db
from models import User

with app.app_context():
    # 查询所有用户
    users = User.query.all()
    if users:
        print("数据库中的用户列表:")
        for user in users:
            print(f"ID: {user.id}, 用户名: {user.username}, 角色: {user.role}, 状态: {user.status}, 姓名: {user.name}")
    else:
        print("数据库中没有用户")