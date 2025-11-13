# -*- coding: utf-8 -*-
"""
应用配置文件

该文件定义了应用的配置参数，包括数据库连接、密钥配置等，
用于集中管理应用的配置信息，便于不同环境下的切换和维护。
"""

import os

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost:5432/test_vue_app?client_encoding=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'