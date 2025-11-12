package repository

import (
	"database/sql"
	"time"
	"hd_golang/internal/model"
	"hd_golang/pkg/database"
)

// RuleRepository 加分规则仓库接口
type RuleRepository interface {
	Create(rule *model.Rule) error
	GetByID(id int) (*model.Rule, error)
	GetActiveRules(ruleType model.RuleType) ([]model.Rule, error)
	Update(rule *model.Rule) error
	Delete(id int) error
	ToggleStatus(id int, active bool) error
	ListRules(filter map[string]interface{}, offset, limit int) ([]model.Rule, int, error)
	GetTemplates(ruleType model.RuleType) ([]model.RuleTemplate, error)
	CreateTemplate(template *model.RuleTemplate) error
}

// ruleRepository 实现RuleRepository接口
type ruleRepository struct {
	db *sql.DB
}

// NewRuleRepository 创建规则仓库实例
func NewRuleRepository() RuleRepository {
	return &ruleRepository{
		db: database.DB,
	}
}

// Create 创建加分规则
func (r *ruleRepository) Create(rule *model.Rule) error {
	query := `INSERT INTO rules (
		type, name, description, level, score, status, version,
		created_at, updated_at
	) VALUES (
		$1, $2, $3, $4, $5, $6, $7, $8, $9
	) RETURNING id`
	err := r.db.QueryRow(
		query,
		rule.Type,
		rule.Name,
		rule.Description,
		rule.Level,
		rule.Score,
		rule.Status,
		rule.Version,
		time.Now(),
		time.Now(),
	).Scan(&rule.ID)
	return err
}

// GetByID 根据ID获取加分规则
func (r *ruleRepository) GetByID(id int) (*model.Rule, error) {
	rule := &model.Rule{}
	query := `SELECT id, type, name, description, level, score, status, version,
		created_at, updated_at FROM rules WHERE id = $1`
	err := r.db.QueryRow(query, id).Scan(
		&rule.ID,
		&rule.Type,
		&rule.Name,
		&rule.Description,
		&rule.Level,
		&rule.Score,
		&rule.Status,
		&rule.Version,
		&rule.CreatedAt,
		&rule.UpdatedAt,
	)
	if err != nil {
		return nil, err
	}
	return rule, nil
}

// GetActiveRules 获取有效的加分规则
func (r *ruleRepository) GetActiveRules(ruleType model.RuleType) ([]model.Rule, error) {
	var rules []model.Rule
	query := `SELECT id, type, name, description, level, score, status, version,
		created_at, updated_at FROM rules WHERE type = $1 AND status = $2`
	rows, err := r.db.Query(query, ruleType, model.RuleStatusActive)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		rule := model.Rule{}
		if err := rows.Scan(
			&rule.ID,
			&rule.Type,
			&rule.Name,
			&rule.Description,
			&rule.Level,
			&rule.Score,
			&rule.Status,
			&rule.Version,
			&rule.CreatedAt,
			&rule.UpdatedAt,
		); err != nil {
			return nil, err
		}
		rules = append(rules, rule)
	}

	return rules, nil
}

// Update 更新加分规则
func (r *ruleRepository) Update(rule *model.Rule) error {
	query := `UPDATE rules SET
		type = $1, name = $2, description = $3, level = $4, score = $5,
		status = $6, version = $7, updated_at = $8
		WHERE id = $9`
	_, err := r.db.Exec(
		query,
		rule.Type,
		rule.Name,
		rule.Description,
		rule.Level,
		rule.Score,
		rule.Status,
		rule.Version,
		time.Now(),
		rule.ID,
	)
	return err
}

// Delete 删除加分规则
func (r *ruleRepository) Delete(id int) error {
	query := `DELETE FROM rules WHERE id = $1`
	_, err := r.db.Exec(query, id)
	return err
}

// ToggleStatus 切换规则状态（启用/禁用）
func (r *ruleRepository) ToggleStatus(id int, active bool) error {
	status := model.RuleStatusInactive
	if active {
		status = model.RuleStatusActive
	}
	query := `UPDATE rules SET status = $1, updated_at = $2 WHERE id = $3`
	_, err := r.db.Exec(query, status, time.Now(), id)
	return err
}

// ListRules 列出规则（带分页和筛选）
func (r *ruleRepository) ListRules(filter map[string]interface{}, offset, limit int) ([]model.Rule, int, error) {
	// 实际实现中需要根据filter构建查询条件
	rules := []model.Rule{}
	total := 0
	// 这里返回空列表，实际项目中需要实现完整的查询逻辑
	return rules, total, nil
}

// GetTemplates 获取规则模板
func (r *ruleRepository) GetTemplates(ruleType model.RuleType) ([]model.RuleTemplate, error) {
	var templates []model.RuleTemplate
	query := `SELECT id, type, name, content, description, version,
		created_at, updated_at FROM rule_templates WHERE type = $1`
	rows, err := r.db.Query(query, ruleType)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		template := model.RuleTemplate{}
		if err := rows.Scan(
			&template.ID,
			&template.Type,
			&template.Name,
			&template.Content,
			&template.Description,
			&template.Version,
			&template.CreatedAt,
			&template.UpdatedAt,
		); err != nil {
			return nil, err
		}
		templates = append(templates, template)
	}

	return templates, nil
}

// CreateTemplate 创建规则模板
func (r *ruleRepository) CreateTemplate(template *model.RuleTemplate) error {
	query := `INSERT INTO rule_templates (
		type, name, content, description, version,
		created_at, updated_at
	) VALUES (
		$1, $2, $3, $4, $5, $6, $7
	) RETURNING id`
	err := r.db.QueryRow(
		query,
		template.Type,
		template.Name,
		template.Content,
		template.Description,
		template.Version,
		time.Now(),
		time.Now(),
	).Scan(&template.ID)
	return err
}