const http = require('http');

// 测试登录功能
async function testLogin(username, password) {
  return new Promise((resolve, reject) => {
    console.log(`\n测试用户: ${username}`);
    
    const loginData = JSON.stringify({
      username: username,
      password: password
    });

    const options = {
      hostname: 'localhost',
      port: 8080,
      path: '/api/auth/login',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(loginData)
      }
    };

    const req = http.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        console.log(`状态码: ${res.statusCode}`);
        console.log(`响应: ${data}`);
        resolve({ statusCode: res.statusCode, response: data });
      });
    });

    req.on('error', (e) => {
      console.error(`请求错误: ${e.message}`);
      reject(e);
    });

    req.write(loginData);
    req.end();
  });
}

// 测试所有可能的用户和密码组合
async function runAllTests() {
  const users = [
    { username: 'admin', password: 'admin123' },
    { username: 'admin', password: '123456' },
    { username: 'testuser123', password: 'TestPassword123!' },
    { username: 'testuser123', password: '123456' },
    { username: '123456', password: '123456' }
  ];

  for (const user of users) {
    await testLogin(user.username, user.password);
  }
  
  console.log('\n所有测试完成！');
}

runAllTests();