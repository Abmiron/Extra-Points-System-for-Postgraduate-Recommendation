# GradPush 公网部署方案

## 一、项目概述

GradPush是一个基于Vue 3 + Flask的推免管理系统，包含前端和后端两个独立的模块：

- **前端**：Vue 3 + Vite，运行在3000端口（开发环境）
- **后端**：Flask + PostgreSQL，运行在5001端口（开发环境）

## 二、服务器环境准备

### 1. 服务器选择

推荐使用以下云服务器：
- 阿里云ECS（推荐配置：2核4G，40GB SSD，5Mbps带宽）
- 腾讯云CVM（推荐配置：2核4G，40GB SSD，5Mbps带宽）
- 华为云ECS（推荐配置：2核4G，40GB SSD，5Mbps带宽）

### 2. 操作系统

推荐使用：
- Ubuntu 22.04 LTS（长期支持版，稳定性好）

### 3. 环境配置

#### 3.1 更新系统

```bash
sudo apt update
sudo apt upgrade -y
```

#### 3.2 安装必要软件

```bash
sudo apt install -y git curl wget build-essential nginx certbot python3-certbot-nginx
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib
```

## 三、数据库配置

### 1. PostgreSQL安装与配置

#### 1.1 启动PostgreSQL服务

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 1.2 创建数据库用户和数据库

```bash
sudo -u postgres psql
```

在PostgreSQL命令行中执行：

```sql
CREATE USER gradpush WITH PASSWORD 'your_strong_password';
CREATE DATABASE gradpush OWNER gradpush;
GRANT ALL PRIVILEGES ON DATABASE gradpush TO gradpush;
\q
```

### 2. 数据库初始化

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 设置环境变量
export FLASK_APP=app.py
export FLASK_ENV=production

# 初始化数据库
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 四、后端部署

### 1. 配置修改

#### 1.1 修改配置文件 `backend/config.py`

```python
class Config:
    # 数据库配置 - 修改为生产环境配置
    SQLALCHEMY_DATABASE_URI = "postgresql://gradpush:your_strong_password@localhost:5432/gradpush"
    
    # 密钥配置 - 生产环境必须使用强密钥
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your_production_secret_key_here"
    
    # 其他配置保持不变...
```

#### 1.2 修改应用入口文件 `backend/app.py`

```python
# 修改调试模式为False
if __name__ == "__main__":
    app.run(debug=False, port=5001, use_reloader=False)
```

### 2. 使用Gunicorn部署Flask应用

#### 2.1 安装Gunicorn

```bash
pip install gunicorn
```

#### 2.2 创建Gunicorn配置文件 `backend/gunicorn.conf.py`

```python
bind = "127.0.0.1:5001"
workers = 4
worker_class = "gthread"
threads = 2
max_requests = 1000
max_requests_jitter = 50
```

#### 2.3 创建systemd服务文件 `/etc/systemd/system/gradpush-backend.service`

```ini
[Unit]
Description=GradPush Backend Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/path/to/gradpush/backend
ExecStart=/path/to/gradpush/backend/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=your_production_secret_key_here"

[Install]
WantedBy=multi-user.target
```

#### 2.4 启动后端服务

```bash
sudo systemctl daemon-reload
sudo systemctl start gradpush-backend
sudo systemctl enable gradpush-backend
```

## 五、前端部署

### 1. 安装Node.js

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2. 配置修改（已优化）

#### 2.1 API请求地址配置

**注意：** 前端API请求地址已经修改为相对路径，无需手动修改域名。

我们已经将 `frontend/utils/api.js` 中的硬编码URL修改为相对路径：

```javascript
// 旧配置（已修改）
// const API_BASE_URL = 'http://localhost:5001/api';

// 新配置 - 使用相对路径
const API_BASE_URL = '/api';

// 公开系统信息接口也已修改为相对路径
getPublicSystemInfo: async () => {
  // 旧配置（已修改）
  // const url = 'http://localhost:5001/public/system-info';
  
  // 新配置 - 使用相对路径
  const url = '/public/system-info';
  // 其他代码保持不变...
}
```

这样修改的好处：
1. 自动适应开发环境和生产环境
2. 自动使用当前页面的域名和协议（支持HTTPS）
3. 部署时无需手动修改URL配置
4. 提高了代码的可维护性

### 3. 构建前端应用

```bash
cd frontend
npm install
npm run build
```

### 4. 部署前端静态文件

将构建后的静态文件复制到Nginx的web根目录：

```bash
sudo cp -r frontend/dist/* /var/www/html/
```

## 六、Nginx配置

### 1. 创建Nginx配置文件 `/etc/nginx/sites-available/gradpush`

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    root /var/www/html;
    index index.html;

    # 前端静态文件处理
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:5001/api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 公开系统信息接口代理
    location /public {
        proxy_pass http://127.0.0.1:5001/public;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 文件上传下载代理
    location /uploads {
        proxy_pass http://127.0.0.1:5001/uploads;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. 启用Nginx配置

```bash
sudo ln -s /etc/nginx/sites-available/gradpush /etc/nginx/sites-enabled/
sudo nginx -t  # 测试配置文件是否正确
sudo systemctl reload nginx
```

## 七、SSL证书配置

### 1. 使用Certbot获取免费SSL证书

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 2. 配置自动续期

```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## 八、安全配置

### 1. 防火墙配置

```bash
sudo ufw enable
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw status
```

### 2. PostgreSQL安全配置

修改PostgreSQL配置文件 `/etc/postgresql/14/main/pg_hba.conf`（版本号可能不同）：

```
# 只允许本地连接
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

重启PostgreSQL服务：

```bash
sudo systemctl restart postgresql
```

### 3. 禁用不必要的服务

```bash
sudo systemctl stop postgresql
```

## 九、性能优化

### 1. Nginx性能优化

在 `/etc/nginx/nginx.conf` 的 `http` 块中添加：

```nginx
http {
    # ... 其他配置 ...
    
    # 性能优化配置
    worker_processes auto;
    worker_connections 1024;
    
    # 启用压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # 缓存静态文件
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }
}
```

### 2. 后端性能优化

#### 2.1 增加Gunicorn工作进程数

修改 `backend/gunicorn.conf.py`：

```python
workers = 8  # 根据服务器CPU核心数调整
```

#### 2.2 启用数据库连接池

在 `backend/config.py` 中添加：

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_timeout': 30,
    'pool_recycle': 1800
}
```

## 十、监控与维护

### 1. 日志查看

#### 1.1 Nginx日志

```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

#### 1.2 后端日志

```bash
sudo journalctl -u gradpush-backend -f
```

### 2. 定期备份

#### 2.1 数据库备份

创建备份脚本 `backup-db.sh`：

```bash
#!/bin/bash

BACKUP_DIR="/path/to/backup"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
sudo -u postgres pg_dump gradpush > $BACKUP_DIR/gradpush_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/gradpush_$DATE.sql

# 删除7天前的备份文件
find $BACKUP_DIR -name "gradpush_*.sql.gz" -mtime +7 -delete
```

设置定时任务：

```bash
crontab -e
```

添加以下内容（每天凌晨2点备份）：

```
0 2 * * * /path/to/backup-db.sh
```

#### 2.2 文件备份

备份上传的文件：

```bash
#!/bin/bash

BACKUP_DIR="/path/to/backup/files"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份上传的文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /path/to/gradpush/backend/uploads

# 删除7天前的备份文件
find $BACKUP_DIR -name "uploads_*.tar.gz" -mtime +7 -delete
```

设置定时任务：

```bash
crontab -e
```

添加以下内容（每天凌晨3点备份）：

```
0 3 * * * /path/to/backup-files.sh
```

## 十一、常见问题与解决方案

### 1. 前端无法连接后端API

- 检查Nginx配置中的代理设置
- 检查后端服务是否正常运行
- 检查防火墙设置
- 检查SSL证书是否有效

### 2. 数据库连接失败

- 检查数据库服务是否正常运行
- 检查数据库用户和密码是否正确
- 检查数据库配置文件中的连接字符串

### 3. 文件上传失败

- 检查文件上传目录的权限
- 检查Nginx的客户端最大体配置
- 检查后端的MAX_CONTENT_LENGTH配置

## 十二、部署验证

1. 访问 `https://your-domain.com` 检查前端是否正常显示
2. 尝试登录系统，检查是否能正常连接后端API
3. 尝试上传文件，检查文件上传功能是否正常
4. 检查数据库是否能正常存储数据

---

以上就是GradPush系统的公网部署方案。根据实际情况，你可能需要调整某些配置参数以适应你的服务器环境和需求。