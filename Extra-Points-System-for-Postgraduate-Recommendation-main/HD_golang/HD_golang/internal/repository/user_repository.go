package repository

import (
	"database/sql"
	"log"
	"time"
	
	"hd_golang/internal/model"
	"hd_golang/pkg/database"
)

// UserRepository 用户仓库接口
type UserRepository interface {
	GetByUsername(username string) (*model.User, error)
	GetStudentByID(id int) (*model.Student, error)
	GetTeacherByID(id int) (*model.Teacher, error)
	GetAdminByID(id int) (*model.Admin, error)
	CreateUser(user *model.User) error
	CreateStudent(student *model.Student) error
	CreateTeacher(teacher *model.Teacher) error
	DeleteUser(userID int) error
	UpdateUser(user *model.User) error
	UpdateLastLoginTime(userID int) error
	ListStudents(filter map[string]interface{}, offset, limit int) ([]model.Student, int, error)
	ListTeachers(filter map[string]interface{}, offset, limit int) ([]model.Teacher, int, error)
	ChangePassword(userID int, passwordHash string) error
	DisableUser(userID int) error
	EnableUser(userID int) error
}

// userRepository 实现UserRepository接口

type userRepository struct {
	db *sql.DB
}

// NewUserRepository 创建用户仓库实例
func NewUserRepository() UserRepository {
	return &userRepository{
		db: database.DB,
	}
}

// GetByUsername 根据用户名获取用户
func (r *userRepository) GetByUsername(username string) (*model.User, error) {
	user := &model.User{}
	query := `SELECT id, username, password_hash, role, status, created_at, updated_at, last_login FROM users WHERE username = $1`
	var lastLogin sql.NullTime // 使用sql.NullTime处理可能为NULL的时间字段
	err := r.db.QueryRow(query, username).Scan(
		&user.ID,
		&user.Username,
		&user.PasswordHash,
		&user.Role,
		&user.Status,
		&user.CreatedAt,
		&user.UpdatedAt,
		&lastLogin,
	)
	if err != nil {
		return nil, err
	}
	// 如果last_login不为NULL，则设置LastLoginAt
	if lastLogin.Valid {
		user.LastLoginAt = lastLogin.Time
	}
	return user, nil
}

// GetStudentByID 根据ID获取学生信息
func (r *userRepository) GetStudentByID(id int) (*model.Student, error) {
	student := &model.Student{}
	// 使用正确的关联字段名并包含student_id，只查询表中实际存在的字段
	query := `SELECT u.id, u.username, u.role, u.status, u.created_at, u.updated_at, u.last_login,
		s.student_id, s.name, s.department, s.major, s.gender
		FROM users u JOIN students s ON u.id = s.user_id WHERE u.id = $1`
	var lastLogin sql.NullTime // 使用sql.NullTime处理可能为NULL的时间字段
	var gender sql.NullString // 使用sql.NullString处理可能为NULL的gender字段
	err := r.db.QueryRow(query, id).Scan(
		&student.ID,
		&student.Username,
		&student.Role,
		&student.Status,
		&student.CreatedAt,
		&student.UpdatedAt,
		&lastLogin,
		&student.StudentID,
		&student.Name,
		&student.Department,
		&student.Major,
		&gender,
	)
	if err != nil {
		return nil, err
	}
	// 如果last_login不为NULL，则设置LastLoginAt
	if lastLogin.Valid {
		student.LastLoginAt = lastLogin.Time
	}
	// 如果gender不为NULL，则设置Gender
	if gender.Valid {
		student.Gender = &gender.String
	}
	return student, nil
}

// GetTeacherByID 根据ID获取教师信息
func (r *userRepository) GetTeacherByID(id int) (*model.Teacher, error) {
	teacher := &model.Teacher{}
	query := `SELECT u.id, u.username, u.role, u.status, u.created_at, u.updated_at, u.last_login,
		t.department, t.name FROM users u JOIN teachers t ON u.id = t.user_id WHERE u.id = $1`
	var lastLogin sql.NullTime // 使用sql.NullTime处理可能为NULL的时间字段
	err := r.db.QueryRow(query, id).Scan(
		&teacher.ID,
		&teacher.Username,
		&teacher.Role,
		&teacher.Status,
		&teacher.CreatedAt,
		&teacher.UpdatedAt,
		&lastLogin,
		&teacher.Department,
		&teacher.Name,
	)
	if err != nil {
		return nil, err
	}
	// 如果last_login不为NULL，则设置LastLoginAt
	if lastLogin.Valid {
		teacher.LastLoginAt = lastLogin.Time
	}
	return teacher, nil
}

// GetAdminByID 根据ID获取管理员信息
func (r *userRepository) GetAdminByID(id int) (*model.Admin, error) {
	admin := &model.Admin{}
	query := `SELECT u.id, u.username, u.role, u.status, u.created_at, u.updated_at, u.last_login,
		a.name FROM users u JOIN admins a ON u.id = a.user_id WHERE u.id = $1`
	var lastLogin sql.NullTime // 使用sql.NullTime处理可能为NULL的时间字段
	err := r.db.QueryRow(query, id).Scan(
		&admin.ID,
		&admin.Username,
		&admin.Role,
		&admin.Status,
		&admin.CreatedAt,
		&admin.UpdatedAt,
		&lastLogin,
		&admin.Name,
	)
	if err != nil {
		return nil, err
	}
	// 如果last_login不为NULL，则设置LastLoginAt
	if lastLogin.Valid {
		admin.LastLoginAt = lastLogin.Time
	}
	return admin, nil
}

// 其他方法的实现略...

// CreateUser 创建用户
func (r *userRepository) CreateUser(user *model.User) error {
	query := `INSERT INTO users (username, password_hash, role, status, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6) RETURNING id`
	err := r.db.QueryRow(query, user.Username, user.PasswordHash, user.Role, user.Status, time.Now(), time.Now()).Scan(&user.ID)
	return err
}

// CreateStudent 创建学生信息
func (r *userRepository) CreateStudent(student *model.Student) error {
	// 确保使用log包输出日志，而不是fmt包
	log.Println("CreateStudent方法被调用，开始处理学生数据")
	log.Printf("学生数据: ID=%d, Username=%s, Name=%s\n", 
		student.ID, student.Username, student.Name)

	// 修复：根据实际数据库结构，students表有自增的id主键
	// 将username作为student_id值，将用户ID作为user_id值
	query := `INSERT INTO students (student_id, user_id, name, department, major) 
			VALUES ($1, $2, $3, $4, $5) RETURNING id`
	log.Printf("执行SQL: %s, 参数: %s, %d, %s, %s, %s\n", 
		query, student.Username, student.ID, student.Name, student.Department, student.Major)
	// 获取插入后的自增ID
	err := r.db.QueryRow(query, student.Username, student.ID, student.Name, student.Department, student.Major).Scan(&student.ID)
	if err != nil {
		log.Printf("插入学生信息失败: %v\n", err)
		return err
	}

	log.Println("插入学生信息成功")
	return nil
}

// CreateTeacher 创建教师信息
func (r *userRepository) CreateTeacher(teacher *model.Teacher) error {
	query := `INSERT INTO teachers (user_id, name, department)
		VALUES ($1, $2, $3)`
	_, err := r.db.Exec(query, teacher.ID, teacher.Name, teacher.Department)
	return err
}

// DeleteUser 删除用户
func (r *userRepository) DeleteUser(userID int) error {
	query := `DELETE FROM users WHERE id = $1`
	_, err := r.db.Exec(query, userID)
	return err
}

// UpdateUser 更新用户信息
func (r *userRepository) UpdateUser(user *model.User) error {
	query := `UPDATE users SET status = $1, updated_at = $2 WHERE id = $3`
	_, err := r.db.Exec(query, user.Status, time.Now(), user.ID)
	return err
}

// UpdateLastLoginTime 更新最后登录时间
func (r *userRepository) UpdateLastLoginTime(userID int) error {
	query := `UPDATE users SET last_login = $1, updated_at = $2 WHERE id = $3`
	_, err := r.db.Exec(query, time.Now(), time.Now(), userID)
	return err
}

// ChangePassword 修改密码
func (r *userRepository) ChangePassword(userID int, passwordHash string) error {
	query := `UPDATE users SET password_hash = $1, updated_at = $2 WHERE id = $3`
	_, err := r.db.Exec(query, passwordHash, time.Now(), userID)
	return err
}

// DisableUser 禁用用户
func (r *userRepository) DisableUser(userID int) error {
	query := `UPDATE users SET status = $1, updated_at = $2 WHERE id = $3`
	_, err := r.db.Exec(query, model.UserStatusDisabled, time.Now(), userID)
	return err
}

// EnableUser 启用用户
func (r *userRepository) EnableUser(userID int) error {
	query := `UPDATE users SET status = $1, updated_at = $2 WHERE id = $3`
	_, err := r.db.Exec(query, model.UserStatusActive, time.Now(), userID)
	return err
}

// ListStudents 列出学生
func (r *userRepository) ListStudents(filter map[string]interface{}, offset, limit int) ([]model.Student, int, error) {
	// 基本查询语句，包含name字段和student_id字段
	// 修复：使用正确的关联字段名 u.id = s.user_id，且只查询表中实际存在的字段
	baseQuery := `SELECT u.id, u.username, u.role, u.status, u.created_at, u.updated_at, u.last_login,
		s.student_id, s.name, s.department, s.major, s.gender
		FROM users u JOIN students s ON u.id = s.user_id WHERE 1=1`
	
	// 这里应该实现根据filter条件构建查询，但为了简单起见，我们返回一个基本实现
	students := []model.Student{}
	query := baseQuery + " LIMIT $1 OFFSET $2"
	rows, err := r.db.Query(query, limit, offset)
	if err != nil {
		return nil, 0, err
	}
	defer rows.Close()
	
	for rows.Next() {
		var student model.Student
		var lastLogin sql.NullTime // 使用sql.NullTime处理可能为NULL的时间字段
		err := rows.Scan(
			&student.ID,
			&student.Username,
			&student.Role,
			&student.Status,
			&student.CreatedAt,
			&student.UpdatedAt,
			&lastLogin,
			&student.StudentID,
			&student.Name,
			&student.Department,
			&student.Major,
			&student.Gender,
		)
		if err != nil {
			return nil, 0, err
		}
		// 如果last_login不为NULL，则设置LastLoginAt
		if lastLogin.Valid {
			student.LastLoginAt = lastLogin.Time
		}
		students = append(students, student)
	}
	
	// 获取总数
	var total int
	// 修复：使用正确的关联字段名 u.id = s.user_id
	err = r.db.QueryRow("SELECT COUNT(*) FROM users u JOIN students s ON u.id = s.user_id WHERE 1=1").Scan(&total)
	if err != nil {
		return nil, 0, err
	}
	
	return students, total, nil
}

// ListTeachers 列出教师（带分页和筛选）
func (r *userRepository) ListTeachers(filter map[string]interface{}, offset, limit int) ([]model.Teacher, int, error) {
	// 实际实现中需要根据filter构建查询条件
	teachers := []model.Teacher{}
	total := 0
	// 这里返回空列表，实际项目中需要实现完整的查询逻辑
	return teachers, total, nil
}