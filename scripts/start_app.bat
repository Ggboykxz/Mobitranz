@echo off
echo ==========================================
echo    LANCEMENT MOBITRANZ
echo ==========================================
echo.

echo [1/2] Lancement du backend API...
start "Backend API" cmd /k "cd /d C:\Users\hp\Desktop\Mobitranz && set PYTHONPATH=. && python -m uvicorn backend.main:app --port 8000"

timeout /t 5 /nobreak >nul

echo [2/2] Lancement du Desktop Admin...
start "MobiTranz Admin" cmd /k "cd /d C:\Users\hp\Desktop\Mobitranz && set PYTHONPATH=. && python desktop_admin\main.py"

echo.
echo === LANCEMENT TERMINE ===
echo Backend: http://localhost:8000
echo.
pause