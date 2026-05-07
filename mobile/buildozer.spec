[app]

title = MobiTranz
package.name = mobitranz
package.domain = ga.mobitranz

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

requirements = python3,kivy,android,pillow,pyjnius,sdl2

orientation = portrait
android.archs = arm64-v8a,armeabi-v7a

fullscreen = 0

android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,CAMERA,RECORD_AUDIO,VIBRATE

[buildozer]

log_level = 2

warn_on_root = 1