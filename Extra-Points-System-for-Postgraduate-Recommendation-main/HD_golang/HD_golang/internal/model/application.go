package model

import "time"

// ApplicationType 申请类型枚举
type ApplicationType string

const (
	ApplicationTypeAcademic     ApplicationType = "academic"
	ApplicationTypeComprehensive ApplicationType = "comprehensive"
)

// AwardLevel 奖项级别枚举
type AwardLevel string

const (
	AwardLevelNational    AwardLevel = "national"
	AwardLevelProvincial  AwardLevel = "provincial"
	AwardLevelCity        AwardLevel = "city"
	AwardLevelUniversity  AwardLevel = "university"
	AwardLevelCollege     AwardLevel = "college"
)

// AwardType 奖项类型枚举
type AwardType string

const (
	AwardTypeIndividual AwardType = "individual"
	AwardTypeGroup      AwardType = "group"
)

// ApplicationStatus 申请状态枚举
type ApplicationStatus string

const (
	ApplicationStatusDraft      ApplicationStatus = "draft"
	ApplicationStatusPending    ApplicationStatus = "pending"
	ApplicationStatusApproved   ApplicationStatus = "approved"
	ApplicationStatusRejected   ApplicationStatus = "rejected"
)

// Application 加分申请模型
type Application struct {
	ID                int                `json:"id" db:"id"`
	StudentID         int                `json:"student_id" db:"student_id"`
	Type              ApplicationType    `json:"type" db:"type"`
	ProjectName       string             `json:"project_name" db:"project_name"`
	AwardDate         time.Time          `json:"award_date" db:"award_date"`
	AwardLevel        AwardLevel         `json:"award_level" db:"award_level"`
	AwardType         AwardType          `json:"award_type" db:"award_type"`
	AuthorOrder       int                `json:"author_order" db:"author_order"` // 仅当奖项类型为集体时有效
	SelfAssessedScore float64            `json:"self_assessed_score" db:"self_assessed_score"`
	Reason            string             `json:"reason" db:"reason"`
	ProofFiles        []string           `json:"proof_files" db:"proof_files"` // 文件路径列表
	Status            ApplicationStatus  `json:"status" db:"status"`
	FinalScore        float64            `json:"final_score" db:"final_score"`
	ReviewRemark      string             `json:"review_remark" db:"review_remark"`
	ReviewerID        int                `json:"reviewer_id" db:"reviewer_id"`
	ReviewedAt        time.Time          `json:"reviewed_at" db:"reviewed_at"`
	CreatedAt         time.Time          `json:"created_at" db:"created_at"`
	UpdatedAt         time.Time          `json:"updated_at" db:"updated_at"`
}

// ScoreCalculationResult 成绩计算结果
type ScoreCalculationResult struct {
	AcademicScore      float64 `json:"academic_score"`
	ComprehensiveScore float64 `json:"comprehensive_score"`
	TotalAssessmentScore float64 `json:"total_assessment_score"` // 学术专长+综合表现
	FinalScore         float64 `json:"final_score"` // 学业成绩*80% + 考核综合成绩
}