require('dotenv').config();
const http = require('http');

// 测试健康检查端点
function testHealthEndpoint() {
  console.log('\n=== 测试健康检查端点 ===');
  
  const options = {
    hostname: 'localhost',
    port: process.env.SERVER_PORT || 8080,
    path: '/api/health',
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  };

  const req = http.request(options, (res) => {
    console.log(`健康检查状态码: ${res.statusCode}`);
    
    let data = '';
    res.on('data', (chunk) => {
      data += chunk;
    });

    res.on('end', () => {
      console.log('健康检查响应:', data);
    });
  });

  req.on('error', (e) => {
    console.error(`健康检查请求错误: ${e.message}`);
  });

  req.end();
}

// 测试用户信息API（需要认证）
function testUserInfoEndpoint(token) {
  console.log('\n=== 测试用户信息端点 ===');
  
  const options = {
    hostname: 'localhost',
    port: process.env.SERVER_PORT || 8080,
    path: '/api/user/info',
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  };

  const req = http.request(options, (res) => {
    console.log(`用户信息状态码: ${res.statusCode}`);
    
    let data = '';
    res.on('data', (chunk) => {
      data += chunk;
    });

    res.on('end', () => {
      console.log('用户信息响应:', data);
    });
  });

  req.on('error', (e) => {
    console.error(`用户信息请求错误: ${e.message}`);
  });

  req.end();
}

// 测试管理员学生列表API
function testStudentListEndpoint(token) {
  console.log('\n=== 测试管理员学生列表端点 ===');
  
  const options = {
    hostname: 'localhost',
    port: process.env.SERVER_PORT || 8080,
    path: '/api/admin/user/students',
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  };

  const req = http.request(options, (res) => {
    console.log(`学生列表状态码: ${res.statusCode}`);
    
    let data = '';
    res.on('data', (chunk) => {
      data += chunk;
    });

    res.on('end', () => {
      console.log('学生列表响应:', data);
    });
  });

  req.on('error', (e) => {
    console.error(`学生列表请求错误: ${e.message}`);
  });

  req.end();
}

// 测试登录
function testLogin(username, password, callback) {
  console.log(`\n=== 测试登录 ${username} ===`);
  
  const loginData = JSON.stringify({
    username: username,
    password: password
  });

  const options = {
    hostname: 'localhost',
    port: process.env.SERVER_PORT || 8080,
    path: '/api/auth/login',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(loginData)
    }
  };

  const req = http.request(options, (res) => {
    console.log(`登录状态码: ${res.statusCode}`);
    
    let data = '';
    res.on('data', (chunk) => {
      data += chunk;
    });

    res.on('end', () => {
      console.log('登录响应:', data);
      try {
        const result = JSON.parse(data);
        if (callback) callback(result.token || null);
      } catch (e) {
        console.error('解析登录响应失败:', e.message);
        if (callback) callback(null);
      }
    });
  });

  req.on('error', (e) => {
    console.error(`登录请求错误: ${e.message}`);
    if (callback) callback(null);
  });

  req.write(loginData);
  req.end();
}

// 运行所有测试
testHealthEndpoint();

// 测试admin登录
testLogin('admin', 'admin123', (token) => {
  if (token) {
    console.log('\n✅ Admin登录成功，获取到token');
    testUserInfoEndpoint(token);
    testStudentListEndpoint(token);
  } else {
    console.log('\n❌ Admin登录失败');
    // 尝试其他可能的密码
    testLogin('admin', '123456', (anotherToken) => {
      if (anotherToken) {
        console.log('\n✅ Admin使用密码123456登录成功');
        testUserInfoEndpoint(anotherToken);
        testStudentListEndpoint(anotherToken);
      }
    });
  }
});

// 3秒后测试学生用户登录
setTimeout(() => {
  testLogin('testuser123', '123456', (token) => {
    if (token) {
      console.log('\n✅ 学生登录成功，获取到token');
      testUserInfoEndpoint(token);
    }
  });
}, 3000);