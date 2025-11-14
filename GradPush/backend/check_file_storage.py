# -*- coding: utf-8 -*-
"""
检查文件存储情况

该脚本用于检查数据库中的申请记录和上传的文件，验证文件存储和路径是否正确。
"""

from app import app, db
from models import Application
import os

if __name__ == '__main__':
    print("=== 检查文件存储情况 ===")
    
    with app.app_context():
        # 获取uploads目录路径
        uploads_dir = app.config['UPLOAD_FOLDER']
        print(f"uploads目录: {uploads_dir}")
        
        # 检查uploads目录中的文件
        print(f"\n=== uploads目录内容 ({uploads_dir}) ===")
        if not os.path.exists(uploads_dir):
            print("目录不存在!")
        else:
            files = os.listdir(uploads_dir)
            if not files:
                print("目录为空!")
            else:
                print(f"共有 {len(files)} 个文件:")
                for file in files:
                    file_path = os.path.join(uploads_dir, file)
                    file_size = os.path.getsize(file_path) / 1024  # KB
                    print(f"- {file} ({file_size:.2f} KB)")
        
        # 检查数据库中的申请记录
        print(f"\n=== 数据库中的申请记录 ===")
        applications = Application.query.all()
        print(f"共有 {len(applications)} 条申请记录")
        
        for i, app_record in enumerate(applications, 1):
            print(f"\n=== 申请记录 {i} (ID: {app_record.id}) ===")
            print(f"学生ID: {app_record.student_id}")
            print(f"学生姓名: {app_record.student_name}")
            print(f"申请类型: {app_record.application_type}")
            print(f"状态: {app_record.status}")
            
            # 检查文件信息
            if app_record.files:
                print(f"文件数量: {len(app_record.files)}")
                for j, file in enumerate(app_record.files, 1):
                    print(f"  文件 {j}:")
                    print(f"    名称: {file.get('name')}")
                    print(f"    路径: {file.get('path')}")
                    print(f"    大小: {file.get('size')}")
                    print(f"    类型: {file.get('type')}")
                    
                    # 检查文件是否存在
                    if file.get('path'):
                        # 处理路径格式
                        if file['path'].startswith('/uploads/'):
                            # 相对URL，转换为本地路径
                            filename = file['path'].split('/')[-1]
                            local_path = os.path.join(uploads_dir, filename)
                        elif os.path.isabs(file['path']):
                            # 绝对路径
                            local_path = file['path']
                        else:
                            # 其他格式
                            local_path = os.path.join(uploads_dir, file['path'])
                        
                        if os.path.exists(local_path):
                            print(f"    存在: ✓ (本地路径: {local_path})")
                        else:
                            print(f"    存在: ✗ (本地路径: {local_path})")
            else:
                print("文件: 无")
    
    print("\n=== 检查完成 ===")