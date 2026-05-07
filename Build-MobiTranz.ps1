# ============================================================
# MobiTranz Admin - Script Build PowerShell
# Fichier : Build-MobiTranz.ps1
# Usage: .\Build-MobiTranz.ps1
# ============================================================

param(
    [switch]$Clean,
    [switch]$Portable
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MobiTranz Admin - Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Vérifier Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[ERREUR] Python non trouvé. Veuillez installer Python 3.10+" -ForegroundColor Red
    Write-Host "Téléchargement: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = python --version
Write-Host "Python détecté: $pythonVersion" -ForegroundColor Green

# Changer vers le dossier du script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Nettoyage
if ($Clean) {
    Write-Host "`n[NETTOYAGE]" -ForegroundColor Yellow
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    Write-Host "  Nettoyage terminé" -ForegroundColor Green
}

# Installation des dépendances
Write-Host "`n[DEPENDANCES]" -ForegroundColor Yellow

$deps = @(
    "customtkinter>=5.2.0",
    "darkdetect>=0.8.0",
    "matplotlib>=3.7.0",
    "Pillow>=10.0.0",
    "numpy>=1.24.0",
    "scipy>=1.10.0",
    "pandas>=2.0.0",
    "reportlab>=4.0.0",
    "pyinstaller>=6.0.0"
)

foreach ($dep in $deps) {
    Write-Host "  Installation de $dep..." -ForegroundColor Gray
    python -m pip install $dep --quiet 2>$null
}

# Build avec PyInstaller
Write-Host "`n[BUILD]" -ForegroundColor Yellow

$pyinstallerArgs = @(
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
    "--clean",
    "--log-level", "WARN",
    "desktop_admin/main.py"
)

python -m PyInstaller @pyinstallerArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERREUR] Build échoué" -ForegroundColor Red
    exit 1
}

# Vérifier l'executable
$exePath = "dist\MobiTranzAdmin.exe"
if (Test-Path $exePath) {
    $size = (Get-Item $exePath).Length / 1MB
    Write-Host "`n[OK] Executable créé: $exePath" -ForegroundColor Green
    Write-Host "  Taille: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan
    
    if ($Portable) {
        Write-Host "`n[PORTABLE] Création package..." -ForegroundColor Yellow
        $zipName = "MobiTranzAdmin-Portable-1.0.0.zip"
        Compress-Archive -Path "dist\*" -DestinationPath $zipName -Force
        Write-Host "  Package: $zipName" -ForegroundColor Green
    }
} else {
    Write-Host "[ERREUR] Executable non trouvé" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TERMINE! L'application est prête." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan