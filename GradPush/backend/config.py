# -*- coding: utf-8 -*-
"""
应用配置文件

该文件定义了应用的配置参数，包括数据库连接、密钥配置等，
用于集中管理应用的配置信息，便于不同环境下的切换和维护。
"""

import os
from sqlalchemy.engine.url import URL

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost:5432/gradpush'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    AVATAR_FOLDER = os.path.join(UPLOAD_FOLDER, 'avatars')
    FILE_FOLDER = os.path.join(UPLOAD_FOLDER, 'files')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB