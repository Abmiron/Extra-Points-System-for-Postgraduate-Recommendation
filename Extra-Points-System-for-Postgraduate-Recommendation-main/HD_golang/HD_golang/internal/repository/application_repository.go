package repository

import (
	"database/sql"
	"time"
	"hd_golang/internal/model"
	"hd_golang/pkg/database"
)

// ApplicationRepository 加分申请仓库接口
type ApplicationRepository interface {
	Create(application *model.Application) error
	GetByID(id int) (*model.Application, error)
	GetByStudentID(studentID int, filters map[string]interface{}, offset, limit int) ([]model.Application, int, error)
	GetPending(filter map[string]interface{}, offset, limit int) ([]model.Application, int, error)
	Update(application *model.Application) error
	Delete(id int) error
	UpdateStatus(id int, status model.ApplicationStatus, reviewerID int, finalScore float64, remark string) error
	CalculateStudentScore(studentID int) (*model.ScoreCalculationResult, error)
	GetApplicationsByIDs(ids []int) ([]model.Application, error)
}

// applicationRepository 实现ApplicationRepository接口
type applicationRepository struct {
	db *sql.DB
}

// NewApplicationRepository 创建加分申请仓库实例
func NewApplicationRepository() ApplicationRepository {
	return &applicationRepository{
		db: database.DB,
	}
}

// Create 创建加分申请
func (r *applicationRepository) Create(application *model.Application) error {
	query := `INSERT INTO applications (
		student_id, type, project_name, award_date, award_level, award_type,
		author_order, self_assessed_score, reason, proof_files, status,
		created_at, updated_at
	) VALUES (
		$1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
	) RETURNING id`

	// 将proof_files转换为字符串存储（实际项目中可能需要JSON或数组类型）
	proofFilesStr := "" // 这里简化处理
	err := r.db.QueryRow(
		query,
		application.StudentID,
		application.Type,
		application.ProjectName,
		application.AwardDate,
		application.AwardLevel,
		application.AwardType,
		application.AuthorOrder,
		application.SelfAssessedScore,
		application.Reason,
		proofFilesStr,
		application.Status,
		time.Now(),
		time.Now(),
	).Scan(&application.ID)

	return err
}

// GetByID 根据ID获取加分申请
func (r *applicationRepository) GetByID(id int) (*model.Application, error) {
	application := &model.Application{}
	query := `SELECT id, student_id, type, project_name, award_date, award_level, award_type,
		author_order, self_assessed_score, reason, status, final_score, review_remark,
		reviewer_id, reviewed_at, created_at, updated_at
		FROM applications WHERE id = $1`
	err := r.db.QueryRow(query, id).Scan(
		&application.ID,
		&application.StudentID,
		&application.Type,
		&application.ProjectName,
		&application.AwardDate,
		&application.AwardLevel,
		&application.AwardType,
		&application.AuthorOrder,
		&application.SelfAssessedScore,
		&application.Reason,
		&application.Status,
		&application.FinalScore,
		&application.ReviewRemark,
		&application.ReviewerID,
		&application.ReviewedAt,
		&application.CreatedAt,
		&application.UpdatedAt,
	)
	if err != nil {
		return nil, err
	}
	// 实际项目中需要从proof_files字段解析出文件路径列表
	application.ProofFiles = []string{}
	return application, nil
}

// GetByStudentID 获取学生的加分申请列表
func (r *applicationRepository) GetByStudentID(studentID int, filters map[string]interface{}, offset, limit int) ([]model.Application, int, error) {
	// 实际实现中需要根据filters构建查询条件
	applications := []model.Application{}
	total := 0
	// 这里返回空列表，实际项目中需要实现完整的查询逻辑
	return applications, total, nil
}

// GetPending 获取待审核的申请列表
func (r *applicationRepository) GetPending(filter map[string]interface{}, offset, limit int) ([]model.Application, int, error) {
	// 实际实现中需要根据filter构建查询条件
	applications := []model.Application{}
	total := 0
	// 这里返回空列表，实际项目中需要实现完整的查询逻辑
	return applications, total, nil
}

// Update 更新加分申请
func (r *applicationRepository) Update(application *model.Application) error {
	// 将proof_files转换为字符串存储
	proofFilesStr := "" // 这里简化处理
	query := `UPDATE applications SET
		type = $1, project_name = $2, award_date = $3, award_level = $4, award_type = $5,
		author_order = $6, self_assessed_score = $7, reason = $8, proof_files = $9,
		updated_at = $10
		WHERE id = $11`
	_, err := r.db.Exec(
		query,
		application.Type,
		application.ProjectName,
		application.AwardDate,
		application.AwardLevel,
		application.AwardType,
		application.AuthorOrder,
		application.SelfAssessedScore,
		application.Reason,
		proofFilesStr,
		time.Now(),
		application.ID,
	)
	return err
}

// Delete 删除加分申请
func (r *applicationRepository) Delete(id int) error {
	query := `DELETE FROM applications WHERE id = $1`
	_, err := r.db.Exec(query, id)
	return err
}

// UpdateStatus 更新申请状态
func (r *applicationRepository) UpdateStatus(id int, status model.ApplicationStatus, reviewerID int, finalScore float64, remark string) error {
	query := `UPDATE applications SET
		status = $1, final_score = $2, review_remark = $3, reviewer_id = $4,
		reviewed_at = $5, updated_at = $6
		WHERE id = $7`
	_, err := r.db.Exec(
		query,
		status,
		finalScore,
		remark,
		reviewerID,
		time.Now(),
		time.Now(),
		id,
	)
	return err
}

// CalculateStudentScore 计算学生的总加分
func (r *applicationRepository) CalculateStudentScore(studentID int) (*model.ScoreCalculationResult, error) {
	result := &model.ScoreCalculationResult{}

	// 计算学术专长加分
	var academicScore float64
	queryAcademic := `SELECT COALESCE(SUM(final_score), 0) FROM applications WHERE student_id = $1 AND type = $2 AND status = $3`
	err := r.db.QueryRow(queryAcademic, studentID, model.ApplicationTypeAcademic, model.ApplicationStatusApproved).Scan(&academicScore)
	if err != nil {
		return nil, err
	}
	// 学术专长成绩不超过15分
	if academicScore > 15 {
		academicScore = 15
	}
	result.AcademicScore = academicScore

	// 计算综合表现加分
	var comprehensiveScore float64
	queryComprehensive := `SELECT COALESCE(SUM(final_score), 0) FROM applications WHERE student_id = $1 AND type = $2 AND status = $3`
	err = r.db.QueryRow(queryComprehensive, studentID, model.ApplicationTypeComprehensive, model.ApplicationStatusApproved).Scan(&comprehensiveScore)
	if err != nil {
		return nil, err
	}
	// 综合表现成绩不超过5分
	if comprehensiveScore > 5 {
		comprehensiveScore = 5
	}
	result.ComprehensiveScore = comprehensiveScore

	// 计算考核综合成绩
	result.TotalAssessmentScore = academicScore + comprehensiveScore

	// 获取学业综合成绩
	var academicResultScore float64
	queryAcademicResult := `SELECT academic_score FROM students WHERE user_id = $1`
	err = r.db.QueryRow(queryAcademicResult, studentID).Scan(&academicResultScore)
	if err != nil {
		return nil, err
	}

	// 计算最终推免综合成绩
	result.FinalScore = academicResultScore*0.8 + result.TotalAssessmentScore

	return result, nil
}

// GetApplicationsByIDs 根据ID列表获取申请
func (r *applicationRepository) GetApplicationsByIDs(ids []int) ([]model.Application, error) {
	// 实际实现中需要使用IN子句查询多个ID
	applications := []model.Application{}
	// 这里返回空列表，实际项目中需要实现完整的查询逻辑
	return applications, nil
}