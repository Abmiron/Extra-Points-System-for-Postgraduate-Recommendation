// 模拟数据生成器
export const generateMockApplications = () => {
  const applications = [
    {
      id: 'app001',
      studentName: '张三',
      studentId: '2020318001',
      department: 'cs',
      major: 'cs',
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
        { name: '获奖证书.pdf', url: '/certificates/cert001.pdf' },
        { name: '比赛成绩单.jpg', url: 'https://img95.699pic.com/excel/40015/8976.jpg!/crop/0x1400a0a0/fw/850/quality/90' }
      ]
    },
    {
      id: 'app002',
      studentName: '李四',
      studentId: '2020318002',
      department: 'se',
      major: 'se',
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
      studentName: '王五',
      studentId: '2020318003',
      department: 'ai',
      major: 'ai',
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
      studentName: '赵六',
      studentId: '2020318004',
      department: 'cs',
      major: 'cs',
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
      studentName: '钱七',
      studentId: '2020318005',
      department: 'se',
      major: 'se',
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

// 初始化本地存储数据
export const initializeMockData = () => {
  if (!localStorage.getItem('studentApplications')) {
    const mockApplications = generateMockApplications()
    localStorage.setItem('studentApplications', JSON.stringify(mockApplications))
    console.log('模拟数据已初始化到本地存储')
  }
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