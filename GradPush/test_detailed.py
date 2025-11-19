import requests
import json

BASE_URL = "http://127.0.0.1:5001/api"

# 测试获取所有申请记录
def test_get_all_applications():
    print("\n=== 测试获取所有申请记录 ===")
    response = requests.get(f"{BASE_URL}/applications")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"总记录数: {len(data)}")
        # 打印前5条记录的studentId和status
        print("前5条记录的studentId和status:")
        for i, app in enumerate(data[:5]):
            print(f"  {i+1}. studentId: {app.get('studentId')}, status: {app.get('status')}, applicationType: {app.get('applicationType')}")
        return data
    return []

# 测试使用studentId过滤申请记录
def test_get_applications_by_student_id(student_id):
    print(f"\n=== 测试获取学生 {student_id} 的申请记录 ===")
    response = requests.get(f"{BASE_URL}/applications?studentId={student_id}")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"记录数: {len(data)}")
        # 打印所有记录的详细信息
        for i, app in enumerate(data):
            print(f"  {i+1}. applicationType: {app.get('applicationType')}, status: {app.get('status')}, score: {app.get('score')}")
        return data
    return []

# 测试获取统计数据
def test_get_statistics(student_id):
    print(f"\n=== 测试获取学生 {student_id} 的统计数据 ===")
    response = requests.get(f"{BASE_URL}/applications/statistics?studentId={student_id}")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("统计数据:")
        for key, value in data.items():
            print(f"  {key}: {value}")
        return data
    return None

# 测试获取待审核申请记录
def test_get_pending_applications():
    print("\n=== 测试获取所有待审核申请记录 ===")
    response = requests.get(f"{BASE_URL}/applications/pending")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"待审核记录数: {len(data)}")
        # 打印前5条记录的studentId
        print("前5条待审核记录的studentId:")
        for i, app in enumerate(data[:5]):
            print(f"  {i+1}. studentId: {app.get('studentId')}")
        return data
    return []

# 运行所有测试
if __name__ == "__main__":
    print("开始详细测试API接口...")
    
    # 1. 获取所有申请记录
    all_applications = test_get_all_applications()
    
    # 2. 如果有申请记录，提取一些studentId进行测试
    test_student_ids = []
    if all_applications:
        # 提取前3个不同的studentId
        seen_ids = set()
        for app in all_applications:
            student_id = app.get('studentId')
            if student_id and student_id not in seen_ids:
                test_student_ids.append(student_id)
                seen_ids.add(student_id)
                if len(test_student_ids) >= 3:
                    break
    
    if not test_student_ids:
        # 如果没有提取到studentId，使用一些默认值
        test_student_ids = ['student1', 'student2', 'student3']
    
    # 3. 测试每个studentId的申请记录和统计数据
    for student_id in test_student_ids:
        test_get_applications_by_student_id(student_id)
        test_get_statistics(student_id)
    
    # 4. 测试获取待审核申请记录
    test_get_pending_applications()
    
    print("\n所有测试完成！")