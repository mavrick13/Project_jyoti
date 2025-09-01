@echo off
echo ==========================================
echo Project Moriarty Database Setup
echo ==========================================
echo.

REM Check if PostgreSQL is running
echo Checking PostgreSQL service...
sc query postgresql-x64-14 >nul 2>&1
if %errorlevel% neq 0 (
    echo PostgreSQL service not found. Trying alternative service names...
    sc query postgresql >nul 2>&1
    if %errorlevel% neq 0 (
        echo WARNING: PostgreSQL service may not be running.
        echo Please make sure PostgreSQL is installed and running.
        echo.
    )
)

echo.
echo This script will create the Project Moriarty database with:
echo - All required tables (users, farmers, inventory, tasks, messages)
echo - Sample inventory data with motors, controllers, solar panels, etc.
echo - Default admin user and installers
echo - Proper indexes and constraints
echo.

set /p PGUSER="Enter PostgreSQL username (default: postgres): "
if "%PGUSER%"=="" set PGUSER=postgres

set /p PGPASSWORD="Enter PostgreSQL password: "
if "%PGPASSWORD%"=="" (
    echo Error: Password is required!
    pause
    exit /b 1
)

set /p PGHOST="Enter PostgreSQL host (default: localhost): "
if "%PGHOST%"=="" set PGHOST=localhost

set /p PGPORT="Enter PostgreSQL port (default: 5432): "
if "%PGPORT%"=="" set PGPORT=5432

echo.
echo Connecting to PostgreSQL with:
echo Host: %PGHOST%
echo Port: %PGPORT%
echo User: %PGUSER%
echo.

REM Set environment variables for psql
set PGPASSWORD=%PGPASSWORD%

echo Creating database and tables...
echo.

REM Run the SQL script
psql -h %PGHOST% -p %PGPORT% -U %PGUSER% -d postgres -f "database_setup.sql"

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo ✅ DATABASE SETUP COMPLETED SUCCESSFULLY!
    echo ==========================================
    echo.
    echo Database: project_moriarty
    echo.
    echo Default Login Credentials:
    echo 📧 Admin: admin@jyotielectrotech.com
    echo 🔑 Password: admin123
    echo.
    echo 📧 Installer 1: installer1@jyotielectrotech.com  
    echo 🔑 Password: installer123
    echo.
    echo 📧 Installer 2: installer2@jyotielectrotech.com
    echo 🔑 Password: installer123
    echo.
    echo Next Steps:
    echo 1. Update your .env file with database credentials
    echo 2. Start the FastAPI backend: python main.py
    echo 3. Access API docs: http://localhost:8000/docs
    echo.
    echo The database includes sample inventory data with:
    echo - Motors (3HP, 5HP, 7.5HP with different pump heads)
    echo - Controllers, Solar Panels, BOS, Structure, Wire, Pipe
    echo - Ready for bulk upload testing
    echo.
) else (
    echo.
    echo ❌ DATABASE SETUP FAILED!
    echo.
    echo Please check:
    echo - PostgreSQL is running
    echo - Username and password are correct
    echo - You have permission to create databases
    echo.
    echo Error details above ↑
)

echo.
pause