# -*- coding: utf-8 -*-
"""
学院、系和专业数据初始化脚本（新）

该脚本负责向数据库中添加用户指定的学院、系和专业数据：
1. 电子科学与技术学院
2. 航空航天学院
3. 信息学院
"""

from app import app
from models import Faculty, Department, Major, db

# 用户指定的初始数据
initial_data = [
    {
        "faculty_name": "电子科学与技术学院",
        "faculty_description": "电子科学与技术学院致力于培养电子信息领域的高级工程技术人才，涵盖电子工程、微电子、电子科学等多个方向。",
        "departments": [
            {
                "department_name": "电子工程系",
                "department_description": "电子工程系专注于电子信息工程领域的教学与研究，培养具备电子系统设计和开发能力的专业人才。",
                "majors": [
                    {
                        "major_name": "电子信息工程",
                        "major_description": "本专业培养掌握电子信息系统基本理论和技术，能够从事电子设备、通信系统设计与开发的高级工程技术人才。"
                    }
                ]
            },
            {
                "department_name": "微电子与集成电路系",
                "department_description": "微电子与集成电路系专注于集成电路设计和微电子技术领域，培养芯片设计与制造方面的专业人才。",
                "majors": [
                    {
                        "major_name": "集成电路设计与集成系统",
                        "major_description": "本专业培养掌握集成电路设计基本理论和方法，能够从事集成电路设计、验证和测试的高级工程技术人才。"
                    },
                    {
                        "major_name": "微电子科学与工程",
                        "major_description": "本专业培养掌握微电子技术基本理论和工艺，能够从事微电子器件、集成电路制造的高级工程技术人才。"
                    }
                ]
            },
            {
                "department_name": "电子科学系",
                "department_description": "电子科学系专注于电子科学基础理论和应用技术的研究，培养电子科学领域的专业人才。",
                "majors": [
                    {
                        "major_name": "电子信息科学与技术",
                        "major_description": "本专业培养掌握电子信息科学与技术基本理论，能够从事电子信息系统研究与开发的高级专门人才。"
                    },
                    {
                        "major_name": "电磁场与无线技术",
                        "major_description": "本专业培养掌握电磁场与无线技术基本理论，能够从事无线通信、微波工程等领域的高级工程技术人才。"
                    }
                ]
            }
        ]
    },
    {
        "faculty_name": "航空航天学院",
        "faculty_description": "航空航天学院致力于培养航空航天领域的高级工程技术人才，涵盖仪器电气、机电工程、动力工程、飞行器设计和自动化等多个方向。",
        "departments": [
            {
                "department_name": "仪器与电气系",
                "department_description": "仪器与电气系专注于电气工程和测控技术领域，培养电气和测控方面的专业人才。",
                "majors": [
                    {
                        "major_name": "电气工程及其自动化",
                        "major_description": "本专业培养掌握电气工程基本理论和技术，能够从事电气系统设计、运行和控制的高级工程技术人才。"
                    },
                    {
                        "major_name": "测控技术与仪器",
                        "major_description": "本专业培养掌握测控技术与仪器基本理论，能够从事测量控制、仪器仪表设计的高级工程技术人才。"
                    }
                ]
            },
            {
                "department_name": "机电工程系",
                "department_description": "机电工程系专注于机械设计制造及其自动化领域，培养机械工程方面的专业人才。",
                "majors": [
                    {
                        "major_name": "机械设计制造及其自动化",
                        "major_description": "本专业培养掌握机械设计制造基本理论和技术，能够从事机械产品设计、制造和管理的高级工程技术人才。"
                    }
                ]
            },
            {
                "department_name": "动力工程系",
                "department_description": "动力工程系专注于飞行器动力工程领域，培养航空航天动力系统方面的专业人才。",
                "majors": [
                    {
                        "major_name": "飞行器动力工程",
                        "major_description": "本专业培养掌握飞行器动力系统基本理论和技术，能够从事航空发动机、火箭发动机设计与研究的高级工程技术人才。"
                    }
                ]
            },
            {
                "department_name": "飞行器系",
                "department_description": "飞行器系专注于飞行器设计与工程领域，培养飞行器总体设计方面的专业人才。",
                "majors": [
                    {
                        "major_name": "飞行器设计与工程",
                        "major_description": "本专业培养掌握飞行器设计基本理论和技术，能够从事飞行器总体设计、结构设计的高级工程技术人才。"
                    }
                ]
            },
            {
                "department_name": "自动化系",
                "department_description": "自动化系专注于自动化领域，培养自动化控制系统方面的专业人才。",
                "majors": [
                    {
                        "major_name": "自动化",
                        "major_description": "本专业培养掌握自动化控制基本理论和技术，能够从事自动化系统设计、运行和管理的高级工程技术人才。"
                    }
                ]
            }
        ]
    },
    {
        "faculty_name": "信息学院",
        "faculty_description": "信息学院致力于培养计算机与信息技术领域的高级专业人才，涵盖人工智能、计算机科学、软件工程等多个方向。",
        "departments": [
            {
                "department_name": "人工智能系",
                "department_description": "人工智能系专注于人工智能领域的教学与研究，培养人工智能算法与应用方面的专业人才。",
                "majors": [
                    {
                        "major_name": "人工智能",
                        "major_description": "本专业培养掌握人工智能基本理论和技术，能够从事机器学习、深度学习等领域研究与应用的高级专门人才。"
                    },
                    {
                        "major_name": "智能科学与技术",
                        "major_description": "本专业培养掌握智能科学与技术基本理论，能够从事智能系统设计与开发的高级专门人才。"
                    }
                ]
            },
            {
                "department_name": "计算机科学与技术系",
                "department_description": "计算机科学与技术系专注于计算机科学与技术领域的教学与研究，培养计算机系统与网络方面的专业人才。",
                "majors": [
                    {
                        "major_name": "计算机科学与技术",
                        "major_description": "本专业培养掌握计算机科学与技术基本理论，能够从事计算机系统设计、软件开发的高级专门人才。"
                    },
                    {
                        "major_name": "网络空间安全",
                        "major_description": "本专业培养掌握网络空间安全基本理论和技术，能够从事网络安全防护、信息安全管理的高级专门人才。"
                    }
                ]
            },
            {
                "department_name": "软件工程系",
                "department_description": "软件工程系专注于软件工程领域的教学与研究，培养软件设计与开发方面的专业人才。",
                "majors": [
                    {
                        "major_name": "软件工程",
                        "major_description": "本专业培养掌握软件工程基本理论和方法，能够从事软件系统设计、开发和管理的高级工程技术人才。"
                    },
                    {
                        "major_name": "数字媒体技术",
                        "major_description": "本专业培养掌握数字媒体技术基本理论，能够从事数字媒体设计、开发的高级专门人才。"
                    },
                    {
                        "major_name": "数据科学与大数据技术",
                        "major_description": "本专业培养掌握数据科学与大数据技术基本理论，能够从事大数据分析、处理和应用的高级专门人才。"
                    }
                ]
            }
        ]
    }
]

# 初始化数据
def init_data():
    with app.app_context():
        # 直接添加数据，不检查是否已有数据（因为已经清空了数据库）
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