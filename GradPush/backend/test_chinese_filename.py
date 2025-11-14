# -*- coding: utf-8 -*-
"""
测试中文文件名上传功能

该脚本用于测试中文文件名的上传是否正常工作，验证文件名是否正确保留中文。
"""

import requests
import os
import tempfile
import shutil

# API基础URL
API_BASE_URL = 'http://localhost:5001/api'

# 创建临时测试文件
def create_test_file(filename, content='测试内容'):
    """创建临时测试文件"""
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return file_path, temp_dir

# 测试上传中文文件名的文件
def test_upload_chinese_filename():
    """测试上传中文文件名的文件"""
    print("=== 测试中文文件名上传功能 ===")
    
    # 创建测试文件
    test_filename = '测试文件_中文名.jpg'
    test_file_path, temp_dir = create_test_file(test_filename)
    print(f"创建测试文件: {test_file_path}")
    
    try:
        # 准备上传数据
        application_data = {
            'student_id': 'test_student',
            'student_name': '测试学生',
            'department': '测试学院',
            'major': '测试专业',
            'application_type': 'academic',
            'self_score': 95,
            'project_name': '测试项目',
            'award_date': '2025-12-31',
            'description': '测试申请描述'
        }
        
        # 创建表单数据
        from io import BytesIO
        import json
        
        files = {
            'application': (None, json.dumps(application_data), 'application/json'),
            'file': (test_filename, open(test_file_path, 'rb'), 'image/jpeg')
        }
        
        # 发送POST请求上传文件
        print(f"上传中文文件名文件: {test_filename}")
        response = requests.post(f'{API_BASE_URL}/applications', files=files)
        response.raise_for_status()
        
        print(f"✓ 上传成功，状态码: {response.status_code}")
        print(f"  响应内容: {response.text}")
        application = response.json()
        print(f"  申请ID: {application['id']}")
        
        # 检查返回的文件信息
        if 'files' in application and application['files']:
            uploaded_file = application['files'][0]
            print(f"  文件名称: {uploaded_file['name']}")
            print(f"  文件路径: {uploaded_file['path']}")
            
            # 检查文件名是否保留了中文
            if '测试文件_中文名' in uploaded_file['name']:
                print("✓ 中文文件名正确保留")
            else:
                print("✗ 中文文件名丢失")
        else:
            print(f"✗ 没有返回文件信息或'files'字段不存在")
            
        # 验证文件是否可以访问
        if application['files']:
            file_url = f"http://localhost:5001{application['files'][0]['path']}"
            print(f"  测试文件访问: {file_url}")
            response = requests.get(file_url)
            if response.status_code == 200:
                print("✓ 文件可以正常访问")
            else:
                print(f"✗ 文件访问失败，状态码: {response.status_code}")
                
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 延迟清理临时文件，确保文件已被释放
        import time
        time.sleep(1)
        try:
            shutil.rmtree(temp_dir)
            print(f"✓ 临时文件已清理: {temp_dir}")
        except Exception as e:
            print(f"⚠ 临时文件清理失败: {e}")

# 测试获取申请数据中的中文文件名
def test_get_application_with_chinese_filename():
    """测试获取申请数据中的中文文件名"""
    print("\n=== 测试获取申请数据中的中文文件名 ===")
    
    try:
        # 获取最新的申请
        response = requests.get(f'{API_BASE_URL}/applications?sort=desc')
        response.raise_for_status()
        applications = response.json()
        
        if not applications:
            print("✗ 没有找到申请记录")
            return False
        
        # 查找包含中文文件名的申请
        found = False
        for app in applications:
            if app['files']:
                for file in app['files']:
                    if '测试文件_中文名' in file['name']:
                        print(f"✓ 找到包含中文文件名的申请")
                        print(f"  申请ID: {app['id']}")
                        print(f"  文件名称: {file['name']}")
                        print(f"  文件路径: {file['path']}")
                        found = True
                        break
                if found:
                    break
        
        if not found:
            print("✗ 没有找到包含中文文件名的申请记录")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

if __name__ == '__main__':
    print("=== 中文文件名上传测试 ===")
    
    # 运行测试
    test_upload_chinese_filename()
    test_get_application_with_chinese_filename()
    
    print("\n=== 所有测试完成 ===")