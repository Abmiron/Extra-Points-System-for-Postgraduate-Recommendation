@echo off

echo === 停止现有Go进程 ===
taskkill /F /IM app.exe 2>nul
taskkill /F /IM main.exe 2>nul
echo 现有进程已停止（如果存在）

echo. 
echo === 进入Go项目目录 ===
cd "HD_golang\HD_golang"

echo. 
echo === 重新编译应用程序 ===
go build -o app.exe cmd/app/main.go
if %errorlevel% neq 0 (
    echo 编译失败！请检查错误信息
    pause
    exit /b %errorlevel%
)

echo 编译成功！

echo. 
echo === 启动应用程序 ===
echo 正在启动应用程序...
start "Go后端服务" app.exe

echo. 
echo === 重新启动完成 ===
echo 应用程序已在端口9001上启动
pause