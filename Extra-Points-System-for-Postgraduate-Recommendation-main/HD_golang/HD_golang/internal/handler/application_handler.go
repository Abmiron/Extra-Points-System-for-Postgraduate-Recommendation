package handler

import (
	"encoding/json"
	"net/http"
	"strconv"
	"hd_golang/internal/middleware"
	"hd_golang/internal/model"
	"hd_golang/internal/service"
)

// ApplicationHandler 加分申请处理器
type ApplicationHandler struct {
	appService service.ApplicationService
}

// NewApplicationHandler 创建加分申请处理器实例
func NewApplicationHandler() *ApplicationHandler {
	return &ApplicationHandler{
		appService: service.NewApplicationService(),
	}
}

// CreateApplicationHandler 创建加分申请
func (h *ApplicationHandler) CreateApplicationHandler(w http.ResponseWriter, r *http.Request) {
	// 从上下文中获取用户信息
	userInfo, ok := middleware.GetUserInfoFromContext(r.Context())
	if !ok {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	// 解析请求体
	var application model.Application
	if err := json.NewDecoder(r.Body).Decode(&application); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// 设置学生ID
	application.StudentID = userInfo.UserID

	// 调用服务层创建申请
	if err := h.appService.CreateApplication(&application); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// 返回成功响应
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"id": application.ID,
		"message": "Application created successfully",
	})
}

// GetApplicationHandler 获取加分申请详情
func (h *ApplicationHandler) GetApplicationHandler(w http.ResponseWriter, r *http.Request) {
	// 从URL参数中获取申请ID
	idStr := r.URL.Query().Get("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		http.Error(w, "Invalid application ID", http.StatusBadRequest)
		return
	}

	// 调用服务层获取申请详情
	application, err := h.appService.GetApplicationByID(id)
	if err != nil {
		http.Error(w, "Application not found", http.StatusNotFound)
		return
	}

	// 检查权限（学生只能查看自己的申请，老师和管理员可以查看所有）
	userInfo, ok := middleware.GetUserInfoFromContext(r.Context())
	if !ok {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	if userInfo.Role == string(model.RoleStudent) && application.StudentID != userInfo.UserID {
		http.Error(w, "Forbidden", http.StatusForbidden)
		return
	}

	// 返回申请详情
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(application)
}

// GetStudentApplicationsHandler 获取学生的申请列表
func (h *ApplicationHandler) GetStudentApplicationsHandler(w http.ResponseWriter, r *http.Request) {
	// 从上下文中获取用户信息
	userInfo, ok := middleware.GetUserInfoFromContext(r.Context())
	if !ok {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	// 解析查询参数
	page, _ := strconv.Atoi(r.URL.Query().Get("page"))
	pageSize, _ := strconv.Atoi(r.URL.Query().Get("pageSize"))
	if page <= 0 {
		page = 1
	}
	if pageSize <= 0 {
		pageSize = 10
	}

	// 构建筛选条件
	filter := map[string]interface{}{}
	status := r.URL.Query().Get("status")
	if status != "" {
		filter["status"] = status
	}
	sortBy := r.URL.Query().Get("sortBy")
	if sortBy != "" {
		filter["sortBy"] = sortBy
	}

	// 调用服务层获取申请列表
	applications, total, err := h.appService.GetStudentApplications(userInfo.UserID, filter, page, pageSize)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// 返回申请列表
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"data":  applications,
		"total": total,
		"page":  page,
		"pageSize": pageSize,
	})
}

// SubmitApplicationHandler 提交加分申请审核
func (h *ApplicationHandler) SubmitApplicationHandler(w http.ResponseWriter, r *http.Request) {
	// 从URL参数中获取申请ID
	idStr := r.URL.Query().Get("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		http.Error(w, "Invalid application ID", http.StatusBadRequest)
		return
	}

	// 调用服务层提交申请
	if err := h.appService.SubmitApplication(id); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// 返回成功响应
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"message": "Application submitted successfully"})
}

// UpdateApplicationHandler 更新加分申请
func (h *ApplicationHandler) UpdateApplicationHandler(w http.ResponseWriter, r *http.Request) {
	// 解析请求体
	var application model.Application
	if err := json.NewDecoder(r.Body).Decode(&application); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// 调用服务层更新申请
	if err := h.appService.UpdateApplication(&application); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// 返回成功响应
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"message": "Application updated successfully"})
}

	// DeleteApplicationHandler 删除加分申请
func (h *ApplicationHandler) DeleteApplicationHandler(w http.ResponseWriter, r *http.Request) {
	// 从URL参数中获取申请ID
	idStr := r.URL.Query().Get("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		http.Error(w, "Invalid application ID", http.StatusBadRequest)
		return
	}

	// 调用服务层删除申请
	if err := h.appService.DeleteApplication(id); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// 返回成功响应
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"message": "Application deleted successfully"})
}

	// 审核相关处理器

	// GetPendingApplicationsHandler 获取待审核的申请列表
func (h *ApplicationHandler) GetPendingApplicationsHandler(w http.ResponseWriter, r *http.Request) {
	// 解析查询参数
	page, _ := strconv.Atoi(r.URL.Query().Get("page"))
	pageSize, _ := strconv.Atoi(r.URL.Query().Get("pageSize"))
	if page <= 0 {
		page = 1
	}
	if pageSize <= 0 {
		pageSize = 10
	}

	// 构建筛选条件
	filter := map[string]interface{}{}
	department := r.URL.Query().Get("department")
	if department != "" {
		filter["department"] = department
	}
	major := r.URL.Query().Get("major")
	if major != "" {
		filter["major"] = major
	}
	appType := r.URL.Query().Get("type")
	if appType != "" {
		filter["type"] = appType
	}

	// 调用服务层获取待审核申请列表
	applications, total, err := h.appService.GetPendingApplications(filter, page, pageSize)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// 返回申请列表
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"data":  applications,
		"total": total,
		"page":  page,
		"pageSize": pageSize,
	})
}

	// ApproveApplicationHandler 审核通过加分申请
func (h *ApplicationHandler) ApproveApplicationHandler(w http.ResponseWriter, r *http.Request) {
	// 从上下文中获取用户信息
	userInfo, ok := middleware.GetUserInfoFromContext(r.Context())
	if !ok {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	// 解析请求体
	var approveRequest struct {
		ID         int     `json:"id"`
		FinalScore float64 `json:"final_score"`
		Remark     string  `json:"remark"`
	}
	if err := json.NewDecoder(r.Body).Decode(&approveRequest); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// 调用服务层审核通过申请
	if err := h.appService.ApproveApplication(
		approveRequest.ID,
		userInfo.UserID,
		approveRequest.FinalScore,
		approveRequest.Remark,
	); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// 返回成功响应
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"message": "Application approved successfully"})
}

	// RejectApplicationHandler 驳回加分申请
func (h *ApplicationHandler) RejectApplicationHandler(w http.ResponseWriter, r *http.Request) {
	// 从上下文中获取用户信息
	userInfo, ok := middleware.GetUserInfoFromContext(r.Context())
	if !ok {
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
		return
	}

	// 解析请求体
	var rejectRequest struct {
		ID     int    `json:"id"`
		Remark string `json:"remark"`
	}
	if err := json.NewDecoder(r.Body).Decode(&rejectRequest); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// 调用服务层驳回申请
	if err := h.appService.RejectApplication(
		rejectRequest.ID,
		userInfo.UserID,
		rejectRequest.Remark,
	); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// 返回成功响应
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"message": "Application rejected successfully"})
}

	// CalculateStudentScoreHandler 计算学生的总加分
func (h *ApplicationHandler) CalculateStudentScoreHandler(w http.ResponseWriter, r *http.Request) {
	// 从URL参数中获取学生ID
	studentIDStr := r.URL.Query().Get("studentID")
	studentID, err := strconv.Atoi(studentIDStr)
	if err != nil {
		http.Error(w, "Invalid student ID", http.StatusBadRequest)
		return
	}

	// 调用服务层计算学生分数
	scoreResult, err := h.appService.CalculateStudentScore(studentID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// 返回计算结果
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(scoreResult)
}