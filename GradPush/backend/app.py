# -*- coding: utf-8 -*-
"""
Flask应用主入口文件

该文件负责初始化Flask应用，配置扩展，注册路由和模型，
是整个后端应用的启动点和核心配置文件。
"""

from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from flask_migrate import Migrate
import os
from werkzeug.utils import safe_join
from urllib.parse import quote
from extensions import db

# 创建应用实例
app = Flask(__name__)

# 配置CORS，支持跨域请求
CORS(app, origins="*", supports_credentials=True, allow_headers=["Content-Type", "Authorization", "X-Requested-With"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# 加载配置
app.config.from_object('config.Config')

# 配置JSON编码
app.config['JSON_AS_ASCII'] = False  # 支持中文输出
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'  # 设置响应头 charset

# 初始化数据库
db.init_app(app)
migrate = Migrate(app, db)

# 先创建数据库对象，再导入模型
from models import User, Application, Rule

# 导入并注册蓝图
from blueprints.auth_bp import auth_bp
from blueprints.user_bp import user_bp
from blueprints.application_bp import application_bp
from blueprints.rule_bp import rule_bp
from blueprints.admin_bp import admin_bp
from routes import main_bp

# 配置静态文件服务
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    response = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    # 使用安全的方式处理中文文件名
    response.headers['Content-Disposition'] = f'attachment; filename*=UTF-8''={quote(filename)}'
    return response

# 配置头像文件的静态服务
@app.route('/uploads/avatars/<path:filename>')
def uploaded_avatar(filename):
    response = send_from_directory(app.config['AVATAR_FOLDER'], filename)
    # 使用安全的方式处理中文文件名
    response.headers['Content-Disposition'] = f'attachment; filename*=UTF-8''={quote(filename)}'
    return response

# 配置普通文件的静态服务
@app.route('/uploads/files/<path:filename>')
def uploaded_app_file(filename):
    # 检查文件是否是PDF
    is_pdf = filename.lower().endswith('.pdf')
    response = send_from_directory(app.config['FILE_FOLDER'], filename)
    
    if is_pdf:
        # PDF文件设置为内联显示
        response.headers['Content-Disposition'] = f'inline; filename*=UTF-8''={quote(filename)}'
        response.headers['Content-Type'] = 'application/pdf'
    else:
        # 其他文件设置为附件下载
        response.headers['Content-Disposition'] = f'attachment; filename*=UTF-8''={quote(filename)}'
    
    return response

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(application_bp)
app.register_blueprint(rule_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(main_bp)



if __name__ == '__main__':
    app.run(debug=True, port=5001, use_reloader=False)