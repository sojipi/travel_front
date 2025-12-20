@echo off
chcp 65001 >nul
title Reset Frontend Dependencies

echo ==============================================
echo Reset Frontend Dependencies
echo ==============================================
echo.

echo [WARNING] This will completely reset frontend dependencies
echo All node_modules and package-lock.json will be removed
echo.
echo Press Y to continue or any other key to cancel
choice /c YN /n /m "Continue with reset? (Y/N): "
if errorlevel 2 goto :cancel

echo.
echo [INFO] Removing existing frontend dependencies...

if exist "frontend\node_modules" (
    rmdir /s /q "frontend\node_modules"
    echo [OK] Removed node_modules
)

if exist "frontend\package-lock.json" (
    del /q "frontend\package-lock.json"
    echo [OK] Removed package-lock.json
)

echo.
echo [INFO] Installing fresh dependencies...
cd frontend
npm install
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo.
    echo [INFO] Trying to clean npm cache and retry...
    npm cache clean --force
    npm install
    if errorlevel 1 (
        echo [ERROR] Still failed to install dependencies
        cd ..
        pause
        exit /b 1
    )
)
cd ..

echo.
echo [INFO] Verifying critical packages...

if not exist "frontend\node_modules\@vitejs\plugin-react" (
    echo [ERROR] @vitejs/plugin-react is missing
    cd frontend
    npm install @vitejs/plugin-react
    cd ..
)

if not exist "frontend\node_modules\vite" (
    echo [ERROR] vite is missing
    cd frontend
    npm install vite
    cd ..
)

if not exist "frontend\node_modules\react" (
    echo [ERROR] react is missing
    cd frontend
    npm install react
    cd ..
)

if not exist "frontend\node_modules\react-dom" (
    echo [ERROR] react-dom is missing
    cd frontend
    npm install react-dom
    cd ..
)

echo.
echo ==============================================
echo Frontend dependencies reset complete!
echo ==============================================
echo.
echo You can now run the startup script to start the services.
echo.
goto :end

:cancel
echo.
echo [INFO] Operation cancelled by user
echo.

:end
pause