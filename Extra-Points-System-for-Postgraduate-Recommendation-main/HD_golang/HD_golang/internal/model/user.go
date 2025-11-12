package model

import "time"

// UserRole 用户角色枚举
type UserRole string

const (
	RoleStudent UserRole = "student"
	RoleTeacher UserRole = "teacher"
	RoleAdmin   UserRole = "admin"
)

// UserStatus 用户状态枚举
type UserStatus string

const (
	UserStatusActive   UserStatus = "active"
	UserStatusDisabled UserStatus = "disabled"
)

// User 基础用户模型

type User struct {
	ID           int        `json:"id" db:"id"`
	Username     string     `json:"username" db:"username"`
	PasswordHash string     `json:"-" db:"password_hash"`
	Role         UserRole   `json:"role" db:"role"`
	Status       UserStatus `json:"status" db:"status"`
	CreatedAt    time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt    time.Time  `json:"updated_at" db:"updated_at"`
	LastLoginAt  time.Time  `json:"last_login_at" db:"last_login_at"`
}

// Student 学生信息扩展模型
type Student struct {
	User
	StudentID          string   `json:"student_id" db:"student_id"`
	Name               string   `json:"name" db:"name"`
	Department         string   `json:"department" db:"department"`
	Major              string   `json:"major" db:"major"`
	Gender             *string  `json:"gender" db:"gender"`
	CET4Score          *float64 `json:"cet4_score" db:"cet4_score"`
	CET6Score          *float64 `json:"cet6_score" db:"cet6_score"`
	AcademicScore      *float64 `json:"academic_score" db:"academic_score"`
	MajorRank          *int     `json:"major_rank" db:"major_rank"`
	MajorTotalStudents *int     `json:"major_total_students" db:"major_total_students"`
}

// Teacher 教师信息扩展模型
type Teacher struct {
	User
	Department string `json:"department" db:"department"`
	Name       string `json:"name" db:"name"`
}

// Admin 管理员信息扩展模型
type Admin struct {
	User
	Name string `json:"name" db:"name"`
}
