package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"hd_golang/internal/model"
	"hd_golang/internal/service"
)

// RuleHandler 加分规则处理器
type RuleHandler struct {
	ruleService service.RuleService
}

// NewRuleHandler 创建规则处理器实例
func NewRuleHandler() *RuleHandler {
	return &RuleHandler{
		ruleService: service.NewRuleService(),
	}
}

// CreateRuleHandler 创建加分规则
func (h *RuleHandler) CreateRuleHandler(w http.ResponseWriter, r *http.Request) {
	// 解析请求体
	var rule model.Rule
	if err := json.NewDecoder(r.Body).Decode(&rule); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// 调用服务层创建规则
	if err := h.ruleService.CreateRule(&rule); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// 返回成功响应
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"id": rule.ID,
		"message": "Rule created successfully",
	})
}

// GetRuleHandler 获取加分规则详情
func (h *RuleHandler) GetRuleHandler(w http.ResponseWriter, r *http.Request) {
	// 从URL参数中获取规则ID
	idStr := r.URL.Query().Get("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		http.Error(w, "Invalid rule ID", http.StatusBadRequest)
		return
	}

	// 调用服务层获取规则详情
	rule, err := h.ruleService.GetRuleByID(id)
	if err != nil {
		http.Error(w, "Rule not found", http.StatusNotFound)
		return
	}

	// 返回规则详情
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(rule)
}

// GetRulesHandler 获取加分规则列表
func (h *RuleHandler) GetRulesHandler(w http.ResponseWriter, r *http.Request) {
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
	ruleType := r.URL.Query().Get("type")
	if ruleType != "" {
		filter["type"] = ruleType
	}
	status := r.URL.Query().Get("status")
	if status != "" {
		filter["status"] = status
	}

	// 调用服务层获取规则列表
	rules, total, err := h.ruleService.ListRules(filter, page, pageSize)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// 返回规则列表
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"data":  rules,
		"total": total,
		"page":  page,
		"pageSize": pageSize,
	})
}

// UpdateRuleHandler 更新加分规则
func (h *RuleHandler) UpdateRuleHandler(w http.ResponseWriter, r *http.Request) {
	// 解析请求体
	var rule model.Rule
	if err := json.NewDecoder(r.Body).Decode(&rule); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// 调用服务层更新规则
	if err := h.ruleService.UpdateRule(&rule); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// 返回成功响应
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"message": "Rule updated successfully"})
}

// DeleteRuleHandler 删除加分规则
func (h *RuleHandler) DeleteRuleHandler(w http.ResponseWriter, r *http.Request) {
	// 从URL参数中获取规则ID
	idStr := r.URL.Query().Get("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		http.Error(w, "Invalid rule ID", http.StatusBadRequest)
		return
	}

	// 调用服务层删除规则
	if err := h.ruleService.DeleteRule(id); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// 返回成功响应
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"message": "Rule deleted successfully"})
}

// ToggleRuleStatusHandler 切换规则状态（启用/禁用）
func (h *RuleHandler) ToggleRuleStatusHandler(w http.ResponseWriter, r *http.Request) {
	// 从URL参数中获取规则ID
	idStr := r.URL.Query().Get("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		http.Error(w, "Invalid rule ID", http.StatusBadRequest)
		return
	}

	// 解析查询参数
	activeStr := r.URL.Query().Get("active")
	active := activeStr == "true"

	// 调用服务层切换状态
	err = h.ruleService.ToggleRuleStatus(id, active)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// 返回成功响应
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"id": id,
		"status": active,
		"message": "Rule status updated successfully",
	})
}

// GetValidRulesHandler 获取有效的加分规则
func (h *RuleHandler) GetValidRulesHandler(w http.ResponseWriter, r *http.Request) {
	// 解析查询参数
	ruleTypeStr := r.URL.Query().Get("type")
	ruleType := model.RuleType(ruleTypeStr)

	// 调用服务层获取有效规则
	rules, err := h.ruleService.GetActiveRules(ruleType)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// 返回有效规则
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(rules)
}

// GetRuleTemplatesHandler 获取规则模板
func (h *RuleHandler) GetRuleTemplatesHandler(w http.ResponseWriter, r *http.Request) {
	// 解析查询参数
	templateTypeStr := r.URL.Query().Get("type")
	templateType := model.RuleType(templateTypeStr)

	// 调用服务层获取规则模板
	templates, err := h.ruleService.GetRuleTemplates(templateType)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// 返回规则模板
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(templates)
}

// ImportRulesHandler 导入规则（批量创建）
func (h *RuleHandler) ImportRulesHandler(w http.ResponseWriter, r *http.Request) {
	// 解析请求体
	var rules []model.Rule
	if err := json.NewDecoder(r.Body).Decode(&rules); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// 循环调用服务层创建规则
	for i := range rules {
		if err := h.ruleService.CreateRule(&rules[i]); err != nil {
			http.Error(w, fmt.Sprintf("导入规则 %d 失败: %s", i+1, err.Error()), http.StatusBadRequest)
			return
		}
	}

	// 返回成功响应
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"message": "Rules imported successfully"})
}