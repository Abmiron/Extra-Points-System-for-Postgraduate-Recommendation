package main

import (
	"context"
	"fmt"
	"hd_golang/internal/config"
	"hd_golang/internal/router"
	"hd_golang/pkg/database"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

func main() {
	// 加载配置
	cfg := config.LoadConfig()

	// 初始化数据库
	if err := database.InitDB(cfg); err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer func() {
		database.CloseDB()
		log.Println("Database connection closed")
	}()
	// 初始化数据库表结构
	if err := database.InitSchema(); err != nil {
		log.Fatalf("Failed to initialize database schema: %v", err)
	}

	// 初始化种子数据
	if err := database.SeedData(); err != nil {
		log.Fatalf("Failed to seed data: %v", err)
	}

	// 设置路由
	mux := router.SetupRouter()

	// 创建HTTP服务器
	serverAddr := fmt.Sprintf("%s:%s", cfg.Server.Host, cfg.Server.Port)
	server := &http.Server{
		Addr:         serverAddr,
		Handler:      mux,
		ReadTimeout:  time.Duration(cfg.Server.ReadTimeout) * time.Second,
		WriteTimeout: time.Duration(cfg.Server.WriteTimeout) * time.Second,
		IdleTimeout:  time.Duration(cfg.Server.IdleTimeout) * time.Second,
	}

	// 启动服务器
	go func() {
		log.Printf("Server starting on %s", serverAddr)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Failed to start server: %v", err)
		}
	}()

	// 等待中断信号以优雅地关闭服务器
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down server...")

	// 设置5秒超时来关闭服务器
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Println("Server exiting")
}
