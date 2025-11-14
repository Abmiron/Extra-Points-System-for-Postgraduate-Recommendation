# -*- coding: utf-8 -*-
"""
Flask应用主入口文件

该文件负责初始化Flask应用，配置扩展，注册路由和模型，
是整个后端应用的启动点和核心配置文件。
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
import os
from extensions import db

# 创建应用实例
app = Flask(__name__)

# 配置CORS
CORS(app, resources={"/*": {"origins": "*"}})

# 加载配置
app.config.from_object('config.Config')

# 初始化数据库
db.init_app(app)
migrate = Migrate(app, db)

# 先创建数据库对象，再导入模型
from models import User, Application

# 导入并注册蓝图
from blueprints.auth_bp import auth_bp
from blueprints.user_bp import user_bp
from blueprints.application_bp import application_bp
from routes import main_bp

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(application_bp)
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5001, use_reloader=False)