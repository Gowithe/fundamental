@echo off
REM Stock Analyzer - Run Script for Windows

echo 🚀 Stock Analyzer - Starting...
echo.

REM Check if venv exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Run app
echo.
echo 🎯 Starting Flask server...
echo 📍 Open browser: http://localhost:5000
echo.
python app.py

pause
