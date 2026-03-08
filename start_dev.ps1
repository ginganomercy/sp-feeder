# ============================================
# Smart Pet Feeder - PowerShell Quick Start
# ============================================

Write-Host ""
Write-Host "========================================"
Write-Host "  Smart Pet Feeder - Development"
Write-Host "========================================"
Write-Host ""

# Check if venv exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "[*] Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Check if dependencies installed
& python -c "import flask" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[WARN] Dependencies not installed!" -ForegroundColor Yellow
    Write-Host "[*] Installing dependencies..." -ForegroundColor Cyan
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "========================================"
Write-Host "  Environment Ready!"
Write-Host "========================================"
Write-Host ""
Write-Host "Virtual environment: " -NoNewline
Write-Host "ACTIVE" -ForegroundColor Green
Write-Host ""
Write-Host "Python version:"
python --version
Write-Host ""
Write-Host "Available commands:"
Write-Host "  - python app.py              : Run application" -ForegroundColor Cyan
Write-Host "  - python monitor.py          : Run MQTT monitor" -ForegroundColor Cyan
Write-Host "  - python setup_database.py   : Setup database" -ForegroundColor Cyan
Write-Host "  - deactivate                 : Exit virtual env" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================"
Write-Host ""
