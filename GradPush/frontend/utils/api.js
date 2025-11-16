// API请求工具

const API_BASE_URL = '/api';

// 封装API请求（支持JSON和文件上传）
async function apiRequest(endpoint, method = 'GET', data = null, token = null) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const options = {
    method,
    headers: {},
  };
  
  // 如果有token，添加到请求头
  if (token) {
    options.headers['Authorization'] = `Bearer ${token}`;
  }
  
  if (data) {
    if (data instanceof FormData) {
      // 文件上传，不设置Content-Type，让浏览器自动处理
      options.body = data;
    } else {
      // JSON数据
      options.headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(data);
    }
  }
  
  try {
    const response = await fetch(url, options);
    
    // 解析响应数据
    const responseData = await response.json();
    
    // 检查响应状态
    if (!response.ok) {
      throw new Error(responseData.message || '请求失败');
    }
    
    return responseData;
  } catch (error) {
    console.error('API请求错误:', error);
    throw error;
  }
}

// 导出API函数
export default {
  // 认证相关
  login: (data) => apiRequest('/login', 'POST', data),
  register: (data) => apiRequest('/register', 'POST', data),
  resetPassword: (data) => apiRequest('/reset-password', 'POST', data),
  getFaculties: () => apiRequest('/faculties'),
  getDepartmentsByFaculty: (facultyId) => apiRequest(`/departments/${facultyId}`),
  getMajorsByDepartment: (departmentId) => apiRequest(`/majors/${departmentId}`),
  getMajors: () => apiRequest('/majors'),
  
  // 用户相关
  getUser: (username) => apiRequest(`/user/${username}`),
  updateProfile: (data) => apiRequest('/user/profile', 'PUT', data),
  uploadAvatar: (username, avatarFile) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('avatar', avatarFile);
    return apiRequest('/user/avatar', 'POST', formData);
  },
  changePassword: (data) => apiRequest('/user/change-password', 'POST', data),
  
  // 申请相关
  getApplications: (filters) => {
    const filteredParams = { ...filters };
    // 排除值为'all'的参数
    Object.keys(filteredParams).forEach(key => {
      if (filteredParams[key] === 'all') {
        delete filteredParams[key];
      }
    });
    const queryParams = new URLSearchParams(filteredParams).toString();
    return apiRequest(`/applications?${queryParams}`);
  },
  getApplication: (id) => apiRequest(`/applications/${id}`),
  createApplication: (data) => apiRequest('/applications', 'POST', data),
  updateApplication: (id, data) => apiRequest(`/applications/${id}`, 'PUT', data),
  deleteApplication: (id) => apiRequest(`/applications/${id}`, 'DELETE'),
  // 规则相关
  matchRules: (data) => apiRequest('/rules/match', 'POST', data),
  getStatistics: (studentId) => apiRequest(`/applications/statistics?studentId=${studentId}`),
  
  // 规则管理相关
  getRules: (filters) => {
    const filteredParams = { ...filters };
    // 排除值为'all'的参数
    Object.keys(filteredParams).forEach(key => {
      if (filteredParams[key] === 'all') {
        delete filteredParams[key];
      }
    });
    const queryParams = new URLSearchParams(filteredParams).toString();
    return apiRequest(`/rules?${queryParams}`);
  },
  getRule: (id) => apiRequest(`/rules/${id}`),
  createRule: (data) => apiRequest('/rules', 'POST', data),
  updateRule: (id, data) => apiRequest(`/rules/${id}`, 'PUT', data),
  deleteRule: (id) => apiRequest(`/rules/${id}`, 'DELETE'),
  toggleRuleStatus: (id) => apiRequest(`/rules/${id}/toggle-status`, 'PATCH'),
  
  // 学院管理相关API
  getFacultiesAdmin: () => apiRequest('/admin/faculties'),
  getFacultyAdmin: (facultyId) => apiRequest(`/admin/faculties/${facultyId}`),
  createFacultyAdmin: (data) => apiRequest('/admin/faculties', 'POST', data),
  updateFacultyAdmin: (facultyId, data) => apiRequest(`/admin/faculties/${facultyId}`, 'PUT', data),
  deleteFacultyAdmin: (facultyId) => apiRequest(`/admin/faculties/${facultyId}`, 'DELETE'),
  getDepartmentsAdmin: (facultyId = '') => {
    const queryParams = facultyId ? `?faculty_id=${facultyId}` : '';
    return apiRequest(`/admin/departments${queryParams}`);
  },
  getDepartmentAdmin: (departmentId) => apiRequest(`/admin/departments/${departmentId}`),
  createDepartmentAdmin: (data) => apiRequest('/admin/departments', 'POST', data),
  updateDepartmentAdmin: (departmentId, data) => apiRequest(`/admin/departments/${departmentId}`, 'PUT', data),
  deleteDepartmentAdmin: (departmentId) => apiRequest(`/admin/departments/${departmentId}`, 'DELETE'),
  getMajorsAdmin: (departmentId = '', facultyId = '') => {
    let queryParams = '';
    if (departmentId) {
      queryParams = `?department_id=${departmentId}`;
    } else if (facultyId) {
      queryParams = `?faculty_id=${facultyId}`;
    }
    return apiRequest(`/admin/majors${queryParams}`);
  },
  getMajorAdmin: (majorId) => apiRequest(`/admin/majors/${majorId}`),
  createMajorAdmin: (data) => apiRequest('/admin/majors', 'POST', data),
  updateMajorAdmin: (majorId, data) => apiRequest(`/admin/majors/${majorId}`, 'PUT', data),
  deleteMajorAdmin: (majorId) => apiRequest(`/admin/majors/${majorId}`, 'DELETE')
};