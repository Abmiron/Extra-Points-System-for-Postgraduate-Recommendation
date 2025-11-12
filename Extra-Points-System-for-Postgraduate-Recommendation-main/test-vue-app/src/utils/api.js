// API服务配置
// 使用相对路径，通过Vite代理转发到后端
const API_BASE_URL = '/api';
// 是否启用模拟数据模式
let useMockData = false;

// 通用请求方法
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // 添加默认配置
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json'
    }
  };
  
  // 如果有认证令牌，添加到请求头
  const token = localStorage.getItem('token');
  if (token) {
    defaultOptions.headers['Authorization'] = `Bearer ${token}`;
  }
  
  // 合并选项
  const fetchOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers
    }
  };
  
  // 检查是否是登录请求（移到try-catch外部以避免作用域问题）
  const isLoginRequest = endpoint === '/auth/login' && options.method === 'POST';
  
  try {
    // 检查是否使用模拟数据
    const shouldUseMock = useMockData || (token && token.startsWith('mock_'));
    
    // 对于非登录请求，如果应该使用模拟数据，则返回模拟数据
    if (!isLoginRequest && shouldUseMock) {
      console.warn(`使用模拟数据模式处理请求: ${endpoint}`);
      
      // 根据不同的端点返回相应的模拟数据
      if (endpoint === '/user/info') {
        // 返回模拟用户信息
        console.log('API模拟模式: 获取用户信息');
        
        // 首先尝试从localStorage获取userInfo
        let userInfo = null;
        const storedUserInfo = localStorage.getItem('userInfo');
        if (storedUserInfo) {
          try {
            userInfo = JSON.parse(storedUserInfo);
            console.log('从localStorage获取到用户信息:', userInfo);
          } catch (e) {
            console.error('解析用户信息失败:', e);
          }
        }
        
        // 如果localStorage中没有用户信息，尝试从users中获取
        if (!userInfo) {
          try {
            const users = JSON.parse(localStorage.getItem('users') || '{}');
            const token = localStorage.getItem('token');
            
            // 尝试通过token或用户名查找用户
            if (token && token.startsWith('mock_')) {
              // 在模拟模式下，尝试查找当前可能登录的用户
              for (const username in users) {
                const user = users[username];
                // 假设最后更新的用户就是当前登录用户
                if (user && user.lastLogin) {
                  userInfo = user;
                  break;
                }
              }
            }
            
            if (userInfo) {
              console.log('从users存储中获取到用户信息:', userInfo);
            }
          } catch (e) {
            console.error('从users存储获取用户信息失败:', e);
          }
        }
        
        // 确保用户信息完整
        if (userInfo) {
          // 确保有名称字段
          if (!userInfo.name && !userInfo.studentName && userInfo.username) {
            userInfo.name = userInfo.username;
            userInfo.studentName = userInfo.username;
            console.log('为用户信息添加名称字段:', userInfo.name);
          }
          
          // 确保有角色字段
          if (!userInfo.role) {
            userInfo.role = userInfo.username === 'admin' ? 'admin' : 
                          userInfo.username === 'teacher' ? 'teacher' : 'student';
          }
          
          return userInfo;
        }
        
        // 如果所有尝试都失败，返回更完整的默认用户信息
        console.log('使用默认用户信息');
        const defaultUser = {
          id: 1,
          name: '模拟学生',
          studentName: '模拟学生',
          username: 'student',
          role: 'student',
          status: 'active',
          faculty: '信息学院',
          major: '计算机科学与技术'
        };
        return defaultUser;
      } else if (endpoint.includes('/application/list')) {
        // 返回模拟申请列表
        return {
          success: true,
          data: [
            {
              id: '1',
              title: '学术竞赛加分申请',
              description: '参加省级数学建模竞赛获得二等奖',
              status: 'pending',
              studentId: '2020318001',
              createdAt: new Date().toISOString()
            }
          ]
        };
      }
      // 其他端点返回基本结构
      return { success: true, data: [] };
    }
    
    const response = await fetch(url, fetchOptions);
    
    // 解析响应数据
    let data = null;
    
    // 首先获取响应文本，避免响应体被多次读取
    const responseText = await response.text();
    
    try {
      // 尝试将文本解析为JSON
      if (responseText.trim()) {
        data = JSON.parse(responseText);
      } else {
        data = {};
      }
    } catch (parseError) {
      console.warn('无法解析JSON响应:', parseError);
      // JSON解析失败，使用文本响应
      data = { message: responseText, rawText: responseText };
    }
    
    // 检查响应状态
    if (!response.ok) {
      // 对于登录请求，不自动切换到模拟模式，让auth.js处理
      if (!isLoginRequest) {
        // 构建错误消息，优先使用data中的错误信息
        const errorMessage = data?.error || data?.message || data?.msg || `请求失败，状态码: ${response.status}`;
        throw new Error(errorMessage);
      } else {
        // 登录请求失败，抛出错误让auth.js处理模拟登录
        throw new Error('登录失败');
      }
    }
    
    return data;
  } catch (error) {
    console.error('API请求错误:', error);
    
    // 对于非登录请求，如果有模拟令牌，启用模拟数据模式
    if (!isLoginRequest && token && token.startsWith('mock_')) {
      console.warn('启用模拟数据模式以避免应用崩溃');
      useMockData = true;
      // 返回模拟数据，避免应用崩溃
      return { success: true, data: [] };
    }
    
    throw error;
  }
}

// API方法集合
export const api = {
  // 认证相关
  auth: {
    // 登录
    login: (credentials) => request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    }),
    // 登出
    logout: () => request('/auth/logout'),
    // 注册
    register: (userData) => request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    })
  },
  
  // 用户相关
  user: {
    // 获取用户信息
    getInfo: () => request('/user/info'),
    // 更新用户信息
    updateInfo: (userInfo) => request('/user/update', {
      method: 'POST',
      body: JSON.stringify(userInfo)
    }),
    // 修改密码
    changePassword: (passwordData) => request('/user/change-password', {
      method: 'POST',
      body: JSON.stringify(passwordData)
    })
  },
  
  // 申请相关
  application: {
    // 创建申请
    create: (data) => request('/application/create', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
    // 获取申请列表
    list: (params) => request(`/application/list?${new URLSearchParams(params)}`),
    // 获取申请详情
    detail: (id) => request(`/application/detail/${id}`),
    // 更新申请
    update: (id, data) => request(`/application/update/${id}`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
    // 提交申请
    submit: (id) => request('/application/submit', {
      method: 'POST',
      body: JSON.stringify({ id })
    }),
    // 删除申请
    delete: (id) => request(`/application/delete/${id}`, {
      method: 'DELETE'
    })
  },
  
  // 审核相关
  review: {
    // 获取待审核列表
    pending: (params) => request(`/review/pending?${new URLSearchParams(params)}`),
    // 获取审核历史
    history: (params) => request(`/review/history?${new URLSearchParams(params)}`),
    // 审核通过
    approve: (id, data) => request('/review/approve', {
      method: 'POST',
      body: JSON.stringify({ id, ...data })
    }),
    // 审核驳回
    reject: (id, data) => request('/review/reject', {
      method: 'POST',
      body: JSON.stringify({ id, ...data })
    })
  },
  
  // 规则相关
  rule: {
    // 获取有效规则列表
    valid: () => request('/rule/valid'),
    // 获取所有规则
    list: () => request('/rule/list'),
    // 创建规则
    create: (rule) => request('/rule/create', {
      method: 'POST',
      body: JSON.stringify(rule)
    }),
    // 更新规则
    update: (id, rule) => request(`/rule/update/${id}`, {
      method: 'POST',
      body: JSON.stringify(rule)
    }),
    // 切换规则状态
    toggleStatus: (id) => request(`/rule/toggle/${id}`, {
      method: 'POST'
    })
  },
  
  // 分数相关
  score: {
    // 计算学生分数
    calculate: () => request('/score/calculate'),
    // 获取分数汇总
    summary: (studentId) => request(`/score/summary/${studentId}`)
  },
  
  // 管理员相关
  admin: {
    // 用户管理
    users: {
      list: (params) => request(`/admin/user/list?${new URLSearchParams(params)}`),
      create: (user) => request('/admin/user/create', {
        method: 'POST',
        body: JSON.stringify(user)
      }),
      update: (id, user) => request(`/admin/user/update/${id}`, {
        method: 'POST',
        body: JSON.stringify(user)
      }),
      delete: (id) => request(`/admin/user/delete/${id}`, {
        method: 'DELETE'
      })
    },
    // 系统设置
    settings: {
      get: () => request('/admin/settings'),
      update: (settings) => request('/admin/settings/update', {
        method: 'POST',
        body: JSON.stringify(settings)
      })
    }
  }
};

export default api;