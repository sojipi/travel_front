@echo off
chcp 65001 >nul
title Travel Assistant - Quick Start

echo ==============================================
echo Travel Assistant - Quick Frontend & Backend Start
echo ==============================================
echo.

REM Check and create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    py -m venv venv
)

REM Check if frontend dependencies exist
if not exist "frontend\node_modules\@vitejs\plugin-react" (
    echo Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
) else (
    REM Check if @vitejs/plugin-vue is installed
    if not exist "frontend\node_modules\@vitejs\plugin-vue" (
        echo Missing @vitejs/plugin-vue, reinstalling dependencies...
        cd frontend
        npm install
        cd ..
    )
)

REM Kill processes using ports 8001 and 5173
echo Checking for processes using ports 8001 and 5173...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8001" ^| find "LISTENING"') do (
    echo Terminating process %%a using port 8001...
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5173" ^| find "LISTENING"') do (
    echo Terminating process %%a using port 5173...
    taskkill /F /PID %%a >nul 2>&1
)
echo Port cleanup completed

REM Start backend service
echo Starting backend service...
start "Backend Service" cmd /k "call venv\Scripts\activate.bat && cd backend && python main.py"

REM Wait for backend service to start
echo Waiting for backend service to start...
timeout /t 5 /nobreak >nul

REM Check if backend is running
echo Checking if backend service is running...
curl -s http://localhost:8001/docs >nul 2>&1
if errorlevel 1 (
    echo Backend service may not be ready yet
    echo Continuing with frontend startup...
) else (
    echo Backend service is running
)

REM Start frontend service
echo Starting frontend service...
start "Frontend Service" cmd /k "cd frontend && npm run dev"

echo.
echo ==============================================
echo Services started successfully!
echo Frontend URL: http://localhost:5173/
echo Backend URL: http://localhost:8001/
echo ==============================================
echo.
echo Press any key to close this window...
pause >nul