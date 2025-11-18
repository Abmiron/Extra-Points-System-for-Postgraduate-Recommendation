from app import app
from models import db, Student, Application

with app.app_context():
    # 模拟API的主要查询逻辑
    print("=== 模拟API的主要查询逻辑 ===")
    
    # 1. 获取所有学生
    students = Student.query.all()
    print(f"获取到 {len(students)} 个学生")
    
    # 2. 构建学生统计数据
    student_stats = {}
    for student in students:
        student_id = student.id
        student_stats[student_id] = {
            'student_id': student.student_id,
            'student_name': student.student_name,
            'departmentId': student.department_id,
            'department': student.department.name if student.department else '未知系别',
            'majorId': student.major_id,
            'major': student.major.name if student.major else '未知专业',
            'facultyId': student.faculty_id,
            'faculty': student.faculty.name if student.faculty else '未知学院',
            'specialty_score': 0.0,
            'comprehensive_score': 0.0,
            'academic_items': [],
            'comprehensive_items': []
        }
    
    # 3. 模拟获取学术专长和综合表现详情
    print("\n=== 模拟获取学术专长和综合表现详情 ===")
    for student_id in student_stats:
        student_data = student_stats[student_id]
        student_number = student_data['student_id']
        student_number_str = str(student_number)
        
        print(f"\n处理学生 {student_data['student_name']} (学号: {student_number_str})")
        
        # 测试学术专长查询
        print("  学术专长查询:")
        academic_query = Application.query.filter_by(student_id=student_number_str, status='approved').filter(
            (Application.application_type.in_(['research', 'competition', 'innovation'])) | 
            (Application.application_type == 'academic')
        )
        academic_details = academic_query.all()
        print(f"  - 查询条件: student_id={student_number_str}, status=approved, type in ['research', 'competition', 'innovation'] or 'academic'")
        print(f"  - 找到 {len(academic_details)} 个记录")
        for detail in academic_details:
            print(f"    * 类型: {detail.application_type}, 项目名称: {detail.project_name}")
        
        # 测试综合表现查询
        print("\n  综合表现查询:")
        comprehensive_query = Application.query.filter_by(student_id=student_number_str, status='approved').filter(
            (Application.application_type.in_(['international_internship', 'military_service', 'volunteer', 'social_work', 'sports', 'honor_title'])) | 
            (Application.application_type == 'comprehensive')
        )
        comprehensive_details = comprehensive_query.all()
        print(f"  - 查询条件: student_id={student_number_str}, status=approved, type in ['international_internship', 'military_service', 'volunteer', 'social_work', 'sports', 'honor_title'] or 'comprehensive'")
        print(f"  - 找到 {len(comprehensive_details)} 个记录")
        for detail in comprehensive_details:
            print(f"    * 类型: {detail.application_type}, 项目名称: {detail.project_name}")
        
        # 模拟添加到统计数据
        academic_items = []
        for detail in academic_details:
            academic_items.append({
                'project_name': detail.project_name,
                'award_time': detail.award_date.strftime('%Y-%m-%d') if detail.award_date else '',
                'award_level': detail.award_level,
                'individual_collective': detail.award_type,
                'author_order': detail.author_order,
                'self_eval_score': detail.self_score,
                'score_basis': '',
                'college_approved_score': detail.final_score,
                'total_score': detail.final_score or 0.0
            })
        
        comprehensive_items = []
        for detail in comprehensive_details:
            comprehensive_items.append({
                'project_name': detail.project_name,
                'award_time': detail.award_date.strftime('%Y-%m-%d') if detail.award_date else '',
                'award_level': detail.award_level,
                'individual_collective': detail.award_type,
                'author_order': detail.author_order,
                'self_eval_score': detail.self_score,
                'score_basis': '',
                'college_approved_score': detail.final_score,
                'total_score': detail.final_score or 0.0
            })
        
        student_data['academic_items'] = academic_items
        student_data['comprehensive_items'] = comprehensive_items
        
        print(f"\n  添加到统计数据后:")
        print(f"  - 学术专长项目数: {len(student_data['academic_items'])}")
        print(f"  - 综合表现项目数: {len(student_data['comprehensive_items'])}")
    
    # 4. 打印最终的统计数据
    print("\n=== 最终统计数据 ===")
    for student_id, student_data in student_stats.items():
        print(f"\n学生 {student_data['student_name']} (学号: {student_data['student_id']})")
        print(f"  - 学术专长项目数: {len(student_data['academic_items'])}")
        for item in student_data['academic_items']:
            print(f"    * 项目名称: {item['project_name']}")
        print(f"  - 综合表现项目数: {len(student_data['comprehensive_items'])}")
        for item in student_data['comprehensive_items']:
            print(f"    * 项目名称: {item['project_name']}")