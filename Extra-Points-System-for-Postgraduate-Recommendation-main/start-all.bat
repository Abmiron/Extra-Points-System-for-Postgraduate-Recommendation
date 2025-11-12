@echo off
cls

echo ==========================================
echo 正在启动加分推荐系统前后端服务...
echo ==========================================

REM 检查并创建日志目录
if not exist "logs" mkdir logs

REM 启动后端服务
echo 启动后端服务...
start "后端服务" /min cmd /c "d:\Code\VSCode\Extra-Points-System-for-Postgraduate-Recommendation-main\HD_golang\HD_golang\app.exe > logs\backend.log 2>&1"

REM 等待后端服务启动
choice /t 3 /d y /n >nul
echo 后端服务启动中...

REM 启动前端服务
echo 启动前端服务...
start "前端服务" /min cmd /c "cd test-vue-app && npm install && npm run dev > logs\frontend.log 2>&1"

echo ==========================================
echo 服务启动中，请稍候...
echo 前端访问地址: http://localhost:3000
echo 后端API地址: http://localhost:9001
echo 日志文件路径: logs目录下
echo ==========================================
echo 按任意键查看启动日志...
pause
start logs\backend.log
start logs\frontend.log
