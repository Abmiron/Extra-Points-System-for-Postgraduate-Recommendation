package middleware

import (
	"context"
	"net/http"
	"strings"
	"hd_golang/pkg/utils"
)

// UserInfo 用户信息上下文键
type UserInfo struct {
	UserID   int
	Username string
	Role     string
}

// JWTKey 上下文中存储用户信息的键
const JWTKey = "user_info"

// JWTAuthMiddleware JWT认证中间件
func JWTAuthMiddleware(secretKey string, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 从请求头中获取Authorization
		authHeader := r.Header.Get("Authorization")
		if authHeader == "" {
			http.Error(w, "Authorization header is required", http.StatusUnauthorized)
			return
		}

		// 验证Authorization格式
		parts := strings.SplitN(authHeader, " ", 2)
		if !(len(parts) == 2 && parts[0] == "Bearer") {
			http.Error(w, "Authorization header format must be Bearer {token}", http.StatusUnauthorized)
			return
		}

		// 解析JWT令牌
		claims, err := utils.ParseToken(parts[1], secretKey)
		if err != nil {
			if err == utils.ErrExpiredToken {
				http.Error(w, "Token has expired", http.StatusUnauthorized)
			} else {
				http.Error(w, "Invalid or malformed token", http.StatusUnauthorized)
			}
			return
		}

		// 将用户信息存储到上下文中
		userInfo := UserInfo{
			UserID:   claims.UserID,
			Username: claims.Username,
			Role:     claims.Role,
		}
		ctx := context.WithValue(r.Context(), JWTKey, userInfo)

		// 继续处理请求
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// RoleMiddleware 角色授权中间件
func RoleMiddleware(requiredRoles []string, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 从上下文中获取用户信息
		userInfo, ok := r.Context().Value(JWTKey).(UserInfo)
		if !ok {
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}

		// 检查用户角色是否在允许的角色列表中
		roleAllowed := false
		for _, role := range requiredRoles {
			if userInfo.Role == role {
				roleAllowed = true
				break
			}
		}

		if !roleAllowed {
			http.Error(w, "Forbidden: insufficient permissions", http.StatusForbidden)
			return
		}

		// 继续处理请求
		next.ServeHTTP(w, r)
	})
}

// GetUserInfoFromContext 从上下文中获取用户信息
func GetUserInfoFromContext(ctx context.Context) (UserInfo, bool) {
	userInfo, ok := ctx.Value(JWTKey).(UserInfo)
	return userInfo, ok
}