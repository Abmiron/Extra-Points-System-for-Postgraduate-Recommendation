# -*- coding: utf-8 -*-
"""
测试文件访问功能

该脚本用于测试静态文件服务是否正常工作，以及文件URL是否能正确访问。
"""

import requests
import os

base_url = 'http://localhost:5001'

# 测试静态文件服务
def test_static_file_service():
    print("测试静态文件服务...")
    
    # 列出uploads目录下的文件
    upload_dir = os.path.join(os.getcwd(), 'uploads')
    if not os.path.exists(upload_dir):
        print("✗ uploads目录不存在")
        return False
    
    files = os.listdir(upload_dir)
    if not files:
        print("✗ uploads目录下没有文件")
        return False
    
    print(f"✓ uploads目录下有 {len(files)} 个文件")
    
    # 测试访问第一个文件
    test_file = files[0]
    file_url = f"{base_url}/uploads/{test_file}"
    
    try:
        response = requests.get(file_url)
        if response.status_code == 200:
            print(f"✓ 文件 {test_file} 可以通过 {file_url} 访问")
            return True
        else:
            print(f"✗ 文件 {test_file} 访问失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 文件 {test_file} 访问出错: {str(e)}")
        return False

# 测试获取申请数据
def test_get_applications():
    print("\n测试获取申请数据...")
    
    try:
        response = requests.get(f"{base_url}/api/applications")
        if response.status_code == 200:
            applications = response.json()
            print(f"✓ 获取到 {len(applications)} 个申请")
            
            if applications:
                # 检查第一个申请是否包含文件信息
                first_app = applications[0]
                if 'files' in first_app and first_app['files']:
                    print(f"✓ 申请 {first_app['id']} 包含 {len(first_app['files'])} 个文件")
                    
                    # 检查文件信息格式是否正确
                    for file in first_app['files']:
                        if 'path' in file and file['path'].startswith('/uploads/'):
                            print(f"✓ 文件 {file['name']} 的路径格式正确: {file['path']}")
                        else:
                            print(f"✗ 文件 {file['name']} 的路径格式错误: {file.get('path')}")
                else:
                    print("✗ 申请中没有文件信息")
            
            return True
        else:
            print(f"✗ 获取申请数据失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 获取申请数据出错: {str(e)}")
        return False

if __name__ == '__main__':
    print("=== 测试文件访问功能 ===")
    
    test_static_file_service()
    test_get_applications()
    
    print("\n=== 测试完成 ===")