# -*- coding: utf-8 -*-
"""
生成测试数据的脚本
"""

from app import app
from extensions import db
from models import *  # 导入所有模型
from datetime import datetime, date
import random

print("正在生成测试数据...")

with app.app_context():
    try:
        # 创建学院数据
        faculties = []
        faculty_names = ["计算机科学与技术学院", "电子工程学院", "机械工程学院", "经济管理学院", "外国语学院"]
        for name in faculty_names:
            faculty = Faculty(name=name)
            faculties.append(faculty)
            db.session.add(faculty)
        db.session.commit()
        print(f"创建了 {len(faculties)} 个学院")

        # 创建系数据
        departments = []
        department_data = [
            (0, "计算机科学系"), (0, "软件工程系"), (0, "网络工程系"),  # 计算机科学与技术学院
            (1, "电子信息工程系"), (1, "通信工程系"),  # 电子工程学院
            (2, "机械设计制造系"), (2, "自动化系"),  # 机械工程学院
            (3, "工商管理系"), (3, "经济学系"),  # 经济管理学院
            (4, "英语系"), (4, "日语系")  # 外国语学院
        ]
        for faculty_index, name in department_data:
            faculty = faculties[faculty_index]  # 获取实际的学院对象
            department = Department(name=name, faculty_id=faculty.id)
            departments.append(department)
            db.session.add(department)
        db.session.commit()
        print(f"创建了 {len(departments)} 个系")

        # 创建专业数据
        majors = []
        major_data = [
            (0, "计算机科学与技术"), (0, "数据科学与大数据技术"),  # 计算机科学系
            (1, "软件工程"), (1, "人工智能"),  # 软件工程系
            (2, "网络工程"), (2, "信息安全"),  # 网络工程系
            (3, "电子信息工程"), (3, "电子科学与技术"),  # 电子信息工程系
            (4, "通信工程"), (4, "物联网工程"),  # 通信工程系
            (5, "机械设计制造及其自动化"), (5, "智能制造工程"),  # 机械设计制造系
            (6, "自动化"), (6, "机器人工程"),  # 自动化系
            (7, "工商管理"), (7, "市场营销"),  # 工商管理系
            (8, "经济学"), (8, "金融学"),  # 经济学系
            (9, "英语"), (9, "翻译"),  # 英语系
            (10, "日语"), (10, "朝鲜语")  # 日语系
        ]
        for department_index, name in major_data:
            department = departments[department_index]  # 获取实际的系对象
            major = Major(name=name, department_id=department.id)
            majors.append(major)
            db.session.add(major)
        db.session.commit()
        print(f"创建了 {len(majors)} 个专业")

        # 创建用户数据
        users = []
        
        # 管理员用户
        admin = User(
            username="admin",
            name="管理员",
            password="123456",  # 实际应用中应使用哈希密码
            role="admin",
            email="admin@example.com"
        )
        users.append(admin)
        db.session.add(admin)
        
        # 教师用户
        for i in range(1, 6):
            dept_index = random.randint(0, len(departments) - 1)
            department = departments[dept_index]
            faculty = faculties[dept_index // 3]  # 根据系索引计算学院索引（每3个系属于一个学院）
            
            teacher = User(
                username=f"teacher{i}",
                name=f"教师{i}",
                password="123456",
                role="teacher",
                email=f"teacher{i}@example.com",
                faculty_id=faculty.id,
                department_id=department.id
            )
            users.append(teacher)
            db.session.add(teacher)
        
        db.session.commit()
        print(f"创建了 {len(users)} 个用户（管理员和教师）")

        # 创建学生数据（先创建Student模型数据）
        students = []
        for i in range(1, 21):
            # 随机选择一个专业
            major_index = random.randint(0, len(majors) - 1)
            major = majors[major_index]
            department_index = major_index // 2  # 每两个专业属于一个系
            department = departments[department_index]
            faculty_index = major_index // 6  # 每6个专业属于一个学院
            faculty = faculties[faculty_index]
            
            student = Student(
                student_id=f"student{i}",
                student_name=f"学生{i}",  # 注意：Student模型中是student_name，不是name
                gender="男" if i % 2 == 0 else "女",
                faculty_id=faculty.id,
                department_id=department.id,
                major_id=major.id,
                cet4_score=random.randint(425, 600),
                cet6_score=random.randint(425, 600) if i % 3 != 0 else None,
                gpa=round(random.uniform(3.0, 4.0), 2),
                academic_score=round(random.uniform(80, 95), 2),
                academic_weighted=round(random.uniform(75, 92), 2),
                academic_specialty_total=round(random.uniform(0, 10), 2),
                comprehensive_performance_total=round(random.uniform(0, 10), 2),
                total_score=round(random.uniform(85, 100), 2),
                comprehensive_score=round(random.uniform(80, 95), 2),
                major_ranking=random.randint(1, 50),
                total_students=50
            )
            students.append(student)
            db.session.add(student)
        db.session.commit()
        print(f"创建了 {len(students)} 个学生（Student模型）")
        
        # 基于Student模型数据创建对应的User模型学生用户
        for student in students:
            user_student = User(
                username=student.student_id,  # 使用学生学号作为用户名
                name=student.student_name,  # 使用学生姓名
                password="123456",  # 初始密码
                role="student",
                email=f"{student.student_id}@example.com",  # 邮箱使用学号
                student_id=student.student_id,  # 关联学生学号
                faculty_id=student.faculty_id,  # 与Student模型一致的学院ID
                department_id=student.department_id,  # 与Student模型一致的系ID
                major_id=student.major_id  # 与Student模型一致的专业ID
            )
            users.append(user_student)
            db.session.add(user_student)
        
        db.session.commit()
        print(f"创建了 {len(students)} 个学生用户（User模型），总用户数：{len(users)}")

        # 创建规则数据
        rules = []
        rule_data = [
            ("academic", "学术论文", "国家级", "核心期刊", 5.0, 1, 100, False),
            ("academic", "学术论文", "省级", "普通期刊", 3.0, 1, 100, False),
            ("academic", "科研项目", "国家级", "参与", 8.0, 1, 100, False),
            ("academic", "科研项目", "省级", "参与", 5.0, 1, 100, False),
            ("academic", "竞赛获奖", "国家级", "一等奖", 10.0, 1, 100, False),
            ("academic", "竞赛获奖", "国家级", "二等奖", 8.0, 1, 100, False),
            ("academic", "竞赛获奖", "省级", "一等奖", 6.0, 1, 100, False),
            ("comprehensive", "社会实践", "国家级", "优秀团队", 3.0, 1, 100, False),
            ("comprehensive", "社会实践", "省级", "优秀团队", 2.0, 1, 100, False),
            ("comprehensive", "学生干部", "校级", "学生会主席", 4.0, 1, 100, False),
            ("comprehensive", "学生干部", "院级", "学生会主席", 2.0, 1, 100, False),
            ("comprehensive", "荣誉称号", "国家级", "优秀学生", 5.0, 1, 100, False),
            ("comprehensive", "荣誉称号", "省级", "优秀学生", 3.0, 1, 100, False),
            ("comprehensive", "荣誉称号", "校级", "优秀学生", 1.0, 1, 100, False)
        ]
        for rule_type, name, level, research_type, max_score, max_count, author_rank_ratio, is_special in rule_data:
            rule = Rule(
                name=name,
                type=rule_type,
                level=level,
                research_type=research_type,
                score=max_score,  # 设置score字段（必填）
                max_score=max_score,
                max_count=max_count,
                author_rank_ratio=author_rank_ratio,
                is_special=is_special
            )
            rules.append(rule)
            db.session.add(rule)
        db.session.commit()
        print(f"创建了 {len(rules)} 个规则")

        # 创建申请数据
        applications = []
        for i in range(1, 31):
            student_id = f"student{random.randint(1, 20)}"
            rule = random.choice(rules)  # 直接从已创建的规则列表中随机选择
            
            # 随机选择一个专业，并根据专业获取对应的系和学院
            major_index = random.randint(0, len(majors) - 1)
            major = majors[major_index]
            department_index = major_index // 2  # 每两个专业属于一个系
            department = departments[department_index]
            faculty_index = major_index // 6  # 每6个专业属于一个学院
            faculty = faculties[faculty_index]
            
            application = Application(
                student_id=student_id,
                student_name=f"学生{student_id[-2:]}",
                application_type=rule.type,
                project_name=f"{rule.name}项目{i}",
                award_date=date(2024, random.randint(1, 12), random.randint(1, 28)),
                award_level=rule.level,
                award_type="个人" if random.randint(1, 2) == 1 else "集体",
                author_order=random.randint(1, 5) if rule.type == "academic" else None,
                self_score=round(random.uniform(0, rule.max_score), 2),
                rule_id=rule.id,
                status=random.choice(["pending", "approved", "rejected"]),
                faculty_id=faculty.id,
                department_id=department.id,
                major_id=major.id
            )
            
            # 如果申请状态是approved，设置final_score
            if application.status == "approved":
                application.final_score = application.self_score
            
            applications.append(application)
            db.session.add(application)
        db.session.commit()
        print(f"创建了 {len(applications)} 个申请")

        # 创建绩效详情数据
        performance_details = []
        for i in range(1, 51):
            student_id = f"student{random.randint(1, 20)}"
            rule = random.choice(rules)  # 直接从已创建的规则列表中随机选择
            
            detail = PerformanceDetail(
                student_id=student_id,
                rule_id=rule.id,
                type=rule.type,
                project_name=f"{rule.type}绩效项目{i}",
                award_date=date(2024, random.randint(1, 12), random.randint(1, 28)),
                award_level=rule.level,
                award_type="个人" if random.randint(1, 2) == 1 else "集体",
                author_order=random.randint(1, 5) if rule.type == "academic" else None,
                self_score=round(random.uniform(0, rule.max_score), 2),
                score_basis=f"基于{rule.name}规则",
                approved_score=round(random.uniform(0, rule.max_score), 2) if random.randint(1, 2) == 1 else None
            )
            performance_details.append(detail)
            db.session.add(detail)
        db.session.commit()
        print(f"创建了 {len(performance_details)} 个绩效详情")

        print("\n所有测试数据生成完成！")
        print(f"- 学院: {len(faculties)} 个")
        print(f"- 系: {len(departments)} 个")
        print(f"- 专业: {len(majors)} 个")
        print(f"- 用户: {len(users)} 个 (1个管理员, 5个教师, 15个学生)")
        print(f"- 学生: {len(students)} 个")
        print(f"- 规则: {len(rules)} 个")
        print(f"- 申请: {len(applications)} 个")
        print(f"- 绩效详情: {len(performance_details)} 个")
        
    except Exception as e:
        db.session.rollback()
        print(f"生成测试数据时发生错误：{str(e)}")
        import traceback
        traceback.print_exc()