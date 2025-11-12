package service

import (
	"errors"
	"hd_golang/internal/config"
	"hd_golang/internal/model"
	"hd_golang/internal/repository"
	"hd_golang/pkg/utils"
)

// UserService 用户服务接口
type UserService interface {
	Login(username, password string) (string, error)
	GetUserInfo(userID int, role string) (interface{}, error)
	UpdateUserStatus(userID int, status model.UserStatus) error
	ResetPassword(userID int) error
	CreateStudent(student *model.Student, password string) error
	CreateTeacher(teacher *model.Teacher, password string) error
	ListStudents(filter map[string]interface{}, page, pageSize int) ([]model.Student, int, error)
	ListTeachers(filter map[string]interface{}, page, pageSize int) ([]model.Teacher, int, error)
}

// userService 实现UserService接口
type userService struct {
	userRepo repository.UserRepository
	config   *config.Config
}

// NewUserService 创建用户服务实例
func NewUserService() UserService {
	return &userService{
		userRepo: repository.NewUserRepository(),
		config:   config.LoadConfig(),
	}
}

// Login 用户登录
func (s *userService) Login(username, password string) (string, error) {
	// 根据用户名获取用户
	user, err := s.userRepo.GetByUsername(username)
	if err != nil {
		return "", errors.New("用户名或密码错误")
	}

	// 检查用户状态
	if user.Status != model.UserStatusActive {
		return "", errors.New("用户已禁用")
	}

	// 验证密码
	if !utils.CheckPasswordHash(password, user.PasswordHash) {
		return "", errors.New("用户名或密码错误")
	}

	// 更新最后登录时间
	if err := s.userRepo.UpdateLastLoginTime(user.ID); err != nil {
		// 不影响登录，但记录错误
		// 实际项目中应该有日志记录
	}

	// 生成JWT令牌
	// 从配置中获取JWT密钥和过期时间
	token, err := utils.GenerateToken(user.ID, user.Username, string(user.Role), s.config.JWT.SecretKey, s.config.JWT.ExpirationTime)
	if err != nil {
		return "", errors.New("生成令牌失败")
	}

	return token, nil
}

// GetUserInfo 获取用户信息
func (s *userService) GetUserInfo(userID int, role string) (interface{}, error) {
	// 根据角色获取不同的用户信息
	if role == string(model.RoleStudent) {
		return s.userRepo.GetStudentByID(userID)
	} else if role == string(model.RoleTeacher) {
		return s.userRepo.GetTeacherByID(userID)
	} else if role == string(model.RoleAdmin) {
		return s.userRepo.GetAdminByID(userID)
	}
	return nil, errors.New("无效的用户角色")
}

// UpdateUserStatus 更新用户状态
func (s *userService) UpdateUserStatus(userID int, status model.UserStatus) error {
	user := &model.User{ID: userID, Status: status}
	return s.userRepo.UpdateUser(user)
}

// ResetPassword 重置用户密码
func (s *userService) ResetPassword(userID int) error {
	// 默认密码可以设置为学号/工号的后6位或其他规则
	// 这里简化处理，使用"123456"作为默认密码
	defaultPassword := "123456"
	passwordHash, err := utils.HashPassword(defaultPassword)
	if err != nil {
		return errors.New("密码加密失败")
	}
	return s.userRepo.ChangePassword(userID, passwordHash)
}

// CreateStudent 创建学生用户
func (s *userService) CreateStudent(student *model.Student, password string) error {
	// 检查用户名是否已存在
	if _, err := s.userRepo.GetByUsername(student.Username); err == nil {
		return errors.New("用户名已存在")
	}

	// 加密密码
	passwordHash, err := utils.HashPassword(password)
	if err != nil {
		return errors.New("密码加密失败")
	}

	// 创建基础用户
	user := &model.User{
		Username:     student.Username,
		PasswordHash: passwordHash,
		Role:         model.RoleStudent,
		Status:       model.UserStatusActive,
	}
	if err := s.userRepo.CreateUser(user); err != nil {
		return err
	}

	// 设置用户ID到学生对象
	student.ID = user.ID
	// 确保StudentID字段也设置了值，使用用户名作为学号
	student.StudentID = student.Username

	if err := s.userRepo.CreateStudent(student); err != nil {
		// 如果学生信息插入失败，删除已创建的用户
		_ = s.userRepo.DeleteUser(user.ID)
		return err
	}

	return nil
}

// CreateTeacher 创建教师用户
func (s *userService) CreateTeacher(teacher *model.Teacher, password string) error {
	// 检查用户名是否已存在
	if _, err := s.userRepo.GetByUsername(teacher.Username); err == nil {
		return errors.New("用户名已存在")
	}

	// 加密密码
	passwordHash, err := utils.HashPassword(password)
	if err != nil {
		return errors.New("密码加密失败")
	}

	// 创建基础用户
	user := &model.User{
		Username:     teacher.Username,
		PasswordHash: passwordHash,
		Role:         model.RoleTeacher,
		Status:       model.UserStatusActive,
	}
	if err := s.userRepo.CreateUser(user); err != nil {
		return err
	}

	// 将用户ID赋给教师
	teacher.ID = user.ID
	if err := s.userRepo.CreateTeacher(teacher); err != nil {
		// 如果教师信息插入失败，删除已创建的用户
		_ = s.userRepo.DeleteUser(user.ID)
		return err
	}

	return nil
}

// ListStudents 列出学生
func (s *userService) ListStudents(filter map[string]interface{}, page, pageSize int) ([]model.Student, int, error) {
	offset := (page - 1) * pageSize
	return s.userRepo.ListStudents(filter, offset, pageSize)
}

// ListTeachers 列出教师
func (s *userService) ListTeachers(filter map[string]interface{}, page, pageSize int) ([]model.Teacher, int, error) {
	offset := (page - 1) * pageSize
	return s.userRepo.ListTeachers(filter, offset, pageSize)
}
