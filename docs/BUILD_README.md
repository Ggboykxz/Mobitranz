# MobiTranz Admin - Guide d'Installation Windows

## Prérequis

1. **Windows 10/11** (64-bit)
2. **Python 3.10+** installé
3. **Connexion internet** pour les dépendances

## Option 1: Exécution directe (Sans installation)

### Étape 1: Installer Python
- Télécharger Python 3.12 depuis https://www.python.org/downloads/
- Cocher "Add Python to PATH" pendant l'installation

### Étape 2: Préparer le projet
```batch
cd dossier_contenant_le_projet
pip install -r requirements-windows.txt
```

### Étape 3: Lancer l'application
```batch
python desktop_admin\main.py
```

---

## Option 2: Créer un .exe (PyInstaller)

### Étape 1: Installer les dépendances
```batch
pip install -r requirements-windows.txt
pip install pyinstaller
```

### Étape 2: Compiler l'executable
```batch
pyinstaller --onefile --windowed --name "MobiTranzAdmin" desktop_admin\main.py
```

### Étape 3: Récupérer l'executable
L'executable se trouve dans `dist\MobiTranzAdmin.exe`

---

## Option 3: Script automatique (build.bat)

Exécuter simplement:
```batch
build.bat
```

---

## Option 4: Inno Setup (Installateur professionnel)

1. Installer Inno Setup: https://jrsoftware.org/isinfo.php
2. Compiler: `iscc MobiTranzAdmin.iss`
3. L'installateur sera dans `dist\MobiTranzAdmin-Setup-1.0.0.exe`

---

## Structure des fichiers

```
MobiTranz/
├── desktop_admin/
│   ├── main.py              # Point d'entrée
│   ├── config.py           # Configuration
│   ├── theme/               # Thème Fluent Design
│   └── windows/             # Fenêtres et modules
├── build.bat               # Script build Windows
├── build_simple.py         # Script build alternatif
├── setup.py                # Setup cx_Freeze
├── requirements-windows.txt # Dépendances
├── MobiTranzAdmin.iss      # Script Inno Setup
└── IMPROVEMENTS.md         # Améliorations futures
```

## Résolution de problèmes

### Erreur: "Module not found"
```batch
pip install <module_manquant>
```

### Erreur: "Permission denied"
- Exécuter PowerShell en tant qu'administrateur

### L'application ne démarre pas
- Vérifier que tous les fichiers desktop_admin sont présents
- Vérifier Python 64-bit installé

---

## Support

- Email: support@mobitranz.ga
- Site: https://mobitranz.ga
- Gabon: +241 74 XX XX XX