// 简化版模拟数据

// 初始化模拟用户数据
export const initializeMockUsers = () => {
  if (!localStorage.getItem('users')) {
    const mockUsers = {
      'student': {
        username: 'student',
        password: '123456',
        name: '张同学',
        studentName: '张同学',
        studentId: '2020318001',
        role: 'student',
        avatar: '/images/头像1.jpg',
        faculty: '信息学院',
        department: '计算机科学与技术系',
        major: '计算机科学与技术',
        email: 'student@xmu.edu.cn',
        phone: '13800138000'
      },
      'teacher': {
        username: 'teacher',
        password: '123456',
        name: '张老师',
        role: 'teacher',
        avatar: '/images/头像2.jpg',
        faculty: '信息学院',
        roleName: '审核员',
        email: 'teacher@xmu.edu.cn',
        phone: '13900139000'
      },
      'admin': {
        username: 'admin',
        password: '123456',
        name: '管理员',
        role: 'admin',
        avatar: '/images/头像2.jpg',
        faculty: '信息学院',
        roleName: '系统管理员',
        email: 'admin@xmu.edu.cn',
        phone: '13700137000'
      }
    };
    
    localStorage.setItem('users', JSON.stringify(mockUsers));
    return mockUsers;
  }
  return JSON.parse(localStorage.getItem('users') || '{}');
};

// 初始化模拟申请数据
export const generateMockApplications = () => {
  const applications = [
    {
      id: 'app001',
      studentName: '张三',
      studentId: '2020318001',
      department: '计算机科学与技术系',
      major: '计算机科学与技术',
      applicationType: 'academic',
      appliedAt: '2024-03-15T10:30:00Z',
      selfScore: 4.5,
      status: 'pending',
      projectName: '全国大学生程序设计竞赛',
      awardDate: '2024-02-20',
      awardLevel: 'national',
      awardType: 'individual',
      description: '在2024年全国大学生程序设计竞赛中获得一等奖。'
    }
  ];
  
  return applications;
};

// 初始化本地存储数据
export const initializeMockData = () => {
  // 初始化用户数据
  initializeMockUsers();
  
  // 初始化申请数据
  if (!localStorage.getItem('studentApplications')) {
    const mockApplications = generateMockApplications();
    localStorage.setItem('studentApplications', JSON.stringify(mockApplications));
  }
};

// 用户登录验证函数
export const validateLogin = function(username, password) {
  try {
    const users = initializeMockUsers();
    const user = users[username];
    
    if (user && user.password === password) {
      return { username: user.username, name: user.name, role: user.role };
    }
    
    return null;
  } catch (error) {
    console.error('登录错误:', error);
    return null;
  }
};

// 密码重置函数
export const resetPassword = async function(username, newPassword) {
  try {
    const users = initializeMockUsers();
    
    if (users[username]) {
      // 更新用户密码
      users[username].password = newPassword;
      // 保存到localStorage
      localStorage.setItem('users', JSON.stringify(users));
      console.log(`用户 ${username} 的密码已重置`);
      return true;
    }
    
    console.log(`未找到用户 ${username}`);
    return false;
  } catch (error) {
    console.error('密码重置错误:', error);
    return false;
  }
};