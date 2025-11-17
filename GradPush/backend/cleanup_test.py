#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理脚本：删除测试用户记录
"""

from extensions import db
from models import User, Student
from app import app

with app.app_context():
    print("清理测试数据...")
    
    # 删除测试用户
    user = User.query.filter_by(username='teststudent001').first()
    if user:
        db.session.delete(user)
        db.session.commit()
        print(f"已删除用户: {user.username}")
    else:
        print("未找到测试用户")
    
    # 检查并删除测试学生记录（如果存在）
    student = Student.query.filter_by(student_id='teststudent001').first()
    if student:
        db.session.delete(student)
        db.session.commit()
        print(f"已删除学生: {student.student_id}")
    else:
        print("未找到测试学生记录")