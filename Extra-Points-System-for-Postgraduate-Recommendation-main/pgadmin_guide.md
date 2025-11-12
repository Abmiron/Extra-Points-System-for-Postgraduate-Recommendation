# pgAdmin连接数据库和查看用户表指南

## 数据库连接参数

从项目配置中，我们获取到以下数据库连接信息：

- **主机地址**: localhost
- **端口**: 5432
- **用户名**: postgres
- **密码**: 123456
- **数据库名**: hd_golang

## pgAdmin操作步骤

### 1. 打开pgAdmin

- 确保您已安装pgAdmin（通常与PostgreSQL一起安装）
- 从开始菜单或桌面快捷方式启动pgAdmin

### 2. 创建新的服务器连接

1. 打开pgAdmin后，在左侧浏览器面板中右键点击"服务器"（Servers）
2. 选择"创建"（Create）→ "服务器..."（Server...）

### 3. 配置服务器连接

在弹出的"创建 - 服务器"窗口中：

#### 通用（General）选项卡
- **名称**: 输入一个名称，例如 "HD_Golang_Server"
- **评论**: 可选，输入描述性注释

#### 连接（Connection）选项卡
- **主机名/地址**: `localhost`
- **端口**: `5432`
- **维护数据库**: `postgres`（默认维护数据库）
- **用户名**: `postgres`
- **密码**: `123456`
- **保存密码**: 勾选此选项以便下次连接时不需要重新输入密码

#### SSL选项卡
- **SSL模式**: `禁用`（与项目配置中的DB_SSLMODE=disable一致）

点击"保存"按钮创建连接

### 4. 连接到服务器

- 服务器创建后，双击左侧面板中的服务器名称进行连接
- 系统可能会提示输入密码，输入`123456`

### 5. 访问hd_golang数据库

连接成功后，按照以下路径导航到hd_golang数据库：

1. 展开服务器节点（HD_Golang_Server）
2. 展开"数据库"（Databases）
3. 找到并展开`hd_golang`数据库

### 6. 查看用户表

1. 在hd_golang数据库下，展开"模式"（Schemas）→ "public" → "表"（Tables）
2. 您应该能看到`users`表

### 7. 查看表数据

有两种方法可以查看users表中的数据：

#### 方法一：使用pgAdmin的图形界面

1. 右键点击`users`表
2. 选择"查看/编辑数据"（View/Edit Data）→ "全部行"（All Rows）
3. 这将打开一个新的选项卡，显示表中的所有用户记录

#### 方法二：执行SQL查询

1. 右键点击`hd_golang`数据库
2. 选择"查询工具"（Query Tool）
3. 在查询编辑器中输入以下SQL：
   ```sql
   SELECT * FROM users;
   ```
4. 点击执行按钮（绿色三角形）或按F5键运行查询
5. 查询结果将显示在下方的结果窗格中

### 8. 使用项目中的自定义函数

项目中创建了一个方便查看用户的函数：

1. 在查询工具中输入：
   ```sql
   SELECT * FROM get_all_users();
   ```
2. 执行查询，查看按ID排序的所有用户

## 表结构说明

users表包含以下字段：

- **id**: 自动递增的主键
- **username**: 用户名（唯一）
- **password_hash**: 密码哈希值
- **role**: 用户角色（如admin、student等）
- **status**: 用户状态（默认为'active'）
- **created_at**: 创建时间
- **updated_at**: 更新时间
- **last_login**: 最后登录时间

## 常见操作示例

### 1. 查看特定角色的用户

```sql
SELECT id, username, role, status, created_at 
FROM users 
WHERE role = 'admin';  -- 或 'student'
```

### 2. 查看活跃用户

```sql
SELECT id, username, role, created_at 
FROM users 
WHERE status = 'active';
```

### 3. 统计各角色用户数量

```sql
SELECT role, COUNT(*) as count 
FROM users 
GROUP BY role;
```