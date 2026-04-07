@echo off
REM FL-DP Healthcare Web Application Startup Script for Windows

echo ==========================================
echo FL-DP Healthcare Web Application
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [*] Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/Update dependencies
echo [*] Installing dependencies...
pip install -r App\requirements.txt --quiet

REM Create necessary directories
echo [*] Creating necessary directories...
if not exist "App\database" mkdir App\database
if not exist "App\uploads" mkdir App\uploads
if not exist "FL-DP-Healthcare\server" mkdir FL-DP-Healthcare\server
if not exist "FL-DP-Healthcare\client1\dataset" mkdir FL-DP-Healthcare\client1\dataset
if not exist "FL-DP-Healthcare\client2\dataset" mkdir FL-DP-Healthcare\client2\dataset
if not exist "FL-DP-Healthcare\client3\dataset" mkdir FL-DP-Healthcare\client3\dataset

echo [OK] Directories created
echo.

REM Check if .env exists, if not copy from example
if not exist "App\.env" (
    echo [*] Creating .env file from template...
    copy App\.env.example App\.env
    echo [OK] .env file created. Please update it with your settings.
)

echo.
echo ==========================================
echo Starting Application...
echo ==========================================
echo.
echo [*] Frontend: http://localhost:8000
echo [*] API Docs: http://localhost:8000/api/docs
echo [*] Alternative Docs: http://localhost:8000/api/redoc
echo.
echo [*] Default Admin Credentials:
echo    Username: admin
echo    Password: admin123
echo.
echo Press Ctrl+C to stop the server
echo ==========================================
echo.

REM Run the application
python -m uvicorn App.backend.main:app --reload --host 0.0.0.0 --port 8000

@REM Made with Bob
