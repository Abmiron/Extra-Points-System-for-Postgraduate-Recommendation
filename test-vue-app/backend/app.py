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

# 先创建数据库对象，再导入模型和路由
from models import User, Application
from routes import *

if __name__ == '__main__':
    app.run(debug=True)