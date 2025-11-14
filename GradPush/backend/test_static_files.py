# -*- coding: utf-8 -*-
"""
测试静态文件服务是否正常工作
"""

import requests
import os

# 测试文件路径
UPLOAD_FOLDER = 'uploads'

# 检查uploads目录下的文件
print("=== 检查uploads目录下的文件 ===")
if os.path.exists(UPLOAD_FOLDER):
    files = os.listdir(UPLOAD_FOLDER)
    print(f"找到 {len(files)} 个文件:")
    for file in files:
        print(f"  - {file}")
        
        # 测试访问静态文件
        url = f"http://localhost:5001/uploads/{file}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"    ✓ 可以访问: {url}")
                print(f"    响应内容类型: {response.headers.get('Content-Type')}")
                print(f"    响应内容长度: {len(response.content)} 字节")
            else:
                print(f"    ✗ 无法访问: {url} (状态码: {response.status_code})")
        except Exception as e:
            print(f"    ✗ 访问错误: {e}")
        print()
else:
    print(f"✗ uploads目录不存在: {UPLOAD_FOLDER}")

print("=== 测试完成 ===")