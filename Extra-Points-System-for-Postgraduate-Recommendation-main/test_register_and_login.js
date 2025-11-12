const http = require('http');

// 注册新用户
async function registerUser(username, password, name) {
  return new Promise((resolve, reject) => {
    console.log(`\n开始注册用户: ${username}`);
    
    const userData = JSON.stringify({
      username: username,
      password: password,
      name: name,
      role: "student",
      student_id: username // 添加学号字段，使用用户名作为学号
    });

    const options = {
      hostname: 'localhost',
      port: 8080,
      path: '/api/auth/register',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(userData)
      }
    };

    const req = http.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        console.log(`注册状态码: ${res.statusCode}`);
        console.log(`注册响应: ${data}`);
        resolve({ statusCode: res.statusCode, response: data });
      });
    });

    req.on('error', (e) => {
      console.error(`注册请求错误: ${e.message}`);
      reject(e);
    });

    req.write(userData);
    req.end();
  });
}

// 登录用户
async function loginUser(username, password) {
  return new Promise((resolve, reject) => {
    console.log(`\n开始登录用户: ${username}`);
    
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
        console.log(`登录状态码: ${res.statusCode}`);
        console.log(`登录响应: ${data}`);
        resolve({ statusCode: res.statusCode, response: data });
      });
    });

    req.on('error', (e) => {
      console.error(`登录请求错误: ${e.message}`);
      reject(e);
    });

    req.write(loginData);
    req.end();
  });
}

// 主测试函数
async function runTest() {
  const testUsername = 'newtestuser';
  const testPassword = 'NewTestPass123!';
  const testName = '新测试用户';
  
  // 注册新用户
  const registerResult = await registerUser(testUsername, testPassword, testName);
  
  if (registerResult.statusCode === 201 || registerResult.statusCode === 200) {
    // 注册成功，尝试登录
    await loginUser(testUsername, testPassword);
  }
  
  console.log('\n测试完成！');
}

runTest();