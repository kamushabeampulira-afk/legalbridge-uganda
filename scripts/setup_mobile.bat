@echo off
echo ============================================================
echo  LegalBridge Informal — Mobile App Setup (Windows)
echo ============================================================

cd /d "%~dp0..\mobile"

echo.
echo [1/2] Installing Node.js dependencies...
npm install
if errorlevel 1 (echo ERROR: npm install failed. Is Node.js 18+ installed? && pause && exit /b 1)

echo.
echo [2/2] Setup complete!
echo.
echo  Next steps:
echo  1. Update mobile\services\api.ts with your backend IP address
echo  2. Run: npx expo start
echo  3. Press 'a' for Android emulator, scan QR for Expo Go
echo.
echo  IMPORTANT: Change the BASE_URL in mobile\services\api.ts
echo  from 127.0.0.1 to your machine's LAN IP for device testing.
echo ============================================================
pause
