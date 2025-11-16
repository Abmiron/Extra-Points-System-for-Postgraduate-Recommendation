import requests

# 测试获取规则列表
response = requests.get('http://localhost:5001/api/rules')
print('Status Code:', response.status_code)
print('Response Content:', response.text)
print('Response Encoding:', response.encoding)
print('JSON Data:', response.json())