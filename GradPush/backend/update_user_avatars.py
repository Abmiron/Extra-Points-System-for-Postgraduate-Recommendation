from app import app, db
from models import User

with app.app_context():
    try:
        # 更新所有使用旧头像路径的用户
        updated_count = User.query.filter(
            User.avatar.in_(['/images/头像1.jpg', '/images/头像2.jpg'])
        ).update({
            User.avatar: '/images/default-avatar.jpg'
        }, synchronize_session=False)
        
        db.session.commit()
        print(f"成功更新了 {updated_count} 个用户的头像路径")
        
        # 验证更新结果
        users_with_old_avatars = User.query.filter(
            User.avatar.in_(['/images/头像1.jpg', '/images/头像2.jpg'])
        ).count()
        print(f"仍有 {users_with_old_avatars} 个用户使用旧头像路径")
        
    except Exception as e:
        db.session.rollback()
        print(f"更新失败: {e}")