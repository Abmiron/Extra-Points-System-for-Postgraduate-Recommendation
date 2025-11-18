from app import app
from models import db, Application

with app.app_context():
    # 查询所有申请记录
    all_applications = Application.query.all()
    print(f"总共有 {len(all_applications)} 条申请记录")
    
    # 打印每条记录的关键信息
    for app in all_applications:
        print(f"学生ID: {app.student_id}, 类型: {app.application_type}, 状态: {app.status}, 得分: {app.final_score}, 标题: {app.title if hasattr(app, 'title') else app.project_name}")
    
    # 检查学术专长类型记录
    academic_apps = Application.query.filter(Application.application_type.in_(['research', 'competition', 'innovation', 'academic'])).all()
    print(f"\n学术专长类型记录数量: {len(academic_apps)}")
    
    # 检查综合表现类型记录
    comprehensive_apps = Application.query.filter(Application.application_type.in_(['international_internship', 'military_service', 'volunteer', 'social_work', 'sports', 'honor_title', 'comprehensive'])).all()
    print(f"综合表现类型记录数量: {len(comprehensive_apps)}")