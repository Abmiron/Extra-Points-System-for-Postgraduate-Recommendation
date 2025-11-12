const http = require('http');

// 测试获取用户列表的API
function testUsersApi() {
  console.log('开始测试获取用户列表API...');
  
  const options = {
    hostname: 'localhost',
    port: 8080,
    path: '/api/users',
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  };

  const req = http.request(options, (res) => {
    console.log(`状态码: ${res.statusCode}`);
    console.log('响应头:', JSON.stringify(res.headers, null, 2));
    
    let data = '';

    res.on('data', (chunk) => {
      data += chunk;
    });

    res.on('end', () => {
      try {
        const parsedData = JSON.parse(data);
        console.log('\n响应体:');
        console.log(JSON.stringify(parsedData, null, 2));
        
        if (Array.isArray(parsedData)) {
          console.log(`\nAPI返回了 ${parsedData.length} 个用户`);
        } else if (parsedData.users) {
          console.log(`\nAPI返回了 ${parsedData.users.length} 个用户`);
        }
        
      } catch (e) {
        console.log('\n响应体(原始文本):', data);
        console.log('解析JSON失败:', e.message);
      }
    });
  });

  req.on('error', (e) => {
    console.error(`请求错误: ${e.message}`);
  });

  req.end();
}

// 测试需要认证的用户API
function testAuthenticatedUsersApi() {
  console.log('\n\n开始测试需要认证的用户API...');
  
  // 先登录获取token
  console.log('1. 尝试使用admin账户登录...');
  
  const loginData = JSON.stringify({
    username: 'admin',
    password: 'admin123'
  });

  const loginOptions = {
    hostname: 'localhost',
    port: 8080,
    path: '/api/auth/login',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(loginData)
    }
  };

  const loginReq = http.request(loginOptions, (res) => {
    let loginData = '';

    res.on('data', (chunk) => {
      loginData += chunk;
    });

    res.on('end', () => {
      try {
        const loginResult = JSON.parse(loginData);
        console.log('登录结果:', JSON.stringify(loginResult, null, 2));
        
        if (loginResult.token) {
          console.log('\n2. 使用获取的token查询用户列表...');
          
          const userListOptions = {
            hostname: 'localhost',
            port: 8080,
            path: '/api/admin/users',
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${loginResult.token}`
            }
          };

          const userListReq = http.request(userListOptions, (userRes) => {
            console.log(`用户列表API状态码: ${userRes.statusCode}`);
            
            let userData = '';
            userRes.on('data', (chunk) => {
              userData += chunk;
            });
            
            userRes.on('end', () => {
              try {
                const parsedUserData = JSON.parse(userData);
                console.log('用户列表响应:', JSON.stringify(parsedUserData, null, 2));
              } catch (e) {
                console.log('用户列表响应(原始文本):', userData);
              }
            });
          });
          
          userListReq.on('error', (e) => {
            console.error(`用户列表请求错误: ${e.message}`);
          });
          
          userListReq.end();
        }
      } catch (e) {
        console.log('登录响应(原始文本):', loginData);
        console.log('解析登录结果失败:', e.message);
      }
    });
  });

  loginReq.on('error', (e) => {
    console.error(`登录请求错误: ${e.message}`);
  });

  loginReq.write(loginData);
  loginReq.end();
}

// 执行测试
testUsersApi();
testAuthenticatedUsersApi();