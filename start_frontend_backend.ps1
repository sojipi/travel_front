# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Travel Assistant - Frontend & Backend Services"

Write-Host ""
Write-Host "=============================================="
Write-Host "Travel Assistant - Frontend & Backend Startup"
Write-Host "=============================================="
Write-Host ""

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not installed"
    }
    Write-Host "[OK] Python installed: $pythonVersion"
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.8+"
    Write-Host "Visit: https://www.python.org/downloads/"
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js installation
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Node.js not installed"
    }
    Write-Host "[OK] Node.js installed: $nodeVersion"
} catch {
    Write-Host "[ERROR] Node.js not found. Please install Node.js"
    Write-Host "Visit: https://nodejs.org/"
    Read-Host "Press Enter to exit"
    exit 1
}

# Check virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "[INFO] Creating virtual environment..."
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment"
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Virtual environment created"
    Write-Host ""
} else {
    Write-Host "[OK] Virtual environment exists"
}

# Activate virtual environment and install backend dependencies
Write-Host "[INFO] Installing backend dependencies..."
& "venv\Scripts\Activate.ps1"
pip install flask flask-cors

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install backend dependencies"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Backend dependencies installed"
Write-Host ""

# Check frontend dependencies
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "[INFO] Installing frontend dependencies..."
    Set-Location frontend
    npm install
    Set-Location ..
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install frontend dependencies"
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Frontend dependencies installed"
    Write-Host ""
} else {
    Write-Host "[OK] Frontend dependencies exist"
    # Check if @vitejs/plugin-react is installed
    if (-not (Test-Path "frontend\node_modules\@vitejs\plugin-react")) {
        Write-Host "[WARNING] Missing @vitejs/plugin-react, reinstalling dependencies..."
        Set-Location frontend
        npm install
        Set-Location ..
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Failed to install frontend dependencies"
            Read-Host "Press Enter to exit"
            exit 1
        }
        Write-Host "[OK] Frontend dependencies reinstalled"
        Write-Host ""
    }
}

# Check .env file
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "[WARNING] .env file not found"
    Write-Host "Please copy .env.example to .env and add your API keys"
    Write-Host ""
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "[OK] Created .env file. Please edit it with your API keys"
        Write-Host "Example: MODELSCOPE_TOKEN=your_token_here"
        Write-Host ""
    }
}

# Kill processes using ports 8001 and 5173
Write-Host "[INFO] Checking for processes using ports 8001 and 5173..."
$port8001Processes = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue | Where-Object {$_.State -eq "Listen"}
foreach ($process in $port8001Processes) {
    Write-Host "[INFO] Terminating process $($process.OwningProcess) using port 8001..."
    Stop-Process -Id $process.OwningProcess -Force -ErrorAction SilentlyContinue
}

$port5173Processes = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | Where-Object {$_.State -eq "Listen"}
foreach ($process in $port5173Processes) {
    Write-Host "[INFO] Terminating process $($process.OwningProcess) using port 5173..."
    Stop-Process -Id $process.OwningProcess -Force -ErrorAction SilentlyContinue
}
Write-Host "[OK] Port cleanup completed"

# Start backend service
Write-Host "[INFO] Starting backend service..."
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & "venv\Scripts\Activate.ps1"
    Set-Location backend
    python main.py
} -Name "BackendService"

# Wait for backend service to start
Write-Host "[INFO] Waiting for backend service to start..."
Start-Sleep -Seconds 5

# Check if backend is running
Write-Host "[INFO] Checking if backend service is running..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/docs" -UseBasicParsing -TimeoutSec 2
    Write-Host "[OK] Backend service is running"
} catch {
    Write-Host "[WARNING] Backend service may not be ready yet"
    Write-Host "[INFO] Continuing with frontend startup..."
}

# Start frontend service
Write-Host "[INFO] Starting frontend service..."
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD\frontend
    npm run dev
} -Name "FrontendService"

Write-Host ""
Write-Host "=============================================="
Write-Host "Services started successfully!"
Write-Host "Frontend URL: http://localhost:5173/"
Write-Host "Backend URL: http://localhost:8001/"
Write-Host "=============================================="
Write-Host ""
Write-Host "Press Ctrl+C to stop all services"

# Wait for user interruption
try {
    while ($true) {
        Start-Sleep -Seconds 1
        
        # Check job status
        $backendState = (Get-Job -Name "BackendService").State
        $frontendState = (Get-Job -Name "FrontendService").State
        
        if ($backendState -eq "Failed" -or $frontendState -eq "Failed") {
            Write-Host "[ERROR] One of the services failed to start"
            break
        }
        
        if ($backendState -eq "Stopped" -or $frontendState -eq "Stopped") {
            Write-Host "[INFO] One of the services has stopped"
            break
        }
    }
} finally {
    # Clean up jobs
    Write-Host "[INFO] Stopping all services..."
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    Write-Host "[OK] All services stopped"
}