# MobiTranz Mobile - Build APK

## Pre-requis

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv python3-dev \
  autoconf automake libtool libltdl-dev \
  git zip unzip openjdk-17-jdk \
  libssl-dev libffi-dev

# Installer Android SDK
mkdir -p ~/android
cd ~/android
wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip commandlinetools-linux-*.zip
mkdir cmdline-tools/latest
mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true
yes | ~/android/cmdline-tools/latest/bin/sdkmanager --sdk_root=$HOME/android "platforms;android-34" "build-tools;34.0.0" "ndk;27.0.12077973"
```

### Windows
1. Installer Python 3.12+ depuis python.org (cocher "Add to PATH")
2. Installer Android Studio + SDK (API 34, NDK 27)
3. Configurer les variables d'environnement :
   ```
   ANDROID_SDK_ROOT=C:\Users\<user>\AppData\Local\Android\Sdk
   ANDROID_NDK_ROOT=%ANDROID_SDK_ROOT%\ndk\27.0.12077973
   ```

### macOS
```bash
brew install python autoconf automake libtool
# Installer Android Studio puis SDK API 34 + NDK 27
```

---

## Build APK

### 1. Cloner le projet
```bash
git clone https://github.com/Ggboykxz/Mobitranz.git
cd Mobitranz/mobile
```

### 2. Installer buildozer
```bash
pip install --user buildozer cython
```

### 3. Configurer les chemins SDK
Editer `buildozer.spec` si necessaire :
```ini
android.sdk_path = /home/votreuser/android
android.ndk_path = /home/votreuser/android/ndk/27.0.12077973
```

### 4. Build APK Debug
```bash
buildozer android debug
```

**L'APK sera dans :** `mobile/bin/mobitranz-1.1.0-<version>-debug.apk`

### 5. Build APK Release (signe)
```bash
buildozer android release
```

Signer l'APK :
```bash
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 \
  -keystore ~/mobitranz.keystore \
  mobile/bin/mobitranz-1.1.0-release-unsigned.apk mobitranz

zipalign -v 4 \
  mobile/bin/mobitranz-1.1.0-release-unsigned.apk \
  mobile/bin/mobitranz-1.1.0-release.apk
```

---

## Variables d'environnement (optionnel)

```bash
# API distante (defaut: https://api.mobitranz.ga)
export API_BASE_URL=https://votre-serveur.com
```

---

## Structure du projet mobile

```
mobile/
  main.py              # Point d'entree KivyMD
  buildozer.spec       # Configuration build Android
  config.py            # Configuration API
  screens/
    base_screen.py     # Classe de base avec header/loading/toast
    auth/              # Login, Register
    client/            # 13 ecrans client
    driver/            # 4 ecrans chauffeur
  services/
    api_client.py      # Client API async
    auth_service.py    # Gestion tokens JWT
    cache_service.py   # Cache hors-ligne JsonStore
    kivy_api_client.py # Wrapper Kivy pour appels API
  theme/
    colors.py          # Palette de couleurs
    theme.py           # Theme KivyMD + dark mode
  ui/
    shimmer.py         # Shimmer skeleton loading
    shimmer_list.py    # Templates shimmer (carte, profil, etc.)
    haptic.py          # Retour vibratoire
    ripple.py          # Bouton avec effet d'onde
  tests/
    test_ui.py         # 50 tests unitaires
```

---

## Dependances

| Librairie | Version | Usage |
|-----------|---------|-------|
| kivy | >=2.3.0 | Framework cross-platform |
| kivymd | >=1.2.0 | Material Design widgets |
| httpx | >=0.28.0 | Client API async |
| plyer | >=2.1.0 | Vibrator, GPS, notifications |
| kivy-garden.mapview | >=1.0.0 | Carte OpenStreetMap |
| pillow | >=10.0 | Traitement images |

---

## Tests

```bash
# Sans ecran (headless)
KIVY_UNITTEST=1 python -m pytest mobile/tests/ -v

# Avec couverture
KIVY_UNITTEST=1 python -m pytest mobile/tests/ --cov=mobile --cov-report=term
```

---

## Notes

- Le premier build peut prendre 20-40 minutes (compilation SDL2/Kivy)
- Les builds suivants sont plus rapides (cache Cython)
- Pour le debug USB : `adb logcat | grep python`
- L'API doit etre accessible depuis le telephone (pas de localhost)
