from app import app
from models import Application, db

with app.app_context():
    # 查询所有已通过的申请
    approved_applications = Application.query.filter_by(status='approved').all()
    
    print(f"已通过的申请数量: {len(approved_applications)}")
    
    for app in approved_applications:
        print(f"\n申请ID: {app.id}")
        print(f"学生ID: {app.student_id}")
        print(f"学生姓名: {app.student_name}")
        print(f"申请类型: {app.application_type}")
        print(f"项目名称: {app.project_name}")
        print(f"状态: {app.status}")
        print(f"最终分数: {app.final_score}")
        print(f"学术类型: {app.academic_type}")
        print(f"表现类型: {app.performance_type}")