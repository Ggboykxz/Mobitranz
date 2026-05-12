[app]

title = MobiTranz
package.name = mobitranz
package.domain = ga.mobitranz

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 1.1.0
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

requirements = python3,kivy>=2.3.0,kivymd>=1.2.0,httpx,plyer,kivy-garden.mapview,requests

orientation = portrait
osx.package_name = MobiTranz
osx.bundle_identifier = ga.mobitranz.mobi
osx.icon = icon.png

android.archs = arm64-v8a,armeabi-v7a
android.api = 34
android.minapi = 26
android.sdk_path = /opt/android-sdk
android.ndk_path = /opt/android-ndk
android.ndk = 27
android.sdk = 34
android.gradle_dependencies = 'com.google.firebase:firebase-messaging:24.1.0'
android.add_src = java/

fullscreen = 0

android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,CAMERA,RECORD_AUDIO,VIBRATE,POST_NOTIFICATIONS

android.manifest.intent_filters = [
    {
        "android:name": "ga.mobitranz.mobi.MainActivity",
        "intent-filters": [
            {
                "action": "android.intent.action.MAIN",
                "category": "android.intent.category.LAUNCHER"
            }
        ]
    }
]

presplash.filename = presplash.png
icon.filename = icon.png

[buildozer]

log_level = 2
warn_on_root = 1
