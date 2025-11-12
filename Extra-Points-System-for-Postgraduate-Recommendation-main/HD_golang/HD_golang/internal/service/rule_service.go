package service

import (
	"errors"
	"hd_golang/internal/model"
	"hd_golang/internal/repository"
)

// RuleService 加分规则服务接口
type RuleService interface {
	CreateRule(rule *model.Rule) error
	GetRuleByID(id int) (*model.Rule, error)
	GetActiveRules(ruleType model.RuleType) ([]model.Rule, error)
	UpdateRule(rule *model.Rule) error
	DeleteRule(id int) error
	ToggleRuleStatus(id int, active bool) error
	ListRules(filter map[string]interface{}, page, pageSize int) ([]model.Rule, int, error)
	GetRuleTemplates(ruleType model.RuleType) ([]model.RuleTemplate, error)
	CreateRuleTemplate(template *model.RuleTemplate) error
}

// ruleService 实现RuleService接口
type ruleService struct {
	ruleRepo repository.RuleRepository
}

// NewRuleService 创建规则服务实例
func NewRuleService() RuleService {
	return &ruleService{
		ruleRepo: repository.NewRuleRepository(),
	}
}

// CreateRule 创建加分规则
func (s *ruleService) CreateRule(rule *model.Rule) error {
	// 验证必填字段
	if rule.Name == "" || rule.Score < 0 {
		return errors.New("规则名称和分数不能为空且分数必须大于等于0")
	}

	// 设置默认版本
	if rule.Version == 0 {
		rule.Version = 1
	}

	// 调用仓库创建规则
	return s.ruleRepo.Create(rule)
}

// GetRuleByID 根据ID获取加分规则
func (s *ruleService) GetRuleByID(id int) (*model.Rule, error) {
	return s.ruleRepo.GetByID(id)
}

// GetActiveRules 获取有效的加分规则
func (s *ruleService) GetActiveRules(ruleType model.RuleType) ([]model.Rule, error) {
	return s.ruleRepo.GetActiveRules(ruleType)
}

// UpdateRule 更新加分规则
func (s *ruleService) UpdateRule(rule *model.Rule) error {
	// 验证必填字段
	if rule.Name == "" || rule.Score < 0 {
		return errors.New("规则名称和分数不能为空且分数必须大于等于0")
	}

	// 增加版本号
	oldRule, err := s.ruleRepo.GetByID(rule.ID)
	if err != nil {
		return err
	}
	rule.Version = oldRule.Version + 1

	return s.ruleRepo.Update(rule)
}

// DeleteRule 删除加分规则
func (s *ruleService) DeleteRule(id int) error {
	// 检查规则是否存在
	if _, err := s.ruleRepo.GetByID(id); err != nil {
		return err
	}

	return s.ruleRepo.Delete(id)
}

// ToggleRuleStatus 切换规则状态（启用/禁用）
func (s *ruleService) ToggleRuleStatus(id int, active bool) error {
	// 检查规则是否存在
	if _, err := s.ruleRepo.GetByID(id); err != nil {
		return err
	}

	return s.ruleRepo.ToggleStatus(id, active)
}

// ListRules 列出规则（带分页和筛选）
func (s *ruleService) ListRules(filter map[string]interface{}, page, pageSize int) ([]model.Rule, int, error) {
	offset := (page - 1) * pageSize
	return s.ruleRepo.ListRules(filter, offset, pageSize)
}

// GetRuleTemplates 获取规则模板
func (s *ruleService) GetRuleTemplates(ruleType model.RuleType) ([]model.RuleTemplate, error) {
	return s.ruleRepo.GetTemplates(ruleType)
}

// CreateRuleTemplate 创建规则模板
func (s *ruleService) CreateRuleTemplate(template *model.RuleTemplate) error {
	// 验证必填字段
	if template.Name == "" || template.Content == "" {
		return errors.New("模板名称和内容不能为空")
	}

	// 设置默认版本
	if template.Version == 0 {
		template.Version = 1
	}

	return s.ruleRepo.CreateTemplate(template)
}
