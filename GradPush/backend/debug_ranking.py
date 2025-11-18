from app import app
from models import db, Student, Application

with app.app_context():
    # 检查Student表中的学生记录
    print("=== Student表中的学生记录 ===")
    students = Student.query.all()
    print(f"总共有 {len(students)} 个学生记录")
    for student in students:
        print(f"ID: {student.id}, 学号: {student.student_id}, 姓名: {student.student_name}, 学院ID: {student.faculty_id}")
    
    # 检查Application表中的申请记录
    print("\n=== Application表中的申请记录 ===")
    applications = Application.query.all()
    print(f"总共有 {len(applications)} 个申请记录")
    for app in applications:
        print(f"ID: {app.id}, 学生ID: {app.student_id}, 类型: {app.application_type}, 状态: {app.status}, 项目名称: {app.project_name}")
    
    # 检查特定学生的申请记录
    print("\n=== 按学生匹配申请记录 ===")
    for student in students:
        print(f"\n学生 {student.student_name} ({student.student_id}) 的申请记录:")
        # 用学生学号查询申请记录
        student_apps = Application.query.filter_by(student_id=str(student.student_id)).all()
        print(f"  找到 {len(student_apps)} 个申请记录")
        for app in student_apps:
            print(f"  - 类型: {app.application_type}, 状态: {app.status}, 项目名称: {app.project_name}")
        
        # 测试查询条件
        print("  测试学术专长查询条件:")
        academic_query = Application.query.filter_by(student_id=str(student.student_id)).filter(
            (Application.application_type.in_(['research', 'competition', 'innovation'])) | 
            (Application.application_type == 'academic')
        )
        print(f"  - 学术专长记录数: {academic_query.count()}")
        
        print("  测试综合表现查询条件:")
        comprehensive_query = Application.query.filter_by(student_id=str(student.student_id)).filter(
            (Application.application_type.in_(['international_internship', 'military_service', 'volunteer', 'social_work', 'sports', 'honor_title'])) | 
            (Application.application_type == 'comprehensive')
        )
        print(f"  - 综合表现记录数: {comprehensive_query.count()}")
        
        # 检查申请状态
        print("  测试已批准的申请:")
        approved_query = Application.query.filter_by(student_id=str(student.student_id), status='approved')
        print(f"  - 已批准记录数: {approved_query.count()}")