# -*- coding: utf-8 -*-
"""
测试文件保存逻辑
"""

import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

# 测试文件保存功能
def test_file_save():
    print("=== 测试文件保存逻辑 ===")
    
    # 创建上传目录
    upload_dir = os.path.join(os.getcwd(), 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # 创建一个测试文件
    test_file_name = "test_original.txt"
    test_content = "这是一个测试文件，用于验证文件保存功能。\n这是第二行内容。"
    
    with open(test_file_name, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        # 模拟文件上传
        with open(test_file_name, 'rb') as file:
            # 使用相同的文件名生成逻辑
            def generate_safe_filename(original_filename):
                """
                生成安全的文件名，保留中文等非ASCII字符，确保唯一性
                """
                # 分离文件名和扩展名
                name, ext = os.path.splitext(original_filename)
                # 生成唯一标识符
                unique_id = uuid.uuid4().hex[:8]
                # 使用时间戳和唯一ID确保文件名唯一性
                timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                # 保留原始文件名，仅移除路径分隔符防止目录遍历
                safe_name = name.replace('/', '').replace('\\', '')
                # 构建最终文件名
                return f"{safe_name}_{timestamp}_{unique_id}{ext}"
            
            # 使用自定义函数生成文件名
            filename = generate_safe_filename(file.name)
            filepath = os.path.join(upload_dir, filename)
            
            print(f"原始文件名: {file.name}")
            print(f"保存文件名: {filename}")
            print(f"保存路径: {filepath}")
            print(f"文件大小: {os.path.getsize(test_file_name)} bytes")
            
            # 保存文件
            file.save(filepath)
            
            # 检查保存后的文件
            if os.path.exists(filepath):
                saved_size = os.path.getsize(filepath)
                print(f"保存后的文件大小: {saved_size} bytes")
                
                # 读取保存后的文件内容
                with open(filepath, 'r', encoding='utf-8') as saved_file:
                    saved_content = saved_file.read()
                
                print(f"保存后的文件内容: '{saved_content}'")
                
                if saved_size == os.path.getsize(test_file_name):
                    print("✅ 文件保存成功，大小一致！")
                else:
                    print("❌ 文件保存失败，大小不一致！")
            else:
                print("❌ 文件没有保存成功！")
    except Exception as e:
        print(f"❌ 保存过程中发生错误：{str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理测试文件
        if os.path.exists(test_file_name):
            os.remove(test_file_name)


if __name__ == '__main__':
    test_file_save()