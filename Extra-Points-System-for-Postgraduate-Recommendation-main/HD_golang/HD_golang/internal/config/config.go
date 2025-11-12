package config

import "time"

// Config 系统配置结构体
type Config struct {
	Server struct {
		Host         string        `yaml:"host"`
		Port         string        `yaml:"port"`
		ReadTimeout  time.Duration `yaml:"read_timeout"`
		WriteTimeout time.Duration `yaml:"write_timeout"`
		IdleTimeout  time.Duration `yaml:"idle_timeout"`
	} `yaml:"server"`
	Database struct {
		Driver          string        `yaml:"driver"`
		Host            string        `yaml:"host"`
		Port            string        `yaml:"port"`
		Username        string        `yaml:"username"`
		Password        string        `yaml:"password"`
		DBName          string        `yaml:"dbname"`
		SSLMode         string        `yaml:"sslmode"`
		MaxIdleConns    int           `yaml:"max_idle_conns"`
		MaxOpenConns    int           `yaml:"max_open_conns"`
		ConnMaxLifetime time.Duration `yaml:"conn_max_lifetime"`
	} `yaml:"database"`
	JWT struct {
		SecretKey      string        `yaml:"secret_key"`
		ExpirationTime time.Duration `yaml:"expiration_time"`
	} `yaml:"jwt"`
	File struct {
		UploadDir   string   `yaml:"upload_dir"`
		MaxFileSize int64    `yaml:"max_file_size"`
		AllowedExts []string `yaml:"allowed_exts"`
	} `yaml:"file"`
	System struct {
		AcademicYear         string `yaml:"academic_year"`
		ApplicationStartDate string `yaml:"application_start_date"`
		ApplicationEndDate   string `yaml:"application_end_date"`
	} `yaml:"system"`
}

// LoadConfig 加载配置文件（返回默认配置）
func LoadConfig() *Config {
	// 实际项目中应该从配置文件读取
	// 这里返回默认配置
	return &Config{
		Server: struct {
				Host         string        `yaml:"host"`
				Port         string        `yaml:"port"`
				ReadTimeout  time.Duration `yaml:"read_timeout"`
				WriteTimeout time.Duration `yaml:"write_timeout"`
				IdleTimeout  time.Duration `yaml:"idle_timeout"`
			}{"0.0.0.0", "9001", 15 * time.Second, 15 * time.Second, 60 * time.Second},
		Database: struct {
			Driver          string        `yaml:"driver"`
			Host            string        `yaml:"host"`
			Port            string        `yaml:"port"`
			Username        string        `yaml:"username"`
			Password        string        `yaml:"password"`
			DBName          string        `yaml:"dbname"`
			SSLMode         string        `yaml:"sslmode"`
			MaxIdleConns    int           `yaml:"max_idle_conns"`
			MaxOpenConns    int           `yaml:"max_open_conns"`
			ConnMaxLifetime time.Duration `yaml:"conn_max_lifetime"`
		}{"postgres", "localhost", "5432", "postgres", "admin", "postgres", "disable", 5, 100, 30 * time.Minute},
		JWT: struct {
			SecretKey      string        `yaml:"secret_key"`
			ExpirationTime time.Duration `yaml:"expiration_time"`
		}{"hd_golang_secret_key_2024", 24 * time.Hour},
		File: struct {
			UploadDir   string   `yaml:"upload_dir"`
			MaxFileSize int64    `yaml:"max_file_size"`
			AllowedExts []string `yaml:"allowed_exts"`
		}{"uploads", 10 * 1024 * 1024, []string{".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"}},
		System: struct {
			AcademicYear         string `yaml:"academic_year"`
			ApplicationStartDate string `yaml:"application_start_date"`
			ApplicationEndDate   string `yaml:"application_end_date"`
		}{"2024-2025", "2024-09-01", "2025-06-30"},
	}
}
