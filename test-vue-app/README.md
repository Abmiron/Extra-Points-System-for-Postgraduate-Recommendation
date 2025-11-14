启动后端：使用PowerShell的语法设置环境变量并启动Flask服务
启动前端：在项目根目录下启动Vue前端服务，使用npm run dev命令

# 推免加分系统

一个基于Vue 3和Python Flask的推免加分管理系统。

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

## 后端设置

### 环境配置

1. 进入后端目录
```bash
cd backend
```

2. 激活虚拟环境
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

### 数据库配置

确保PostgreSQL已安装并运行，然后创建数据库：
```sql
CREATE DATABASE test_vue_app;
```

更新`backend/config.py`中的数据库连接信息：
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost:5432/test_vue_app'
```

### 初始化数据库

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 运行后端服务器

```bash
python app.py
```

## API接口

### 认证接口
- `POST /api/login` - 用户登录
- `POST /api/register` - 用户注册
- `POST /api/reset-password` - 密码重置
- `GET /api/user/<username>` - 获取用户信息

### 申请接口
- `GET /api/applications` - 获取所有申请
- `GET /api/applications/<id>` - 获取单个申请
- `POST /api/applications` - 创建申请
- `PUT /api/applications/<id>` - 更新申请
- `POST /api/applications/<id>/review` - 审核申请
- `DELETE /api/applications/<id>` - 删除申请
- `GET /api/applications/pending` - 获取待审核申请

## 注意事项

1. 本项目仅供学习和演示使用，实际部署时需要加强安全性
2. 数据库连接信息中的密码需要根据实际情况修改
3. 首次运行时需要初始化数据库
4. 前端API_BASE_URL可能需要根据后端运行的端口进行调整
