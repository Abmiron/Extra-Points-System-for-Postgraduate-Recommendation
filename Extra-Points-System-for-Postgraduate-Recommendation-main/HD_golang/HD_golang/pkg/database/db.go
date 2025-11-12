package database

import (
	"database/sql"
	"fmt"
	"log"
	"hd_golang/internal/config"
	_ "github.com/lib/pq"
)

// DB 全局数据库连接对象
var DB *sql.DB

// InitDB 初始化数据库连接
func InitDB(cfg *config.Config) error {
	// 构建连接字符串
	connectionString := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
		cfg.Database.Host, cfg.Database.Port, cfg.Database.Username, cfg.Database.Password, cfg.Database.DBName, cfg.Database.SSLMode)

	// 打开数据库连接
	var err error
	DB, err = sql.Open(cfg.Database.Driver, connectionString)
	if err != nil {
		log.Printf("Error: Failed to open database connection: %v", err)
		return err // 返回错误，不允许应用程序在数据库连接失败的情况下继续运行
	}

	// 设置连接池参数
	DB.SetMaxIdleConns(cfg.Database.MaxIdleConns)
	DB.SetMaxOpenConns(cfg.Database.MaxOpenConns)
	DB.SetConnMaxLifetime(cfg.Database.ConnMaxLifetime)

	// 测试连接
	if err = DB.Ping(); err != nil {
		log.Printf("Error: Failed to ping database: %v", err)
		return err // 返回错误，确保数据库连接成功
	}

	log.Println("Database connection established successfully")
	return nil
}

// CloseDB 关闭数据库连接
func CloseDB() {
	if DB != nil {
		if err := DB.Close(); err != nil {
			log.Printf("Warning: Error closing database connection: %v", err)
		}
	}
}