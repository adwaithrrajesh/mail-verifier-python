@echo off
REM Email Finder Application Startup Script for Windows
REM This script starts the Flask application on port 9080

echo 🚀 Starting Email Finder Application...
echo 📍 Port: 9080
echo 🌐 Access: http://localhost:9080
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run 'python -m venv venv' first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo 📦 Checking dependencies...
pip list | findstr "dnspython" >nul || (
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
)

REM Start the application
echo 🎯 Starting Flask application...
echo Press CTRL+C to stop the application
echo.

python -m mailscout

pause
