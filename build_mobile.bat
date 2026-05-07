# ============================================================
# Script Build Mobile Android
# Fichier : build_mobile.bat
# Usage: Sur Windows avec Android SDK installé
# ============================================================

@echo off
setlocal

echo ========================================
echo MobiTranz Mobile - Build Android APK
echo ========================================

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python non trouvé
    pause
    exit /b 1
)

echo.
echo [1/4] Installation des dépendances...
pip install kivy buildozer pillow pyjnius android

echo.
echo [2/4] Initialisation buildozer...
cd mobile
buildozer init

echo.
echo [3/4] Téléchargement Android SDK (si nécessaire)...
buildozer android debug

echo.
echo [4/4] Vérification APK...
if exist "bin\MobiTranz-1.0.0.apk" (
    echo [OK] APK créé: bin\MobiTranz-1.0.0.apk
) else (
    echo [ERREUR] APK non trouvé
)

echo.
echo ========================================
echo Terminé!
echo ========================================
pause