@echo off
echo ================================================
echo Starting License Plate Detection System
echo ================================================
echo.

REM Start Backend
echo Starting Backend (Flask)...
start "Backend Server" cmd /k "cd backend && python app.py"
timeout /t 3 /nobreak >nul

REM Start Frontend
echo Starting Frontend (React)...
start "Frontend Server" cmd /k "cd frontend && npm start"

echo.
echo ================================================
echo System Started!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo ================================================
echo.
echo Press any key to stop all servers...
pause >nul

REM Stop servers
taskkill /FI "WINDOWTITLE eq Backend Server" /T /F
taskkill /FI "WINDOWTITLE eq Frontend Server" /T /F