@echo off
cls

echo ==========================================
echo Starting Postgraduate Recommendation System...
echo ==========================================

REM Create logs directory if not exists
if not exist "logs" mkdir logs

REM Start backend service
cd "HD_golang\HD_golang"
start "Backend Service" /min app.exe
cd ..\..

echo Backend service starting...
ping 127.0.0.1 -n 4 >nul

REM Start frontend service
cd test-vue-app
start "Frontend Service" /min cmd /c "npm run dev"
cd ..

echo ==========================================
echo Services are starting...
echo Frontend URL: http://localhost:3000
echo Backend API URL: http://localhost:9001
echo Logs directory: logs\
echo ==========================================
echo Press any key to exit...
pause