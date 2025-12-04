// API请求工具
import { useAuthStore } from '../stores/auth';

const API_BASE_URL = 'http://localhost:5001/api';

// 封装API请求（支持JSON和文件上传）
async function apiRequest(endpoint, method = 'GET', data = null, token = null, timeout = 10000) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const options = {
    method,
    headers: {},
    credentials: 'include', // 确保发送cookies，支持session认证
    cache: 'no-cache' // 禁用缓存，确保获取最新数据
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
  
  // 添加超时控制
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  options.signal = controller.signal;
  
  try {
    const response = await fetch(url, options);
    clearTimeout(timeoutId);
    
    // 解析响应数据
    const responseData = await response.json();
    
    // 检查响应状态
    if (!response.ok) {
      throw new Error(responseData.message || '请求失败');
    }
    
    return responseData;
  } catch (error) {
    clearTimeout(timeoutId);
    
    // 处理超时错误
    if (error.name === 'AbortError') {
      throw new Error('请求超时，请检查网络连接或稍后重试');
    }
    
    console.error('API请求错误:', error);
    throw error;
  }
}

// 导出API函数
export default {
  // 基础请求方法
  apiRequest,
  // 认证相关
  login: (data) => apiRequest('/login', 'POST', data),
  register: (data) => apiRequest('/register', 'POST', data),
  resetPassword: (data) => apiRequest('/reset-password', 'POST', data),
  generateCaptcha: () => apiRequest('/generate-captcha', 'GET'),
  logout: () => apiRequest('/logout', 'POST'),
  sessionCheck: () => apiRequest('/session-check', 'GET'),
  getFaculties: () => apiRequest('/faculties'),
  getDepartmentsByFaculty: (facultyId) => apiRequest(`/departments/${facultyId}`),
  getMajorsByDepartment: (departmentId) => apiRequest(`/majors/${departmentId}`),
  getMajors: () => apiRequest('/majors'),
  
  // 用户相关
  getCurrentUser: (username) => apiRequest(`/user/current?username=${username}`),
  updateProfile: (data) => apiRequest('/user/profile', 'PUT', data),
  uploadAvatar: (username, avatarFile) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('avatar', avatarFile);
    return apiRequest('/user/avatar', 'POST', formData);
  },
  resetAvatar: (username, token) => {
    const formData = new FormData();
    formData.append('username', username);
    return apiRequest('/user/avatar/reset', 'POST', formData, token);
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
  createApplication: (data) => apiRequest('/applications', 'POST', data),
  updateApplication: (id, data) => apiRequest(`/applications/${id}`, 'PUT', data),

  getStatistics: (studentId) => apiRequest(`/students/statistics?studentId=${studentId}`),
    
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
  
  // 系统设置相关API
  getSystemSettings: () => apiRequest('/admin/system-settings', 'GET'),
  updateSystemSettings: (settingsData) => apiRequest('/admin/system-settings', 'PUT', settingsData),
  
  // 推免相关文件API
  uploadGraduateFile: (file, uploader = "admin", description = "", category = "graduate", facultyId = null) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("uploader", uploader);
    formData.append("description", description);
    formData.append("category", category);
    if (facultyId) {
      formData.append("faculty_id", facultyId);
    }
    return apiRequest("/admin/graduate-files", "POST", formData, null); // Fixed token parameter
  },
  getGraduateFiles: () => apiRequest("/admin/graduate-files", "GET"),
  deleteGraduateFile: (fileId) => apiRequest(`/admin/graduate-files/${fileId}`, "DELETE"),
  getPublicGraduateFiles: (facultyId = null) => {
    const queryParams = facultyId ? `?facultyId=${facultyId}` : '';
    return apiRequest(`/admin/public/graduate-files${queryParams}`, "GET");
  },
  
  // 公开的系统信息接口（无需登录权限）
  getPublicSystemInfo: async () => {
    // 直接请求公开接口，不使用API_BASE_URL中的/api前缀
    const url = 'http://localhost:5001/public/system-info';
    
    // 添加超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        },
        signal: controller.signal // 添加信号
      });
      clearTimeout(timeoutId); // 请求成功，清除超时定时器
      
      const responseData = await response.json();
      if (!response.ok) {
        throw new Error(responseData.message || '请求失败');
      }
      return responseData;
    } catch (error) {
      clearTimeout(timeoutId); // 清除超时定时器
      
      // 处理超时错误
      if (error.name === 'AbortError') {
        throw new Error('请求超时，请检查网络连接或稍后重试');
      }
      
      console.error('获取系统信息失败:', error);
      throw error;
    }
  },
  
  // 学院管理相关API
  getFacultiesAdmin: () => apiRequest('/admin/faculties'),
  createFacultyAdmin: (data) => apiRequest('/admin/faculties', 'POST', data),
  updateFacultyAdmin: (facultyId, data) => apiRequest(`/admin/faculties/${facultyId}`, 'PUT', data),
  deleteFacultyAdmin: (facultyId) => apiRequest(`/admin/faculties/${facultyId}`, 'DELETE'),
  getDepartmentsAdmin: (facultyId = '') => {
    const queryParams = facultyId ? `?faculty_id=${facultyId}` : '';
    return apiRequest(`/admin/departments${queryParams}`);
  },
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
  createMajorAdmin: (data) => apiRequest('/admin/majors', 'POST', data),
  updateMajorAdmin: (majorId, data) => apiRequest(`/admin/majors/${majorId}`, 'PUT', data),
  deleteMajorAdmin: (majorId) => apiRequest(`/admin/majors/${majorId}`, 'DELETE'),
  
  // 学生管理相关API
  getStudentsAdmin: (params = '') => {
    const queryParams = params ? `?${params}` : '';
    return apiRequest(`/students${queryParams}`);
  },
  updateStudentAdmin: (studentId, data) => apiRequest(`/students/${studentId}`, 'PUT', data),
  // 综合成绩计算相关API
  recalculateComprehensiveScores: (params) => {
    const queryParams = params ? new URLSearchParams(params).toString() : '';
    const endpoint = `/students/recalculate-comprehensive-scores${queryParams ? `?${queryParams}` : ''}`;
    return apiRequest(endpoint, 'POST');
  }
};