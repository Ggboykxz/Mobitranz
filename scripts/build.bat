@echo off
REM ============================================================
REM MobiTranz Admin - Script de construction Windows
REM Fichier : build.bat
REM ============================================================

echo ========================================
echo MobiTranz Admin - Build pour Windows
echo ========================================

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python non trouvé. Veuillez installer Python 3.10+
    pause
    exit /b 1
)

echo.
echo [1/4] Installation des dépendances...
pip install -r requirements-windows.txt
if errorlevel 1 (
    echo [ERREUR] Échec installation dépendances
    pause
    exit /b 1
)

echo.
echo [2/4] Nettoyage...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [3/4] Construction executable avec PyInstaller...
pyinstaller --onefile --windowed --name "MobiTranzAdmin" ^
  --add-data "desktop_admin;desktop_admin" ^
  --hidden-import=customtkinter ^
  --hidden-import=darkdetect ^
  --hidden-import=matplotlib ^
  --hidden-import=PIL ^
  --hidden-import=numpy ^
  --hidden-import=scipy ^
  --hidden-import=pandas ^
  --hidden-import=reportlab ^
  --collect-all=customtkinter ^
  --clean ^
  desktop_admin/main.py

if errorlevel 1 (
    echo [ERREUR] Échec construction executable
    pause
    exit /b 1
)

echo.
echo [4/4] Nettoyage...
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__
for /d %%i in (desktop_admin\*) do if exist "%%i\__pycache__" rmdir /s /q "%%i\__pycache__"

echo.
echo ========================================
echo Construction terminée avec succès!
echo Executable: dist\MobiTranzAdmin.exe
echo ========================================
echo.
pause