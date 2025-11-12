# PostgreSQL和pgAdmin连接故障排除指南

## 常见连接问题及解决方案

### 1. 连接被拒绝或超时

**症状**：
- 尝试连接时收到"Connection refused"或"Connection timeout"错误

**解决方案**：
- 确认PostgreSQL服务正在运行
  - Windows: 打开服务管理器，检查"PostgreSQL"服务状态
  - 命令行: `net start postgresql` (以管理员身份运行)
- 确认PostgreSQL正在监听正确的端口(5432)
  - 检查`postgresql.conf`文件中的`listen_addresses`和`port`设置
  - 默认路径: `D:\PostgreSQL\data\postgresql.conf`
- 确保防火墙未阻止5432端口
  - 检查Windows防火墙设置，添加5432端口的入站规则

### 2. 密码认证失败

**症状**：
- 收到"password authentication failed for user postgres"错误

**解决方案**：
- 确认使用正确的密码：`123456`
- 检查pg_hba.conf文件中的认证设置
  - 默认路径: `D:\PostgreSQL\data\pg_hba.conf`
  - 确保localhost连接使用md5或scram-sha-256认证方法
- 尝试重置postgres用户密码
  - 打开PostgreSQL安装目录下的SQL Shell(psql)
  - 连接到数据库后执行: `ALTER USER postgres WITH PASSWORD '123456';`

### 3. 找不到hd_golang数据库

**症状**：
- 连接成功但在数据库列表中看不到hd_golang

**解决方案**：
- 运行项目中的db_operations.js脚本创建数据库：`node db_operations.js`
- 或在pgAdmin的查询工具中手动创建：
  ```sql
  CREATE DATABASE hd_golang;
  ```
- 刷新数据库列表（右键点击"数据库"并选择"刷新"）

### 4. 用户表不存在

**症状**：
- 连接到hd_golang数据库但找不到users表

**解决方案**：
- 确保db_operations.js脚本已成功执行
- 或手动创建users表：
  ```sql
  CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
  );
  ```

### 5. 权限不足

**症状**：
- 收到"permission denied"错误

**解决方案**：
- 确保使用postgres用户连接，该用户有最高权限
- 授予必要的权限：
  ```sql
  GRANT ALL PRIVILEGES ON DATABASE hd_golang TO postgres;
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
  ```

## 验证数据库连接的方法

### 使用项目中的脚本验证

1. 运行`node verify_db_users.js`验证数据库连接和表结构
2. 运行`node view_all_accounts.js`验证用户数据是否可访问

### 使用命令行工具验证

如果安装了psql命令行工具：
```bash
psql -h localhost -p 5432 -U postgres -d hd_golang -c "SELECT * FROM users;"
```

### 检查PostgreSQL日志

查看PostgreSQL日志文件获取更详细的错误信息：
- 默认位置: `D:\PostgreSQL\data\pg_log\`

## 高级故障排除

### 检查PostgreSQL配置文件

1. 编辑`postgresql.conf`文件（通常位于`D:\PostgreSQL\data\`）
2. 确保以下设置正确：
   ```
   listen_addresses = '*'  # 允许所有IP连接
   port = 5432  # 端口号
   ```
3. 重启PostgreSQL服务使更改生效

### 检查pg_hba.conf文件

1. 编辑`pg_hba.conf`文件
2. 确保包含以下行以允许本地连接：
   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            md5
   # IPv6 local connections:
   host    all             all             ::1/128                 md5
   ```
3. 重启PostgreSQL服务使更改生效

### 重启PostgreSQL服务

1. 以管理员身份打开命令提示符
2. 停止服务: `net stop postgresql-x64-版本号`
3. 启动服务: `net start postgresql-x64-版本号`
   (将"版本号"替换为您安装的PostgreSQL版本)

## 联系支持

如果以上解决方案都无法解决问题，请考虑：

1. 检查项目的README文件是否有特定的数据库配置指南
2. 查看项目的issues或讨论区
3. 联系项目维护者获取进一步支持