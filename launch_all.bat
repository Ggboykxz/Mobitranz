@echo off
echo ========================================
echo    Lancement MobiTranz
echo ========================================

echo.
echo [1/2] Lancement du backend API...
start "Backend API" cmd /k "cd /d C:\Users\hp\Desktop\Mobitranz && set PYTHONPATH=. && python -m uvicorn backend.main:app --port 8000"

timeout /t 5 /nobreak >nul

echo [2/2] Lancement Admin Desktop...
start "MobiTranz Admin" cmd /k "cd /d C:\Users\hp\Desktop\Mobitranz && set PYTHONPATH=. && python desktop_admin\main.py"

echo.
echo ========================================
echo   Connexion: admin@mobitranz.ga
echo   Mot de passe: AdminMobitranz2026!
echo ========================================
echo.
pause