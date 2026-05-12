#!/bin/bash
# ============================================================
# Build APK Android - MobiTranz
# Usage: bash scripts/build_android.sh [debug|release]
# ============================================================

set -e
MODE="${1:-debug}"
cd "$(dirname "$0")/../mobile"

echo "=========================================="
echo "  Build APK MobiTranz ($MODE)"
echo "=========================================="

# Verifier les pre-requis
if ! command -v java &>/dev/null; then
    echo "Java JDK 17 requis. Installation..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt update && sudo apt install -y openjdk-17-jdk
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install openjdk@17
    fi
fi

if ! command -v buildozer &>/dev/null; then
    echo "Installation buildozer..."
    pip install --user buildozer cython
    export PATH="$HOME/.local/bin:$PATH"
fi

# Verifier Android SDK
ANDROID_HOME="${ANDROID_HOME:-$HOME/android}"
if [ ! -d "$ANDROID_HOME/platforms/android-34" ]; then
    echo "Installation Android SDK + NDK..."
    mkdir -p "$ANDROID_HOME"
    cd "$ANDROID_HOME"
    
    # Download command line tools
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
    unzip -q commandlinetools-linux-*.zip
    rm commandlinetools-linux-*.zip
    
    # Accept licenses and install SDK
    yes | "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" --sdk_root="$ANDROID_HOME" \
        "platforms;android-34" \
        "build-tools;34.0.0" \
        "ndk;27.0.12077973" \
        "platform-tools"
fi

# Mettre a jour buildozer.spec avec les bons chemins
sed -i "s|android.sdk_path = .*|android.sdk_path = $ANDROID_HOME|" buildozer.spec
sed -i "s|android.ndk_path = .*|android.ndk_path = $ANDROID_HOME/ndk/27.0.12077973|" buildozer.spec

cd "$(dirname "$0")/../mobile"

echo "=========================================="
echo "  Build en cours... ($MODE)"
echo "  Premier build: ~30-40 min"
echo "  Builds suivants: ~2-5 min"
echo "=========================================="

if [ "$MODE" == "release" ]; then
    buildozer android release
    APK="bin/mobitranz-*-release-unsigned.apk"
    echo "APK unsigned: $APK"
    echo "Signer avec:"
    echo "  jarsigner -keystore votre.keystore $APK mobitranz"
    echo "  zipalign -v 4 $APK mobitranz-signed.apk"
else
    buildozer android debug
    APK=$(ls bin/*.apk 2>/dev/null | head -1)
    echo "APK: $APK"
fi

echo "=========================================="
echo "  BUILD TERMINE!"
echo "=========================================="
