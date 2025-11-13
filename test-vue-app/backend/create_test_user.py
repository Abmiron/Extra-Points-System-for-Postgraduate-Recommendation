from app import app, db
from models import User

with app.app_context():
    # 创建测试学生用户
    user = User(
        username='test_student',
        password='123456',
        name='测试学生',
        role='student',
        student_id='20210001',
        faculty='计算机学院',
        department='计算机科学与技术系',
        major='计算机科学与技术',
        email='test@example.com',
        phone='13800138000',
        role_name='学生'
    )
    db.session.add(user)
    
    # 创建测试教师用户
    teacher = User(
        username='test_teacher',
        password='123456',
        name='测试教师',
        role='teacher',
        faculty='计算机学院',
        department='计算机科学与技术系',
        email='teacher@example.com',
        phone='13900139000',
        role_name='教师'
    )
    db.session.add(teacher)
    
    # 创建测试管理员用户
    admin = User(
        username='test_admin',
        password='123456',
        name='测试管理员',
        role='admin',
        email='admin@example.com',
        phone='13700137000',
        role_name='管理员'
    )
    db.session.add(admin)
    
    db.session.commit()
    print('测试用户创建成功！')