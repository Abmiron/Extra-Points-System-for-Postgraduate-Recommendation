import requests

# 测试API接口
def test_api():
    # 先获取所有学生的申请记录，看看有哪些学生ID
    print("获取所有申请记录，查看有哪些学生ID:")
    url = "http://127.0.0.1:5001/api/applications"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            all_data = response.json()
            print(f"所有申请记录数量: {len(all_data)}")
            
            # 提取所有学生ID（注意后端返回的是驼峰式命名的studentId）
            student_ids = set()
            for app in all_data:
                if 'studentId' in app:
                    student_ids.add(app['studentId'])
            
            print(f"所有学生ID: {list(student_ids)}")
            print("\n" + "=" * 50)
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return
    except Exception as e:
        print(f"请求错误: {str(e)}")
        return
    
    # 使用实际存在的学生ID（从上面的结果中选择一个）
    if student_ids:
        student_id = list(student_ids)[0]  # 使用第一个学生ID
    else:
        student_id = '20200001'  # 如果没有记录，使用默认值
    
    print(f"测试学生ID: {student_id}")
    print("=" * 50)
    
    # 测试获取申请记录接口
    print("1. 测试 /api/applications?studentId=xxx 接口:")
    url = f"http://127.0.0.1:5001/api/applications?studentId={student_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"   返回状态码: {response.status_code}")
            print(f"   返回记录数量: {len(data)}")
            print(f"   第一条记录: {data[0] if data else '无记录'}")
        else:
            print(f"   请求失败，状态码: {response.status_code}")
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"   请求错误: {str(e)}")
    
    print("\n" + "=" * 50)
    
    # 测试获取统计数据接口
    print("2. 测试 /api/applications/statistics?studentId=xxx 接口:")
    url = f"http://127.0.0.1:5001/api/applications/statistics?studentId={student_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"   返回状态码: {response.status_code}")
            print(f"   统计数据: {data}")
        else:
            print(f"   请求失败，状态码: {response.status_code}")
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"   请求错误: {str(e)}")

if __name__ == "__main__":
    test_api()