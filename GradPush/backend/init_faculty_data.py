# -*- coding: utf-8 -*-
"""
学院、系和专业数据初始化脚本

该脚本负责向数据库中添加初始的学院、系和专业数据，
为系统提供基础的组织架构信息。
"""

from app import app
from models import Faculty, Department, Major, db

# 初始数据
initial_data = [
    {
        "faculty_name": "信息学院",
        "faculty_description": "信息学院是学校的主要学院之一，负责计算机科学与技术、软件工程等专业的教学和研究。",
        "departments": [
            {
                "department_name": "计算机科学与技术系",
                "department_description": "计算机科学与技术系是信息学院的核心系之一，培养计算机领域的高级人才。",
                "majors": [
                    {
                        "major_name": "计算机科学与技术",
                        "major_description": "本专业培养具有良好科学素养，系统地、较好地掌握计算机科学与技术包括计算机硬件、软件与应用的基本理论、基本知识和基本技能与方法的高级专门科学技术人才。"
                    },
                    {
                        "major_name": "人工智能",
                        "major_description": "本专业培养掌握人工智能基础理论、机器学习、深度学习等核心技术，能够在人工智能领域从事研究、开发和应用的高级专门人才。"
                    }
                ]
            },
            {
                "department_name": "软件工程系",
                "department_description": "软件工程系专注于软件工程领域的教学和研究，培养软件工程高级人才。",
                "majors": [
                    {
                        "major_name": "软件工程",
                        "major_description": "本专业培养具有良好的综合素质、良好的职业道德、扎实的软件理论和软件工程专业基础知识，并且具有良好的软件设计与实现能力、项目管理能力和交流与组织协调能力的高级软件工程专门人才。"
                    }
                ]
            }
        ]
    },
    {
        "faculty_name": "数学科学学院",
        "faculty_description": "数学科学学院是学校的基础学科学院，负责数学、统计学等专业的教学和研究。",
        "departments": [
            {
                "department_name": "数学系",
                "department_description": "数学系是数学科学学院的核心系之一，培养数学领域的高级人才。",
                "majors": [
                    {
                        "major_name": "数学与应用数学",
                        "major_description": "本专业培养掌握数学科学的基本理论与基本方法，具备运用数学知识、使用计算机解决实际问题的能力，受到科学研究的初步训练，能在科技、教育和经济部门从事研究、教学工作或在生产经营及管理部门从事实际应用、开发研究和管理工作的高级专门人才。"
                    },
                    {
                        "major_name": "信息与计算科学",
                        "major_description": "本专业培养具有良好的数学基础和数学思维能力，掌握信息科学与计算科学的基本理论、方法和技能，受到科学研究的初步训练，能运用所学知识和熟练的计算机技能解决实际问题，能在科技、教育和经济部门从事研究、教学和应用开发及管理工作的高级专门人才。"
                    }
                ]
            }
        ]
    },
    {
        "faculty_name": "物理科学与技术学院",
        "faculty_description": "物理科学与技术学院是学校的基础学科学院，负责物理学、天文学等专业的教学和研究。",
        "departments": [
            {
                "department_name": "物理系",
                "department_description": "物理系是物理科学与技术学院的核心系之一，培养物理学领域的高级人才。",
                "majors": [
                    {
                        "major_name": "物理学",
                        "major_description": "本专业培养掌握物理学的基本理论与方法，具有良好的数学基础和实验技能，能在物理学或相关的科学技术领域中从事科研、教学、技术和相关的管理工作的高级专门人才。"
                    }
                ]
            }
        ]
    }
]

# 初始化数据
def init_data():
    with app.app_context():
        # 检查是否已有数据
        if Faculty.query.first():
            print("数据库中已有学院数据，跳过初始化")
            return
        
        print("开始初始化学院、系和专业数据...")
        
        # 遍历初始数据，添加到数据库
        for faculty_data in initial_data:
            # 创建学院
            faculty = Faculty(
                name=faculty_data["faculty_name"],
                description=faculty_data["faculty_description"]
            )
            db.session.add(faculty)
            db.session.flush()  # 获取学院ID
            
            print(f"添加学院: {faculty.name}")
            
            # 创建系
            for dept_data in faculty_data["departments"]:
                department = Department(
                    name=dept_data["department_name"],
                    faculty_id=faculty.id,
                    description=dept_data["department_description"]
                )
                db.session.add(department)
                db.session.flush()  # 获取系ID
                
                print(f"  - 添加系: {department.name}")
                
                # 创建专业
                for major_data in dept_data["majors"]:
                    major = Major(
                        name=major_data["major_name"],
                        department_id=department.id,
                        description=major_data["major_description"]
                    )
                    db.session.add(major)
                    
                    print(f"    - 添加专业: {major.name}")
        
        # 提交事务
        db.session.commit()
        print("数据初始化完成！")

if __name__ == "__main__":
    init_data()