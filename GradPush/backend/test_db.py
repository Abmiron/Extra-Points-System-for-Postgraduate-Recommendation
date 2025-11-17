# -*- coding: utf-8 -*-
"""
数据库连接和权限测试脚本
"""

from extensions import db
from models import User, Student, Faculty, Department, Major
from app import app

def test_db_connection():
    """测试数据库连接是否正常"""
    try:
        with app.app_context():
            # 尝试获取数据库连接
            conn = db.engine.connect()
            print("✓ 数据库连接成功")
            conn.close()
            return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False

def test_user_permissions():
    """测试用户权限是否足够执行INSERT操作"""
    try:
        with app.app_context():
            # 测试创建一个临时的Faculty记录
            faculty = Faculty(name="测试学院", description="用于测试的学院")
            db.session.add(faculty)
            db.session.commit()
            print("✓ INSERT操作权限测试成功")
            
            # 清理测试数据
            db.session.delete(faculty)
            db.session.commit()
            return True
    except Exception as e:
        print(f"✗ INSERT操作权限测试失败: {e}")
        return False

def test_student_insert():
    """测试Student表的INSERT操作是否正常"""
    try:
        with app.app_context():
            # 先创建必要的关联记录
            faculty = Faculty(name="测试学院", description="用于测试的学院")
            db.session.add(faculty)
            db.session.commit()
            
            department = Department(name="测试系", faculty_id=faculty.id, description="用于测试的系")
            db.session.add(department)
            db.session.commit()
            
            major = Major(name="测试专业", department_id=department.id, description="用于测试的专业")
            db.session.add(major)
            db.session.commit()
            
            # 测试创建Student记录
            student = Student(
                student_id="test123",
                student_name="测试学生",
                faculty_id=faculty.id,
                department_id=department.id,
                major_id=major.id
            )
            db.session.add(student)
            db.session.commit()
            print("✓ Student表INSERT操作测试成功")
            
            # 清理测试数据
            db.session.delete(student)
            db.session.delete(major)
            db.session.delete(department)
            db.session.delete(faculty)
            db.session.commit()
            return True
    except Exception as e:
        print(f"✗ Student表INSERT操作测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试数据库连接和权限...")
    print("=" * 50)
    
    test_db_connection()
    print()
    
    test_user_permissions()
    print()
    
    test_student_insert()
    print()
    
    print("测试完成！")