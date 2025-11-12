package utils

import (
	"errors"
	"time"
	"github.com/golang-jwt/jwt/v4"
)

var (
	ErrInvalidToken = errors.New("invalid token")
	ErrExpiredToken = errors.New("token has expired")
)

// Claims 自定义JWT声明

type Claims struct {
	UserID   int    `json:"user_id"`
	Username string `json:"username"`
	Role     string `json:"role"`
	jwt.RegisteredClaims
}

// GenerateToken 生成JWT令牌
func GenerateToken(userID int, username, role, secretKey string, expirationTime time.Duration) (string, error) {
	// 设置过期时间
	expiration := time.Now().Add(expirationTime)

	// 创建声明
	claims := &Claims{
		UserID:   userID,
		Username: username,
		Role:     role,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(expiration),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			NotBefore: jwt.NewNumericDate(time.Now()),
		},
	}

	// 创建令牌
	 token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	// 签名并获取完整编码后的字符串令牌
	tokenString, err := token.SignedString([]byte(secretKey))
	if err != nil {
		return "", err
	}

	return tokenString, nil
}

// ParseToken 解析JWT令牌
func ParseToken(tokenString, secretKey string) (*Claims, error) {
	// 解析令牌
	claims := &Claims{}
	token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
		// 验证签名算法
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, ErrInvalidToken
		}
		return []byte(secretKey), nil
	})

	if err != nil {
		// 检查令牌是否过期
		if errors.Is(err, jwt.ErrTokenExpired) || errors.Is(err, jwt.ErrTokenNotValidYet) {
			return nil, ErrExpiredToken
		}
		return nil, ErrInvalidToken
	}

	// 检查令牌是否有效
	if !token.Valid {
		return nil, ErrInvalidToken
	}

	return claims, nil
}