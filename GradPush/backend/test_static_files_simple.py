# -*- coding: utf-8 -*-
"""
简单测试静态文件服务
"""

import requests
import os

BASE_URL = 'http://localhost:5001'
UPLOAD_DIR = os.path.join(os.getcwd(), 'uploads')

# 获取uploads目录中的所有文件
files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]

print("=== 测试静态文件服务 ===")

for file_name in files:
    # 跳过我创建的测试文件
    if file_name.startswith('test_upload_'):
        continue
    
    # 测试文件URL
    file_url = f"{BASE_URL}/uploads/{file_name}"
    local_path = os.path.join(UPLOAD_DIR, file_name)
    local_size = os.path.getsize(local_path)
    
    print(f"\n测试文件: {file_name}")
    print(f"本地大小: {local_size} bytes")
    print(f"访问URL: {file_url}")
    
    try:
        # 发送HTTP请求获取文件
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            # 计算下载的文件大小
            download_size = len(response.content)
            print(f"下载大小: {download_size} bytes")
            
            if download_size == local_size:
                print("✅ 文件大小一致，服务正常")
            else:
                print(f"❌ 文件大小不一致: 本地={local_size}, 下载={download_size}")
            
            # 检查响应头
            content_type = response.headers.get('Content-Type')
            print(f"Content-Type: {content_type}")
        else:
            print(f"❌ HTTP请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 访问文件时发生错误: {str(e)}")

print("\n=== 测试完成 ===")