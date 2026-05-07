# ============================================================
# MobiTranz Mobile - Guide de Build APK
# ============================================================

## Problème actuel

Le serveur n'a pas les outils de compilation Linux (autoconf, libtool) pour build Kivy/SDL2.

## Solution locale - Sur ton PC Windows/Mac/Linux

### 1. Prérequis
```bash
# Windows: Installer Python 3.10+ et Android Studio
# Linux/Mac: Installer les dépendances
sudo apt install python3-pip autoconf automake libtool libltdl-dev
```

### 2. Installer les dépendances
```bash
pip install kivy buildozer pillow cython
```

### 3. Build APK
```batch
cd mobile
buildozer android debug
```

L'APK sera dans: `mobile/bin/MobiTranz-1.0.0.apk`

## Alternative - APK Debug sans buildozer

Tu peux utiliser l'APK Kivy de démo puis remplacer le code:
1. Télécharger un APK Kivy sample
2. Remplacer les fichiers .py dans l'APK
3. Resigner l'APK

## Résumé

Le code mobile est prêt (18 screens, compile sans erreur).
L'APK doit être généré sur une machine locale avec:
- Python 3.10+
- Android SDK
- buildozer + dépendances