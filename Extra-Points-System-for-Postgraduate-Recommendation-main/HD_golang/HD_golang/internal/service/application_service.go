package service

import (
	"errors"
	"hd_golang/internal/model"
	"hd_golang/internal/repository"
)

// ApplicationService 加分申请服务接口
type ApplicationService interface {
	CreateApplication(application *model.Application) error
	GetApplicationByID(id int) (*model.Application, error)
	GetStudentApplications(studentID int, filters map[string]interface{}, page, pageSize int) ([]model.Application, int, error)
	UpdateApplication(application *model.Application) error
	DeleteApplication(id int) error
	SubmitApplication(id int) error
	ApproveApplication(id int, reviewerID int, finalScore float64, remark string) error
	RejectApplication(id int, reviewerID int, remark string) error
	GetPendingApplications(filter map[string]interface{}, page, pageSize int) ([]model.Application, int, error)
	CalculateStudentScore(studentID int) (*model.ScoreCalculationResult, error)
	BatchReviewApplications(ids []int, status model.ApplicationStatus, reviewerID int, remark string) error
}

// applicationService 实现ApplicationService接口
type applicationService struct {
	appRepo repository.ApplicationRepository
}

// NewApplicationService 创建加分申请服务实例
func NewApplicationService() ApplicationService {
	return &applicationService{
		appRepo: repository.NewApplicationRepository(),
	}
}

// CreateApplication 创建加分申请
func (s *applicationService) CreateApplication(application *model.Application) error {
	// 验证必填字段
	if application.ProjectName == "" || application.Reason == "" {
		return errors.New("项目全称和加分依据不能为空")
	}

	// 验证项目全称长度
	if len(application.ProjectName) > 100 {
		return errors.New("项目全称不能超过100个字符")
	}

	// 验证加分依据长度
	if len(application.Reason) > 300 {
		return errors.New("加分依据不能超过300个字符")
	}

	// 验证奖项类型和作者排序
	if application.AwardType == model.AwardTypeGroup && application.AuthorOrder <= 0 {
		return errors.New("集体奖项必须填写作者排序")
	}

	// 设置默认状态为草稿
	application.Status = model.ApplicationStatusDraft

	// 调用仓库创建申请
	return s.appRepo.Create(application)
}

// GetApplicationByID 根据ID获取加分申请
func (s *applicationService) GetApplicationByID(id int) (*model.Application, error) {
	return s.appRepo.GetByID(id)
}

// GetStudentApplications 获取学生的加分申请列表
func (s *applicationService) GetStudentApplications(studentID int, filters map[string]interface{}, page, pageSize int) ([]model.Application, int, error) {
	offset := (page - 1) * pageSize
	return s.appRepo.GetByStudentID(studentID, filters, offset, pageSize)
}

// UpdateApplication 更新加分申请
func (s *applicationService) UpdateApplication(application *model.Application) error {
	// 只有草稿状态的申请可以修改
	app, err := s.appRepo.GetByID(application.ID)
	if err != nil {
		return err
	}
	if app.Status != model.ApplicationStatusDraft {
		return errors.New("只有草稿状态的申请可以修改")
	}

	// 验证字段（同CreateApplication）
	if application.ProjectName == "" || application.Reason == "" {
		return errors.New("项目全称和加分依据不能为空")
	}

	return s.appRepo.Update(application)
}

// DeleteApplication 删除加分申请
func (s *applicationService) DeleteApplication(id int) error {
	// 只有草稿状态的申请可以删除
	app, err := s.appRepo.GetByID(id)
	if err != nil {
		return err
	}
	if app.Status != model.ApplicationStatusDraft {
		return errors.New("只有草稿状态的申请可以删除")
	}

	return s.appRepo.Delete(id)
}

// SubmitApplication 提交加分申请审核
func (s *applicationService) SubmitApplication(id int) error {
	// 检查申请是否存在且为草稿状态
	app, err := s.appRepo.GetByID(id)
	if err != nil {
		return err
	}
	if app.Status != model.ApplicationStatusDraft {
		return errors.New("只有草稿状态的申请可以提交审核")
	}

	// 检查必填字段是否完整
	if app.ProjectName == "" || app.Reason == "" {
		return errors.New("项目全称和加分依据不能为空")
	}
	if app.AwardType == model.AwardTypeGroup && app.AuthorOrder <= 0 {
		return errors.New("集体奖项必须填写作者排序")
	}

	// 更新状态为待审核
	return s.appRepo.UpdateStatus(id, model.ApplicationStatusPending, 0, 0, "")
}

// ApproveApplication 审核通过加分申请
func (s *applicationService) ApproveApplication(id int, reviewerID int, finalScore float64, remark string) error {
	// 检查申请是否存在且为待审核状态
	app, err := s.appRepo.GetByID(id)
	if err != nil {
		return err
	}
	if app.Status != model.ApplicationStatusPending {
		return errors.New("只有待审核状态的申请可以处理")
	}

	// 更新状态为已通过
	return s.appRepo.UpdateStatus(id, model.ApplicationStatusApproved, reviewerID, finalScore, remark)
}

// RejectApplication 驳回加分申请
func (s *applicationService) RejectApplication(id int, reviewerID int, remark string) error {
	// 检查申请是否存在且为待审核状态
	app, err := s.appRepo.GetByID(id)
	if err != nil {
		return err
	}
	if app.Status != model.ApplicationStatusPending {
		return errors.New("只有待审核状态的申请可以处理")
	}

	// 驳回理由不能为空
	if remark == "" {
		return errors.New("驳回理由不能为空")
	}

	// 更新状态为未通过
	return s.appRepo.UpdateStatus(id, model.ApplicationStatusRejected, reviewerID, 0, remark)
}

// GetPendingApplications 获取待审核的申请列表
func (s *applicationService) GetPendingApplications(filter map[string]interface{}, page, pageSize int) ([]model.Application, int, error) {
	offset := (page - 1) * pageSize
	return s.appRepo.GetPending(filter, offset, pageSize)
}

// CalculateStudentScore 计算学生的总加分
func (s *applicationService) CalculateStudentScore(studentID int) (*model.ScoreCalculationResult, error) {
	return s.appRepo.CalculateStudentScore(studentID)
}

// BatchReviewApplications 批量审核申请
func (s *applicationService) BatchReviewApplications(ids []int, status model.ApplicationStatus, reviewerID int, remark string) error {
	// 实际实现中需要处理事务
	for _, id := range ids {
		if status == model.ApplicationStatusApproved {
			// 批量通过时，需要为每个申请设置最终分数
			// 这里简化处理，实际项目中可能需要更复杂的逻辑
			app, err := s.appRepo.GetByID(id)
			if err != nil {
				return err
			}
			if err := s.appRepo.UpdateStatus(id, status, reviewerID, app.SelfAssessedScore, remark); err != nil {
				return err
			}
		} else {
			// 批量驳回
			if err := s.appRepo.UpdateStatus(id, status, reviewerID, 0, remark); err != nil {
				return err
			}
		}
	}
	return nil
}