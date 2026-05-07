# ============================================================
# MobiTranz Admin - Script de construction simplifiée
# Fichier : build_simple.py
# Usage: python build_simple.py
# ============================================================

import os
import sys
import subprocess
import shutil

def check_python():
    """Vérifie la version de Python."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"[ERREUR] Python 3.8+ requis. Version actuelle: {version.major}.{version.minor}")
        return False
    return True

def install_dependencies():
    """Installe les dépendances nécessaires."""
    print("\n[1/4] Installation des dépendances...")
    deps = [
        "customtkinter>=5.2.0",
        "darkdetect>=0.8.0", 
        "matplotlib>=3.7.0",
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "pandas>=2.0.0",
        "reportlab>=4.0.0",
        "pyinstaller>=6.0.0",
    ]
    
    for dep in deps:
        print(f"  Installation de {dep}...")
        subprocess.run([sys.executable, "-m", "pip", "install", dep], check=False)
    
    return True

def build_exe():
    """Construit l'executable avec PyInstaller."""
    print("\n[2/4] Construction de l'executable...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "MobiTranzAdmin",
        "--add-data", "desktop_admin;desktop_admin",
        "--hidden-import", "customtkinter",
        "--hidden-import", "darkdetect",
        "--hidden-import", "matplotlib",
        "--hidden-import", "PIL",
        "--hidden-import", "numpy",
        "--hidden-import", "scipy",
        "--hidden-import", "pandas",
        "--hidden-import", "reportlab",
        "--collect-all", "customtkinter",
        "--collect-all", "matplotlib",
        "--clean",
        "desktop_admin/main.py"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("  [OK] Construction réussie!")
        return True
    else:
        print(f"  [ERREUR] {result.stderr}")
        return False

def create_installer():
    """Crée un script d'installation."""
    print("\n[3/4] Création du script d'installation...")
    
    installer_script = '''@echo off
REM ========================================
REM MobiTranz Admin - Installateur
REM ========================================

echo.
echo Installation de MobiTranz Admin...
echo.

REM Créer dossier
if not exist "%APPDATA%\\MobiTranz" mkdir "%APPDATA%\\MobiTranz"

REM Copier fichiers
xcopy /e /y "MobiTranzAdmin.exe" "%APPDATA%\\MobiTranz\\"

REM Créer raccourci
echo Set WshShell = CreateObject("WScript.Shell") > temp.vbs
echo Set shortcut = WshShell.CreateShortcut("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\MobiTranz Admin.lnk") >> temp.vbs
echo shortcut.TargetPath = "%APPDATA%\\MobiTranz\\MobiTranzAdmin.exe" >> temp.vbs
echo shortcut.WorkingDirectory = "%APPDATA%\\MobiTranz" >> temp.vbs
echo shortcut.Save >> temp.vbs
cscript //nologo temp.vbs
del temp.vbs

echo.
echo Installation terminée!
echo.
pause
'''
    
    with open("dist/install.bat", "w") as f:
        f.write(installer_script)
    
    return True

def main():
    """Point d'entrée principal."""
    print("=" * 50)
    print("MobiTranz Admin - Build Script")
    print("=" * 50)
    
    if not check_python():
        return 1
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Nettoyage
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    install_dependencies()
    
    if not build_exe():
        print("\n[ERREUR] La construction a échoué.")
        print("Essayez d'exécuter cette commande manuellement:")
        print("  pyinstaller --onefile --windowed --name MobiTranzAdmin desktop_admin/main.py")
        return 1
    
    create_installer()
    
    print("\n" + "=" * 50)
    print("TERMINE!")
    print("Executable: dist/MobiTranzAdmin.exe")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())