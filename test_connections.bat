@echo off
echo ==========================================
echo Project Moriarty Connection Test
echo ==========================================
echo.
echo This script will test connections between:
echo - PostgreSQL Database
echo - FastAPI Backend
echo - React Frontend
echo - Integration between components
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if required Python packages are available
echo Checking Python dependencies...

python -c "import requests" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  requests package not found. Installing...
    pip install requests
)

python -c "import psycopg2" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  psycopg2 package not found. Installing...
    pip install psycopg2-binary
)

echo.
echo Starting connection tests...
echo.

REM Run the Python test script
python test_connections.py

echo.
echo Connection test completed!
pause