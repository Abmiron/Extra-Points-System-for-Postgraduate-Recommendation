package model

import "time"

// RuleType 规则类型枚举
type RuleType string

const (
	RuleTypeAcademicJournal    RuleType = "academic_journal"
	RuleTypeCompetition        RuleType = "competition"
	RuleTypeInnovation         RuleType = "innovation"
	RuleTypeComprehensive      RuleType = "comprehensive"
)

// RuleStatus 规则状态枚举
type RuleStatus string

const (
	RuleStatusActive   RuleStatus = "active"
	RuleStatusInactive RuleStatus = "inactive"
)

// Rule 加分规则模型
type Rule struct {
	ID          int        `json:"id" db:"id"`
	Type        RuleType   `json:"type" db:"type"`
	Name        string     `json:"name" db:"name"`
	Description string     `json:"description" db:"description"`
	Level       string     `json:"level" db:"level"`
	Score       float64    `json:"score" db:"score"`
	Status      RuleStatus `json:"status" db:"status"`
	Version     int        `json:"version" db:"version"`
	CreatedAt   time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time  `json:"updated_at" db:"updated_at"`
}

// RuleTemplate 规则模板模型（用于内置模板）
type RuleTemplate struct {
	ID          int        `json:"id" db:"id"`
	Type        RuleType   `json:"type" db:"type"`
	Name        string     `json:"name" db:"name"`
	Content     string     `json:"content" db:"content"` // JSON格式的规则内容
	Description string     `json:"description" db:"description"`
	Version     int        `json:"version" db:"version"`
	CreatedAt   time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time  `json:"updated_at" db:"updated_at"`
}