package handler

import (
	"encoding/json"
	"net/http"
	"hd_golang/internal/middleware"
	"hd_golang/internal/model"
	"hd_golang/internal/service"
)

// UserHandler 用户处理器
type UserHandler struct {
	userService service.UserService
}

// NewUserHandler 创建用户处理器实例
func NewUserHandler() *UserHandler {
	return &UserHandler{
		userService: service.NewUserService(),
	}
}

// LoginHandler 处理用户登录请求
func (h *UserHandler) LoginHandler(w http.ResponseWriter, r *http.Request) {
	// 解析请求体
	var loginRequest struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}
	if err := json.NewDecoder(r.Body).Decode(&loginRequest); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// 调用服务层进行登录验证
	token, err := h.userService.Login(loginRequest.Username, loginRequest.Password)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	// 返回令牌
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"token": token})
}

// GetUserInfoHandler 处理获取用户信息请求
func (h *UserHandler) GetUserInfoHandler(w http.ResponseWriter, r *http.Request) {
	// 从上下文中获取用户信息
	userInfo, ok := middleware.GetUserInfoFromContext(r.Context())
	if !ok {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	// 调用服务层获取详细用户信息
	info, err := h.userService.GetUserInfo(userInfo.UserID, userInfo.Role)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// 返回用户信息
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(info)
}

// 管理员操作相关处理器

// ListStudentsHandler 列出学生列表（管理员用）
func (h *UserHandler) ListStudentsHandler(w http.ResponseWriter, r *http.Request) {
	// 实际实现中需要解析查询参数
	// 这里简化处理
	filter := map[string]interface{}{}
	page := 1
	pageSize := 10

	students, total, err := h.userService.ListStudents(filter, page, pageSize)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"data":  students,
		"total": total,
		"page":  page,
		"pageSize": pageSize,
	})
}

// ListTeachersHandler 列出教师列表（管理员用）
func (h *UserHandler) ListTeachersHandler(w http.ResponseWriter, r *http.Request) {
	// 实际实现中需要解析查询参数
	// 这里简化处理
	filter := map[string]interface{}{}
	page := 1
	pageSize := 10

	teachers, total, err := h.userService.ListTeachers(filter, page, pageSize)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"data":  teachers,
		"total": total,
		"page":  page,
		"pageSize": pageSize,
	})
}

// UpdateUserStatusHandler 更新用户状态（管理员用）
func (h *UserHandler) UpdateUserStatusHandler(w http.ResponseWriter, r *http.Request) {
	// 实际实现中需要从请求参数中获取用户ID和状态
	// 这里简化处理

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"message": "User status updated successfully"})
}

// RegisterHandler 处理用户注册请求
func (h *UserHandler) RegisterHandler(w http.ResponseWriter, r *http.Request) {
	// 解析请求体
	var registerRequest struct {
		Username string `json:"username"`
		Name     string `json:"name"`
		Password string `json:"password"`
		Role     string `json:"role"`
	}
	if err := json.NewDecoder(r.Body).Decode(&registerRequest); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// 参数验证
	if registerRequest.Username == "" || registerRequest.Name == "" || registerRequest.Password == "" || registerRequest.Role == "" {
		http.Error(w, "Missing required fields", http.StatusBadRequest)
		return
	}

	// 角色验证
	if registerRequest.Role != "student" && registerRequest.Role != "teacher" {
		http.Error(w, "Invalid role", http.StatusBadRequest)
		return
	}

	// 根据角色调用不同的创建方法
	if registerRequest.Role == "student" {
		student := &model.Student{
			User: model.User{
				Username: registerRequest.Username,
			},
			Name:       registerRequest.Name,
			Department: "计算机科学与技术系",
			Major:      "计算机科学与技术",
		}
		if err := h.userService.CreateStudent(student, registerRequest.Password); err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
	} else if registerRequest.Role == "teacher" {
		teacher := &model.Teacher{
			User: model.User{
				Username: registerRequest.Username,
			},
			TeacherID:  registerRequest.Username, // 明确设置teacher_id为username
			Name:       registerRequest.Name,
			Department: "计算机科学与技术系",
		}
		if err := h.userService.CreateTeacher(teacher, registerRequest.Password); err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
	}

	// 返回成功响应
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"message": "User registered successfully"})
}

// ResetPasswordHandler 重置用户密码（管理员用）
func (h *UserHandler) ResetPasswordHandler(w http.ResponseWriter, r *http.Request) {
	// 实际实现中需要从请求参数中获取用户ID
	// 这里简化处理

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"message": "Password reset successfully"})
}
