from app import app, db
from models import Student, Application

with app.app_context():
    # 检查Student模型的字段
    print('Student模型字段:', [c.name for c in Student.__table__.columns])
    
    # 检查Application模型的字段
    print('\nApplication模型字段:', [c.name for c in Application.__table__.columns])
    
    # 获取一个学生示例
    student = Student.query.first()
    if student:
        print('\n学生示例:', student.student_id)
        
        # 尝试模拟get_students_ranking函数中的查询
        try:
            # 检查academic_items查询
            academic_types = ['research', 'competition', 'innovation']
            academic_items = Application.query.filter(
                Application.student_number_str == student.student_id,
                Application.type.in_(academic_types)
            ).all()
            print('\n学术专长项目数量:', len(academic_items))
            for item in academic_items:
                print(f'  项目: {item.title}, 类型: {item.type}, 获奖时间: {item.award_date}')
        except Exception as e:
            print('\n学术专长查询出错:', str(e))
            import traceback
            traceback.print_exc()
            
        try:
            # 检查comprehensive_items查询
            comprehensive_types = ['international_internship', 'military_service', 'volunteer', 'social_work', 'sports', 'honor_title']
            comprehensive_items = Application.query.filter(
                Application.student_number_str == student.student_id,
                Application.type.in_(comprehensive_types)
            ).all()
            print('\n综合表现项目数量:', len(comprehensive_items))
            for item in comprehensive_items:
                print(f'  项目: {item.title}, 类型: {item.type}, 获奖时间: {item.award_date}')
        except Exception as e:
            print('\n综合表现查询出错:', str(e))
            import traceback
            traceback.print_exc()

    # 检查是否有任何与performance_detail相关的外键约束
    print('\n检查Student模型的外键约束:')
    for constraint in Student.__table__.foreign_keys:
        print(f'  外键: {constraint}')
        print(f'    目标表: {constraint.column.table.name}')
        print(f'    目标列: {constraint.column.name}')
    
    print('\n检查Application模型的外键约束:')
    for constraint in Application.__table__.foreign_keys:
        print(f'  外键: {constraint}')
        print(f'    目标表: {constraint.column.table.name}')
        print(f'    目标列: {constraint.column.name}')