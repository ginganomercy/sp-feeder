@echo off
REM ============================================
REM Smart Pet Feeder - Quick Start Script
REM ============================================
echo.
echo ========================================
echo   Smart Pet Feeder - Development
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Run: python -m venv venv
    exit /b 1
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo.
    echo [WARN] Dependencies not installed!
    echo [*] Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo ========================================
echo   Environment Ready!
echo ========================================
echo.
echo Virtual environment: ACTIVE
echo Python version:
python --version
echo.
echo Available commands:
echo   - python app.py          : Run application
echo   - python monitor.py      : Run MQTT monitor
echo   - python setup_database.py : Setup database
echo   - deactivate             : Exit virtual env
echo.
echo ========================================
