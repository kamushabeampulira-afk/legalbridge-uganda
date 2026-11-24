@echo off
echo ============================================================
echo  LegalBridge Informal — Backend Setup (Windows)
echo ============================================================

cd /d "%~dp0..\backend"

echo.
echo [1/6] Creating virtual environment...
python -m venv venv
if errorlevel 1 (echo ERROR: Python not found. Install Python 3.11+ && pause && exit /b 1)

echo.
echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/6] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (echo ERROR: pip install failed && pause && exit /b 1)

echo.
echo [4/6] Copying .env file...
if not exist .env (
    copy ..\\.env.example .env
    echo .env created from .env.example — please edit it with your credentials.
) else (
    echo .env already exists — skipping.
)

echo.
echo [5/6] Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Migration failed.
    echo Make sure PostgreSQL is running and .env DB settings are correct.
    pause && exit /b 1
)

echo.
echo [6/6] Seeding sample legal data...
python manage.py seed_legal_data
if errorlevel 1 (echo WARNING: Seed data failed — you can run it manually later)

echo.
echo ============================================================
echo  Setup complete!
echo.
echo  Next steps:
echo  1. Edit backend\.env with your API keys
echo  2. Run: python manage.py createsuperuser
echo  3. Run: python manage.py runserver
echo  4. Open: http://127.0.0.1:8000/admin/
echo ============================================================
pause
