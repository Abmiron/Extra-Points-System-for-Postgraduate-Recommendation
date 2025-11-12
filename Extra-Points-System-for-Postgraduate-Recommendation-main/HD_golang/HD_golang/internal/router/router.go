package router

import (
	"net/http"
	"hd_golang/internal/handler"
	"hd_golang/internal/middleware"
	"hd_golang/internal/model"
	"hd_golang/internal/config"
)

// SetupRouter 设置路由
func SetupRouter() *http.ServeMux {
	mux := http.NewServeMux()

	// 创建处理器实例
	userHandler := handler.NewUserHandler()
	appHandler := handler.NewApplicationHandler()
	ruleHandler := handler.NewRuleHandler()

	// 加载配置
	cfg := config.LoadConfig()

	// CORS中间件
	corsMiddleware := func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Access-Control-Allow-Origin", "*")
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
			w.Header().Set("Access-Control-Max-Age", "86400")

			if r.Method == "OPTIONS" {
				w.WriteHeader(http.StatusOK)
				return
			}

			next.ServeHTTP(w, r)
		})
	}

	// 日志中间件
	loggerMiddleware := func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// 这里可以添加日志记录逻辑
			next.ServeHTTP(w, r)
		})
	}

	// 通用错误处理中间件
	errorHandlerMiddleware := func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			defer func() {
				if err := recover(); err != nil {
					w.Header().Set("Content-Type", "application/json")
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(`{"error":"Internal server error"}`))
				}
			}()
			next.ServeHTTP(w, r)
		})
	}

	// 根路径重定向到健康检查
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		// 如果是根路径，则重定向到健康检查端点
		if r.URL.Path == "/" || r.URL.Path == "/api" {
			http.Redirect(w, r, "/api/health", http.StatusFound)
			return
		}
		// 其他未匹配的路径返回404
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		w.Write([]byte(`{"error":"Not Found"}`))
	})

	// 健康检查
	mux.HandleFunc("/api/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(`{"status":"ok"}`))
	})

	// 公开路由（无需认证）
	mux.HandleFunc("/api/auth/login", userHandler.LoginHandler)
	mux.HandleFunc("/api/auth/register", userHandler.RegisterHandler)

	// API路由组
	apiRouter := http.NewServeMux()

	// 用户相关路由
	userRouter := http.NewServeMux()
	userRouter.HandleFunc("/info", userHandler.GetUserInfoHandler) // 获取用户信息
	// 移除不存在的方法引用

	// 管理员用户管理路由
	adminUserRouter := http.NewServeMux()
	adminUserRouter.HandleFunc("/students", userHandler.ListStudentsHandler) // 学生列表
	adminUserRouter.HandleFunc("/teachers", userHandler.ListTeachersHandler) // 教师列表
	adminUserRouter.HandleFunc("/reset-password", userHandler.ResetPasswordHandler) // 重置密码
	adminUserRouter.HandleFunc("/update-status", userHandler.UpdateUserStatusHandler) // 更新用户状态
	// 移除不存在的方法引用

	// 加分申请路由
	appRouter := http.NewServeMux()
	appRouter.HandleFunc("/create", appHandler.CreateApplicationHandler)          // 创建申请
	appRouter.HandleFunc("/detail", appHandler.GetApplicationHandler)             // 获取申请详情
	appRouter.HandleFunc("/list", appHandler.GetStudentApplicationsHandler)       // 学生申请列表
	appRouter.HandleFunc("/submit", appHandler.SubmitApplicationHandler)          // 提交申请
	appRouter.HandleFunc("/update", appHandler.UpdateApplicationHandler)          // 更新申请
	appRouter.HandleFunc("/delete", appHandler.DeleteApplicationHandler)          // 删除申请

	// 审核相关路由
	reviewRouter := http.NewServeMux()
	reviewRouter.HandleFunc("/pending", appHandler.GetPendingApplicationsHandler) // 待审核列表
	reviewRouter.HandleFunc("/approve", appHandler.ApproveApplicationHandler)      // 审核通过
	reviewRouter.HandleFunc("/reject", appHandler.RejectApplicationHandler)        // 审核驳回

	// 分数计算路由
	scoreRouter := http.NewServeMux()
	scoreRouter.HandleFunc("/calculate", appHandler.CalculateStudentScoreHandler) // 计算学生分数

	// 规则管理路由
	ruleRouter := http.NewServeMux()
	ruleRouter.HandleFunc("/create", ruleHandler.CreateRuleHandler)           // 创建规则
	ruleRouter.HandleFunc("/detail", ruleHandler.GetRuleHandler)              // 获取规则详情
	ruleRouter.HandleFunc("/list", ruleHandler.GetRulesHandler)               // 规则列表
	ruleRouter.HandleFunc("/update", ruleHandler.UpdateRuleHandler)           // 更新规则
	ruleRouter.HandleFunc("/delete", ruleHandler.DeleteRuleHandler)           // 删除规则
	ruleRouter.HandleFunc("/toggle-status", ruleHandler.ToggleRuleStatusHandler) // 切换状态
	ruleRouter.HandleFunc("/valid", ruleHandler.GetValidRulesHandler)         // 有效规则列表
	ruleRouter.HandleFunc("/templates", ruleHandler.GetRuleTemplatesHandler)  // 规则模板
	ruleRouter.HandleFunc("/import", ruleHandler.ImportRulesHandler)          // 批量导入规则

	// 创建中间件包装的处理器
	jwtAuth := func(h http.Handler) http.Handler {
		return middleware.JWTAuthMiddleware(cfg.JWT.SecretKey, h)
	}

	adminAuth := func(h http.Handler) http.Handler {
		return middleware.RoleMiddleware([]string{string(model.RoleAdmin)}, jwtAuth(h))
	}

	reviewerAuth := func(h http.Handler) http.Handler {
		return middleware.RoleMiddleware([]string{string(model.RoleTeacher), string(model.RoleAdmin)}, jwtAuth(h))
	}

	// 注册子路由到API路由
	apiRouter.Handle("/user/", http.StripPrefix("/user", jwtAuth(userRouter)))                // 用户路由需要JWT认证
	apiRouter.Handle("/admin/user/", http.StripPrefix("/admin/user", adminAuth(adminUserRouter))) // 管理员路由需要admin权限
	apiRouter.Handle("/application/", http.StripPrefix("/application", jwtAuth(appRouter)))    // 申请路由需要JWT认证
	apiRouter.Handle("/review/", http.StripPrefix("/review", reviewerAuth(reviewRouter)))      // 审核路由需要teacher或admin权限
	apiRouter.Handle("/score/", http.StripPrefix("/score", jwtAuth(scoreRouter)))             // 分数路由需要JWT认证
	apiRouter.Handle("/rule/", http.StripPrefix("/rule", adminAuth(ruleRouter)))               // 规则管理需要admin权限

	// 应用中间件
	handlerWithMiddleware := errorHandlerMiddleware(loggerMiddleware(apiRouter))

	// 注册API路由，同时处理/api和/api/路径
	mux.HandleFunc("/api", func(w http.ResponseWriter, r *http.Request) {
		// 直接重定向到健康检查端点
		http.Redirect(w, r, "/api/health", http.StatusFound)
	})
	// 处理带斜杠的API路径
	mux.Handle("/api/", http.StripPrefix("/api", corsMiddleware(handlerWithMiddleware)))

	return mux
}