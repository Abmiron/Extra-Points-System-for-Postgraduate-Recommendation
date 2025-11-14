# -*- coding: utf-8 -*-
"""
测试API响应中的文件路径格式

该脚本模拟前端调用API获取申请数据，验证返回的文件路径是否正确。
"""

import requests

# API基础URL
API_BASE_URL = 'http://localhost:5001/api'

def test_get_all_applications():
    """测试获取所有申请API"""
    print("=== 测试获取所有申请API ===")
    try:
        response = requests.get(f'{API_BASE_URL}/applications')
        response.raise_for_status()
        applications = response.json()
        
        print(f"获取到 {len(applications)} 个申请")
        for i, app in enumerate(applications, 1):
            print(f"\n申请 {i} (ID: {app['id']}):")
            print(f"  学生姓名: {app['studentName']}")
            print(f"  状态: {app['status']}")
            if app['files']:
                print(f"  文件数量: {len(app['files'])}")
                for j, file in enumerate(app['files'], 1):
                    print(f"    文件 {j}:")
                    print(f"      名称: {file['name']}")
                    print(f"      路径: {file['path']}")
                    print(f"      格式正确: {file['path'].startswith('/uploads/')}")
        
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_get_application_by_id(app_id):
    """测试获取单个申请API"""
    print(f"\n=== 测试获取单个申请API (ID: {app_id}) ===")
    try:
        response = requests.get(f'{API_BASE_URL}/applications/{app_id}')
        response.raise_for_status()
        app = response.json()
        
        print(f"申请 ID: {app['id']}")
        print(f"学生姓名: {app['studentName']}")
        print(f"状态: {app['status']}")
        if app['files']:
            print(f"文件数量: {len(app['files'])}")
            for j, file in enumerate(app['files'], 1):
                print(f"  文件 {j}:")
                print(f"    名称: {file['name']}")
                print(f"    路径: {file['path']}")
                print(f"    格式正确: {file['path'].startswith('/uploads/')}")
        
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_get_pending_applications():
    """测试获取待审核申请API"""
    print(f"\n=== 测试获取待审核申请API ===")
    try:
        response = requests.get(f'{API_BASE_URL}/applications/pending')
        response.raise_for_status()
        applications = response.json()
        
        print(f"获取到 {len(applications)} 个待审核申请")
        for i, app in enumerate(applications, 1):
            print(f"\n申请 {i} (ID: {app['id']}):")
            print(f"  学生姓名: {app['studentName']}")
            print(f"  状态: {app['status']}")
            if app['files']:
                print(f"  文件数量: {len(app['files'])}")
                for j, file in enumerate(app['files'], 1):
                    print(f"    文件 {j}:")
                    print(f"      名称: {file['name']}")
                    print(f"      路径: {file['path']}")
                    print(f"      格式正确: {file['path'].startswith('/uploads/')}")
        
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == '__main__':
    print("=== 测试API响应中的文件路径格式 ===")
    
    test_get_all_applications()
    test_get_application_by_id(1)  # 测试旧申请记录
    test_get_application_by_id(2)  # 测试旧申请记录
    test_get_application_by_id(3)  # 测试新申请记录
    test_get_pending_applications()
    
    print("\n=== 所有测试完成 ===")