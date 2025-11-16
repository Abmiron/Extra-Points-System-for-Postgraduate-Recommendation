import requests
import json

# 测试创建新的中文规则
new_rule = {
    "name": "国家级数学竞赛一等奖",
    "type": "academic",
    "sub_type": "competition",
    "level": "国家级",
    "grade": "一等奖",
    "score": 8.0,
    "status": "active",
    "description": "在国家级数学竞赛中获得一等奖"
}

# 创建新规则
response = requests.post('http://localhost:5000/api/rules', json=new_rule)
print('Create Rule Status Code:', response.status_code)
print('Create Rule Response:', response.json())

# 再次获取所有规则
response = requests.get('http://localhost:5000/api/rules')
print('\nGet Rules Status Code:', response.status_code)
print('Get Rules JSON Data:', response.json())