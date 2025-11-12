package database

import (
	"fmt"
	"log"
	"time"
)

// InitSchema 初始化数据库表结构
func InitSchema() error {
	// 检查数据库连接
	if DB == nil {
		log.Printf("Error: database not initialized")
		return fmt.Errorf("database not initialized") // 不允许应用程序在数据库未初始化的情况下继续运行
	}

	log.Println("Initializing database schema...")

	// 创建用户表
	userTableSQL := `
	CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			username VARCHAR(100) UNIQUE NOT NULL,
			password_hash VARCHAR(255) NOT NULL,
			role VARCHAR(50) NOT NULL,
			status VARCHAR(50) NOT NULL DEFAULT 'active',
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			last_login TIMESTAMP
		);
	
	CREATE TABLE IF NOT EXISTS students (
			id SERIAL PRIMARY KEY,
			user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
			student_id VARCHAR(50) UNIQUE NOT NULL,
			name VARCHAR(100) NOT NULL,
			class VARCHAR(100),
			department VARCHAR(100),
			major VARCHAR(100),
			grade VARCHAR(50),
			nickname VARCHAR(100),
			avatar VARCHAR(255),
			gender VARCHAR(20),
			email VARCHAR(255),
			phone VARCHAR(20),
			description TEXT
		);
	
	CREATE TABLE IF NOT EXISTS teachers (
			id SERIAL PRIMARY KEY,
			user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
			teacher_id VARCHAR(50) UNIQUE NOT NULL,
			name VARCHAR(100) NOT NULL,
			department VARCHAR(100),
			position VARCHAR(100),
			nickname VARCHAR(100),
			avatar VARCHAR(255),
			gender VARCHAR(20),
			email VARCHAR(255),
			phone VARCHAR(20)
		);
	
	CREATE TABLE IF NOT EXISTS admins (
			id SERIAL PRIMARY KEY,
			user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
			admin_id VARCHAR(50) UNIQUE NOT NULL,
			name VARCHAR(100) NOT NULL,
			position VARCHAR(100),
			email VARCHAR(255),
			phone VARCHAR(20)
		);
	`

	// 创建加分规则表
	ruleTableSQL := `
	CREATE TABLE IF NOT EXISTS rules (
			id SERIAL PRIMARY KEY,
			rule_code VARCHAR(50) UNIQUE NOT NULL,
			type VARCHAR(50) NOT NULL,
			name VARCHAR(200) NOT NULL,
			description TEXT,
			score FLOAT NOT NULL,
			max_score FLOAT DEFAULT 0,
			multiplier FLOAT DEFAULT 1.0,
			status VARCHAR(50) NOT NULL DEFAULT 'active',
			created_by INTEGER REFERENCES users(id),
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			valid_from DATE,
			valid_until DATE
		);
	
	CREATE TABLE IF NOT EXISTS rule_templates (
			id SERIAL PRIMARY KEY,
			template_code VARCHAR(50) UNIQUE NOT NULL,
			type VARCHAR(50) NOT NULL,
			name VARCHAR(200) NOT NULL,
			description TEXT,
			score_template FLOAT NOT NULL,
			fields JSONB,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);
	`

	// 创建加分申请表
	applicationTableSQL := `
	CREATE TABLE IF NOT EXISTS applications (
			id SERIAL PRIMARY KEY,
			application_code VARCHAR(50) UNIQUE NOT NULL,
			student_id INTEGER REFERENCES students(id) NOT NULL,
			type VARCHAR(50) NOT NULL,
			project_name VARCHAR(255) NOT NULL,
			project_time DATE,
			award_level VARCHAR(50),
			department VARCHAR(100),
			organizer VARCHAR(200),
			self_score FLOAT DEFAULT 0,
			final_score FLOAT DEFAULT 0,
			status VARCHAR(50) NOT NULL DEFAULT 'draft',
			reason TEXT,
			submit_time TIMESTAMP,
			review_time TIMESTAMP,
			review_by INTEGER REFERENCES users(id),
			review_remark TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);
	
	CREATE TABLE IF NOT EXISTS application_files (
			id SERIAL PRIMARY KEY,
			application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
			file_name VARCHAR(255) NOT NULL,
			file_path VARCHAR(255) NOT NULL,
			file_size BIGINT NOT NULL,
			file_type VARCHAR(100),
			upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);
	`

	// 创建索引
	indexSQL := `
	-- 用户表索引
	CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
	CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
	CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
	
	-- 学生表索引
	CREATE INDEX IF NOT EXISTS idx_students_student_id ON students(student_id);
	CREATE INDEX IF NOT EXISTS idx_students_department ON students(department);
	CREATE INDEX IF NOT EXISTS idx_students_major ON students(major);
	CREATE INDEX IF NOT EXISTS idx_students_class ON students(class);
	
	-- 规则表索引
	CREATE INDEX IF NOT EXISTS idx_rules_type ON rules(type);
	CREATE INDEX IF NOT EXISTS idx_rules_status ON rules(status);
	CREATE INDEX IF NOT EXISTS idx_rules_valid ON rules(valid_from, valid_until);
	
	-- 申请表索引
	CREATE INDEX IF NOT EXISTS idx_applications_student_id ON applications(student_id);
	CREATE INDEX IF NOT EXISTS idx_applications_type ON applications(type);
	CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
	CREATE INDEX IF NOT EXISTS idx_applications_submit_time ON applications(submit_time);
	CREATE INDEX IF NOT EXISTS idx_applications_review_time ON applications(review_time);
	`

	// 执行SQL语句
	queries := []string{
		userTableSQL,
		ruleTableSQL,
		applicationTableSQL,
		indexSQL,
	}

	for _, query := range queries {
		if _, err := DB.Exec(query); err != nil {
			log.Printf("Error: failed to execute SQL query: %v", err)
			return err // 返回错误，确保数据库表结构创建成功
		}
	}

	log.Println("Database schema initialized successfully")
	return nil
}

// SeedData 初始化种子数据
func SeedData() error {
	// 检查是否需要创建默认管理员账户
	var count int
	err := DB.QueryRow("SELECT COUNT(*) FROM users WHERE role = 'admin'").Scan(&count)
	if err != nil {
		return fmt.Errorf("failed to check admin account: %v", err)
	}

	// 创建默认管理员账户
	if count == 0 {
		// 密码: admin123
		adminPasswordHash := "$2a$10$rP9d1nPq8cK8f1g6e5a4b3c2d1e0f9g8h7i6j5k4l3m2n1o0p9q8r7s6t5"
		var adminID int
		err := DB.QueryRow(`
			INSERT INTO users (username, password_hash, role, status, created_at, updated_at)
			VALUES ('admin', $1, 'admin', 'active', $2, $2)
			RETURNING id
		`, adminPasswordHash, time.Now()).Scan(&adminID)
		if err != nil {
			return fmt.Errorf("failed to create default admin account: %v", err)
		}

		// 创建管理员扩展信息
		_, err = DB.Exec(`
			INSERT INTO admins (user_id, admin_id, name, position)
			VALUES ($1, $2, $3, $4)
		`, adminID, "AD001", "系统管理员", "超级管理员")
		if err != nil {
			return fmt.Errorf("failed to create admin details: %v", err)
		}

		log.Println("Default admin account created successfully")
	}

	return nil
}
