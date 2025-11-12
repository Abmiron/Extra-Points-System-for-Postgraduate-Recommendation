@echo off

mkdir logs 2>nul

REM Start backend service
start "Backend Service" HD_golang\HD_golang\app.exe

REM Wait for backend to start
ping 127.0.0.1 -n 3 >nul

REM Start frontend service
start "Frontend Service" cmd /c "cd test-vue-app && npm install && npm run dev"

echo Services are starting...
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8080
echo Press any key to exit...
pause
