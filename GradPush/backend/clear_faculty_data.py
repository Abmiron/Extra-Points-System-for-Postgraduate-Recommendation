# -*- coding: utf-8 -*-
"""
清空学院、系和专业数据脚本

该脚本用于清空数据库中的学院、系和专业数据，按照外键关系的逆序删除：
1. 先删除专业(Major)数据
2. 然后删除系(Department)数据
3. 最后删除学院(Faculty)数据
"""

from app import app
from models import db, Faculty, Department, Major

def clear_faculty_data():
    """清空学院、系和专业数据"""
    with app.app_context():
        try:
            # 1. 删除专业数据
            major_count = db.session.query(Major).delete()
            db.session.commit()
            print(f"已删除 {major_count} 条专业数据")
            
            # 2. 删除系数据
            department_count = db.session.query(Department).delete()
            db.session.commit()
            print(f"已删除 {department_count} 条系数据")
            
            # 3. 删除学院数据
            faculty_count = db.session.query(Faculty).delete()
            db.session.commit()
            print(f"已删除 {faculty_count} 条学院数据")
            
            print("\n✅ 学院、系和专业数据已全部清空！")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 清空数据时发生错误: {str(e)}")

if __name__ == "__main__":
    print("开始清空学院、系和专业数据...")
    clear_faculty_data()