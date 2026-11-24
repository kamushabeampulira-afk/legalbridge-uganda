@echo off
echo ============================================================
echo  LegalBridge Informal — Run Backend Tests
echo ============================================================

cd /d "%~dp0..\backend"

if not exist venv\Scripts\activate.bat (
    echo ERROR: Virtual environment not found. Run setup_backend.bat first.
    pause && exit /b 1
)

call venv\Scripts\activate.bat

echo.
echo Running all tests...
pytest tests/ -v --tb=short

echo.
echo ============================================================
echo  Tests complete.
echo ============================================================
pause
