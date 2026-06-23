@echo off
cls

echo ================================
echo   Receipt OCR API - Startup
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.8 or higher.
    echo Visit: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Y Python is available
echo.

REM Check if requirements are installed
echo Checking dependencies...
python -m pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo X Failed to install dependencies
        pause
        exit /b 1
    )
    echo Y Dependencies installed
) else (
    echo Y All dependencies already installed
)

echo.
echo ================================
echo   Starting API Server
echo ================================
echo.
echo Launch Server at: http://localhost:8000
echo Documentation at: http://localhost:8000/docs
echo Health Check at:  http://localhost:8000/health
echo.
echo Press CTRL+C to stop the server
echo.

python -m uvicorn receipt_api:app --host 0.0.0.0 --port 8000

pause
