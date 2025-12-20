@echo off
chcp 65001 >nul
title Fix Frontend Dependencies

echo ==============================================
echo Fix Frontend Dependencies
echo ==============================================
echo.

echo [INFO] Checking frontend dependencies...

REM Check if node_modules exists
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
) else (
    echo [OK] node_modules exists
    
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
    ) else (
        echo [OK] @vitejs/plugin-react is installed
    )
)

echo.
echo [INFO] Verifying critical packages...

REM Check for other critical packages
if not exist "frontend\node_modules\vite" (
    echo [WARNING] Missing vite, installing...
    cd frontend
    npm install vite
    cd ..
)

if not exist "frontend\node_modules\react" (
    echo [WARNING] Missing react, installing...
    cd frontend
    npm install react
    cd ..
)

if not exist "frontend\node_modules\react-dom" (
    echo [WARNING] Missing react-dom, installing...
    cd frontend
    npm install react-dom
    cd ..
)

echo.
echo [INFO] Cleaning npm cache (optional)...
echo Press Y to clean npm cache or any other key to skip
choice /c YN /n /m "Clean npm cache? (Y/N): "
if errorlevel 2 goto :skip_cache
cd frontend
npm cache clean --force
cd ..

:skip_cache
echo.
echo ==============================================
echo Frontend dependencies check complete!
echo ==============================================
echo.
echo You can now run the startup script to start the services.
echo.
pause