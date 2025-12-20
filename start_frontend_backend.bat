@echo off
chcp 65001 >nul
title Travel Assistant - Frontend & Backend Services

echo.
echo ==============================================
echo Travel Assistant - Frontend & Backend Startup
echo ==============================================
echo.

REM Check Python installation
py --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    echo Visit: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python installed

REM Check Node.js installation
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js
    echo Visit: https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js installed

REM Check virtual environment
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    py -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo.
) else (
    echo [OK] Virtual environment exists
)

REM Activate virtual environment and install backend dependencies
echo [INFO] Installing backend dependencies...
call venv\Scripts\activate.bat
pip install flask flask-cors

if errorlevel 1 (
    echo [ERROR] Failed to install backend dependencies
    pause
    exit /b 1
)

echo [OK] Backend dependencies installed
echo.

REM Check frontend dependencies
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
    if errorlevel 1 (
        echo [ERROR] Failed to install frontend dependencies
        pause
        exit /b 1
    )
    echo [OK] Frontend dependencies installed
    echo.
) else (
    echo [OK] Frontend dependencies exist
    REM Check if @vitejs/plugin-react is installed
    if not exist "frontend\node_modules\@vitejs\plugin-react" (
        echo [WARNING] Missing @vitejs/plugin-react, reinstalling dependencies...
        cd frontend
        npm install
        cd ..
        if errorlevel 1 (
            echo [ERROR] Failed to install frontend dependencies
            pause
            exit /b 1
        )
        echo [OK] Frontend dependencies reinstalled
        echo.
    )
)

REM Check .env file
if not exist ".env" (
    echo.
    echo [WARNING] .env file not found
    echo Please copy .env.example to .env and add your API keys
    echo.
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] Created .env file. Please edit it with your API keys
        echo Example: MODELSCOPE_TOKEN=your_token_here
        echo.
    )
)

REM Kill processes using ports 8001 and 5173
echo [INFO] Checking for processes using ports 8001 and 5173...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8001" ^| find "LISTENING"') do (
    echo [INFO] Terminating process %%a using port 8001...
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5173" ^| find "LISTENING"') do (
    echo [INFO] Terminating process %%a using port 5173...
    taskkill /F /PID %%a >nul 2>&1
)
echo [OK] Port cleanup completed

echo [INFO] Starting backend service...
start /B "Backend Service" cmd /k "title Backend Service && chcp 65001 >nul && call venv\Scripts\activate.bat && cd backend && python main.py"

echo [INFO] Waiting for backend service to start...
timeout /t 5 /nobreak >nul

REM Check if backend is running
echo [INFO] Checking if backend service is running...
curl -s http://localhost:8001/docs >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Backend service may not be ready yet
    echo [INFO] Continuing with frontend startup...
) else (
    echo [OK] Backend service is running
)

echo [INFO] Starting frontend service...
start /B "Frontend Service" cmd /k "title Frontend Service && chcp 65001 >nul && cd frontend && npm run dev"

echo.
echo ==============================================
echo Services started successfully!
echo Frontend URL: http://localhost:5173/
echo Backend URL: http://localhost:8001/
echo ==============================================
echo.
echo Press any key to close this window (services will continue running)
pause >nul