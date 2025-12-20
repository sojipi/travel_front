@echo off
chcp 65001 >nul
title Fix Vite Configuration

echo ==============================================
echo Fix Vite Configuration
echo ==============================================
echo.

echo [INFO] Checking Vite configuration...

REM Check if vite.config.js exists
if not exist "frontend\vite.config.js" (
    echo [ERROR] vite.config.js not found
    pause
    exit /b 1
)

echo [OK] vite.config.js found
echo.

REM Check if @vitejs/plugin-react is installed
if not exist "frontend\node_modules\@vitejs\plugin-react" (
    echo [WARNING] @vitejs/plugin-react is missing
    echo [INFO] Installing @vitejs/plugin-react...
    cd frontend
    npm install @vitejs/plugin-react
    cd ..
    if errorlevel 1 (
        echo [ERROR] Failed to install @vitejs/plugin-react
        pause
        exit /b 1
    )
    echo [OK] @vitejs/plugin-react installed
) else (
    echo [OK] @vitejs/plugin-react is installed
)

echo.
echo [INFO] Checking Vite installation...

if not exist "frontend\node_modules\vite" (
    echo [WARNING] vite is missing
    echo [INFO] Installing vite...
    cd frontend
    npm install vite
    cd ..
    if errorlevel 1 (
        echo [ERROR] Failed to install vite
        pause
        exit /b 1
    )
    echo [OK] vite installed
) else (
    echo [OK] vite is installed
)

echo.
echo [INFO] Checking React installation...

if not exist "frontend\node_modules\react" (
    echo [WARNING] react is missing
    echo [INFO] Installing react...
    cd frontend
    npm install react
    cd ..
    if errorlevel 1 (
        echo [ERROR] Failed to install react
        pause
        exit /b 1
    )
    echo [OK] react installed
) else (
    echo [OK] react is installed
)

if not exist "frontend\node_modules\react-dom" (
    echo [WARNING] react-dom is missing
    echo [INFO] Installing react-dom...
    cd frontend
    npm install react-dom
    cd ..
    if errorlevel 1 (
        echo [ERROR] Failed to install react-dom
        pause
        exit /b 1
    )
    echo [OK] react-dom installed
) else (
    echo [OK] react-dom is installed
)

echo.
echo [INFO] Verifying package.json configuration...

REM Check if package.json has the correct type
findstr /C:"\"type\": \"module\"" "frontend\package.json" >nul
if errorlevel 1 (
    echo [WARNING] package.json missing \"type\": \"module\"
    echo [INFO] Adding type module to package.json...
    powershell -Command "(Get-Content 'frontend\package.json' -Raw) -replace '(\"name\":.*?,)', '$1\n  \"type\": \"module\",' | Set-Content 'frontend\package.json'"
    if errorlevel 1 (
        echo [ERROR] Failed to update package.json
        pause
        exit /b 1
    )
    echo [OK] Added type module to package.json
) else (
    echo [OK] package.json has type module
)

echo.
echo ==============================================
echo Vite configuration fix complete!
echo ==============================================
echo.
echo You can now run the startup script to start the services.
echo.
pause