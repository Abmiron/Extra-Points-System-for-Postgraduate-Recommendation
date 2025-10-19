// 模拟数据生成器
// 生成mock申请数据
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
      description: '在2024年全国大学生程序设计竞赛中获得一等奖，展现了优秀的算法设计和编程能力。',
      files: [
        { name: '获奖证书.jpg', url: 'https://pic.ibaotu.com/00/02/39/43a888piCzJ2.jpg-0.jpg!ww7006' },
        { name: '比赛成绩单.jpg', url: 'https://img95.699pic.com/excel/40015/8976.jpg!/crop/0x1400a0a0/fw/850/quality/90' }
      ]
    },
    {
      id: 'app002',
      studentName: '张三',
      studentId: '2020318001',
      department: '计算机科学与技术系',
      major: '计算机科学与技术',
      applicationType: 'comprehensive',
      appliedAt: '2024-03-16T14:20:00Z',
      selfScore: 3.0,
      status: 'pending',
      projectName: '校级优秀学生干部',
      awardDate: '2024-01-10',
      awardLevel: 'school',
      awardType: 'individual',
      description: '担任班级学习委员，组织多次学习活动，获得校级优秀学生干部称号。',
      files: [
        { name: '优秀学生干部证书.pdf', url: '/certificates/cert002.pdf' }
      ]
    },
    {
      id: 'app003',
      studentName: '张三',
      studentId: '2020318001',
      department: '计算机科学与技术系',
      major: '计算机科学与技术',
      applicationType: 'academic',
      appliedAt: '2024-03-14T09:15:00Z',
      selfScore: 5.0,
      status: 'pending',
      projectName: '国际人工智能创新大赛',
      awardDate: '2024-03-01',
      awardLevel: 'national',
      awardType: 'team',
      description: '作为团队核心成员参加国际人工智能创新大赛，获得特等奖。',
      files: [
        { name: '获奖证书.pdf', url: '/certificates/cert003.pdf' },
        { name: '项目报告.docx', url: '/certificates/report003.docx' },
        { name: '演示视频.mp4', url: '/certificates/demo003.mp4' }
      ]
    },
    {
      id: 'app004',
      studentName: '张三',
      studentId: '2020318001',
      department: '计算机科学与技术系',
      major: '计算机科学与技术',
      applicationType: 'academic',
      appliedAt: '2024-03-17T16:45:00Z',
      selfScore: 2.5,
      status: 'approved',
      finalScore: 2.0,
      reviewComment: '项目符合加分标准，但自评分数偏高，根据规定调整为2.0分。',
      reviewedAt: '2024-03-18T10:20:00Z',
      reviewedBy: '张老师',
      projectName: '省级数学建模竞赛',
      awardDate: '2024-02-28',
      awardLevel: 'provincial',
      awardType: 'team',
      description: '参加省级数学建模竞赛获得二等奖。',
      files: [
        { name: '获奖证书.pdf', url: '/certificates/cert004.pdf' }
      ]
    },
    {
      id: 'app005',
      studentName: '张三',
      studentId: '2020318001',
      department: '计算机科学与技术系',
      major: '计算机科学与技术',
      applicationType: 'comprehensive',
      appliedAt: '2024-03-13T11:10:00Z',
      selfScore: 4.0,
      status: 'rejected',
      finalScore: 0,
      reviewComment: '申请材料不完整，缺少必要的证明文件，请补充后重新提交。',
      reviewedAt: '2024-03-15T15:30:00Z',
      reviewedBy: '李老师',
      projectName: '社会实践优秀个人',
      awardDate: '2024-01-20',
      awardLevel: 'municipal',
      awardType: 'individual',
      description: '参与社会实践活动表现突出，获得市级表彰。',
      files: [
        { name: '社会实践证明.pdf', url: '/certificates/cert005.pdf' }
      ]
    }
  ]
  
  return applications
}

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
    }
    
    localStorage.setItem('users', JSON.stringify(mockUsers))
    console.log('模拟用户数据已初始化到本地存储')
    return mockUsers
  }
  return JSON.parse(localStorage.getItem('users') || '{}')
}

// 初始化本地存储数据
export const initializeMockData = () => {
  // 初始化用户数据
  initializeMockUsers()
  
  // 初始化申请数据
  if (!localStorage.getItem('studentApplications')) {
    const mockApplications = generateMockApplications()
    
    // 为每个mock申请添加学生信息（与显示组件保持一致）
    const enhancedMockApplications = mockApplications.map(app => ({
      ...app,
      studentName: app.studentName || '模拟学生',
      studentId: app.studentId || '2020318000',
      department: app.department || 'cs',
      major: app.major || 'cs'
    }))
    
    localStorage.setItem('studentApplications', JSON.stringify(enhancedMockApplications))
    console.log('模拟申请数据已初始化到本地存储')
    return enhancedMockApplications
  }
  return JSON.parse(localStorage.getItem('studentApplications') || '[]')
}

// 用户注册函数
export const registerUser = (userData) => {
  try {
    // 获取现有用户数据
    let users = JSON.parse(localStorage.getItem('users') || '{}')
    
    // 检查用户名是否已存在
    if (users[userData.username]) {
      throw new Error('用户名已存在')
    }
    
    // 创建新用户
    const newUser = {
      username: userData.username,
      password: userData.password, // 实际应用中应该进行加密
      name: userData.name,
      role: userData.role,
      avatar: userData.role === 'student' ? '/images/头像1.jpg' : '/images/头像2.jpg',
      faculty: '信息学院', // 默认为信息学院
      email: '', // 默认为空
      phone: '' // 默认为空
    }
    
    // 根据角色添加额外信息
    if (userData.role === 'student') {
      newUser.studentName = userData.name
      newUser.studentId = userData.username
      newUser.department = '计算机科学与技术系'
      newUser.major = '计算机科学与技术'
    } else if (userData.role === 'teacher') {
      newUser.roleName = '审核员'
    }
    
    // 添加到用户数据库
    users[userData.username] = newUser
    localStorage.setItem('users', JSON.stringify(users))
    
    console.log('用户注册成功:', userData.username)
    return true
  } catch (error) {
    console.error('注册失败:', error.message)
    throw error
  }
}

// 用户登录验证函数
export const validateLogin = (username, password) => {
  const users = JSON.parse(localStorage.getItem('users') || '{}')
  const user = users[username]
  
  if (user && user.password === password) {
    // 返回用户信息（不包含密码）
    const { password, ...userInfo } = user
    return userInfo
  }
  return null
}

// 获取待审核申请
export const getPendingApplications = () => {
  const applications = JSON.parse(localStorage.getItem('studentApplications') || '[]')
  return applications.filter(app => app.status === 'pending')
}

// 获取已审核申请
export const getReviewedApplications = () => {
  const applications = JSON.parse(localStorage.getItem('studentApplications') || '[]')
  return applications.filter(app => app.status === 'approved' || app.status === 'rejected')
}

// 密码重置函数
export const resetPassword = (username, newPassword) => {
  try {
    // 获取现有用户数据
    let users = JSON.parse(localStorage.getItem('users') || '{}')
    
    // 检查用户是否存在
    if (!users[username]) {
      console.error('用户不存在:', username)
      return false
    }
    
    // 更新密码
    users[username].password = newPassword
    localStorage.setItem('users', JSON.stringify(users))
    
    console.log('密码重置成功:', username)
    return true
  } catch (error) {
    console.error('密码重置失败:', error.message)
    throw error
  }
}