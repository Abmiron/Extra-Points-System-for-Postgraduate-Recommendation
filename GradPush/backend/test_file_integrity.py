# -*- coding: utf-8 -*-
"""
测试文件上传和下载的完整性
"""

import os
import requests
import shutil
import hashlib
from datetime import datetime
import uuid

# 配置
BASE_URL = 'http://localhost:5001'
UPLOAD_DIR = os.path.join(os.getcwd(), 'uploads')
TEST_IMAGE_PATH = os.path.join(os.getcwd(), 'uploads', '测试文件_中文名_20251114092001_0099de5d.jpg')


def calculate_file_hash(filepath):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def test_file_integrity():
    """测试文件完整性"""
    print("=== 测试文件完整性 ===")
    
    # 检查本地文件
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"错误：测试文件不存在 - {TEST_IMAGE_PATH}")
        return
    
    # 获取本地文件信息
    local_file_size = os.path.getsize(TEST_IMAGE_PATH)
    local_file_hash = calculate_file_hash(TEST_IMAGE_PATH)
    
    print(f"本地文件大小：{local_file_size} bytes")
    print(f"本地文件MD5：{local_file_hash}")
    
    # 测试通过HTTP下载文件
    file_name = os.path.basename(TEST_IMAGE_PATH)
    download_url = f"{BASE_URL}/uploads/{file_name}"
    
    print(f"\n通过HTTP下载文件：{download_url}")
    
    try:
        response = requests.get(download_url, stream=True)
        if response.status_code == 200:
            # 保存下载的文件
            temp_file = f"temp_{uuid.uuid4().hex[:8]}.jpg"
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 检查下载的文件
            downloaded_size = os.path.getsize(temp_file)
            downloaded_hash = calculate_file_hash(temp_file)
            
            print(f"下载文件大小：{downloaded_size} bytes")
            print(f"下载文件MD5：{downloaded_hash}")
            
            # 比较文件
            if local_file_size == downloaded_size and local_file_hash == downloaded_hash:
                print("✅ 文件完整性检查通过！")
            else:
                print("❌ 文件完整性检查失败！")
                print(f"   大小不匹配：本地={local_file_size}, 下载={downloaded_size}")
                print(f"   MD5不匹配：本地={local_file_hash}, 下载={downloaded_hash}")
            
            # 清理临时文件
            os.remove(temp_file)
        else:
            print(f"❌ HTTP下载失败，状态码：{response.status_code}")
            print(f"   响应内容：{response.text}")
    except Exception as e:
        print(f"❌ 下载过程中发生错误：{str(e)}")


def test_upload_new_file():
    """测试上传新文件"""
    print("\n=== 测试上传新文件 ===")
    
    # 创建一个测试文件
    test_file_name = f"test_upload_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
    test_file_content = "这是一个测试文件，用于验证文件上传功能。"
    
    with open(test_file_name, 'w', encoding='utf-8') as f:
        f.write(test_file_content)
    
    try:
        # 上传文件
        upload_url = f"{BASE_URL}/api/applications"
        files = {'file': (test_file_name, open(test_file_name, 'rb'))}
        data = {
            'student_id': '123456',
            'student_name': '测试学生',
            'department': '测试学院',
            'major': '测试专业',
            'application_type': 'award',
            'self_score': '85',
            'project_name': '测试项目',
            'award_date': '2023-01-01'
        }
        
        response = requests.post(upload_url, data=data, files=files)
        print(f"上传响应状态码：{response.status_code}")
        print(f"上传响应内容：{response.json()}")
        
        if response.status_code == 201:
            # 获取上传的文件信息
            application_id = response.json().get('id')
            if application_id:
                # 获取申请详情
                detail_url = f"{BASE_URL}/api/applications/{application_id}"
                detail_response = requests.get(detail_url)
                
                if detail_response.status_code == 200:
                    application_data = detail_response.json()
                    files_data = application_data.get('files', [])
                    
                    if files_data:
                        uploaded_file = files_data[0]
                        file_path = uploaded_file.get('path')
                        file_name = uploaded_file.get('name')
                        
                        print(f"\n上传的文件信息：")
                        print(f"  文件名：{file_name}")
                        print(f"  文件路径：{file_path}")
                        print(f"  文件大小：{uploaded_file.get('size')}")
                        print(f"  文件类型：{uploaded_file.get('type')}")
                        
                        # 检查本地保存的文件
                        local_file_path = os.path.join(UPLOAD_DIR, file_name)
                        if os.path.exists(local_file_path):
                            local_size = os.path.getsize(local_file_path)
                            print(f"\n本地保存的文件大小：{local_size} bytes")
                            
                            if local_size > 0:
                                print("✅ 文件上传成功并完整保存！")
                            else:
                                print("❌ 上传的文件大小为0字节！")
                        else:
                            print(f"❌ 本地文件不存在：{local_file_path}")
                    else:
                        print("❌ 申请详情中没有文件信息！")
                else:
                    print(f"❌ 获取申请详情失败，状态码：{detail_response.status_code}")
    except Exception as e:
        print(f"❌ 上传过程中发生错误：{str(e)}")
    finally:
        # 清理测试文件
        if os.path.exists(test_file_name):
            os.remove(test_file_name)


if __name__ == '__main__':
    test_file_integrity()
    test_upload_new_file()