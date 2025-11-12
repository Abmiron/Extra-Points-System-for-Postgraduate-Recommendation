@echo off

echo Stopping existing Go processes...
taskkill /F /IM app.exe 2>nul
taskkill /F /IM main.exe 2>nul
echo Existing processes stopped (if any)

echo. 
echo Changing to Go project directory...
cd "HD_golang\HD_golang"

echo. 
echo Building application...
go build -o app.exe cmd/app/main.go
if %errorlevel% neq 0 (
    echo Build failed! Please check error messages
    pause
    exit /b %errorlevel%
)

echo Build successful!

echo. 
echo Starting application...
echo Application is starting...
start "Go Backend Service" app.exe

echo. 
echo Restart completed!
echo Application started on port 9001
pause