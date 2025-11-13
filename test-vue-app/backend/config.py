import os

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost:5432/test_vue_app?client_encoding=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'