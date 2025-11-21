# -*- coding: utf-8 -*-
"""
申请管理蓝图 - 主文件

该文件是申请管理蓝图的入口，负责导入和注册各个子模块的路由
"""

from flask import Blueprint

# 创建蓝图实例
application_bp = Blueprint("application", __name__, url_prefix="/api")

# 导入子模块 - 确保所有路由被正确注册
from .application_utils import update_student_statistics
from .application_crud import *
from .application_review import *
from .application_statistics import *
from .application_system import *

# 导出蓝图供主应用使用
__all__ = ['application_bp']
