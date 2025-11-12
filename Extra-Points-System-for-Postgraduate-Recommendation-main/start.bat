@echo off

mkdir logs 2>nul

REM 启动后端服务
start "后端服务" cmd /c "HD_golang\HD_golang\app.exe > logs\backend.log 2>&1"

REM 等待后端启动
ping 127.0.0.1 -n 3 >nul

REM 启动前端服务
start "前端服务" cmd /c "cd test-vue-app && npm install && npm run dev > logs\frontend.log 2>&1"

echo 服务启动中...
echo 前端: http://localhost:3000
echo 后端: http://localhost:8080
echo 日志文件在logs目录下
