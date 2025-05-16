[app]

# (str) Title of your application
title = ResQ App

# (str) Package name
package.name = resqapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.sara

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,env

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# Use the master branch of KivyMD instead of deprecated 1.2.0
requirements = python3,kivy,https://github.com/kivymd/KivyMD/archive/master.zip,requests,pymysql,bcrypt,cryptography,python-dotenv,twilio,sdl2,pyjnius

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
icon.filename = icon.png

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, SEND_SMS, ACCESS_FINE_LOCATION

# (int) Target Android API, should be as high as possible.
#android.api = 31

# (int) Minimum API your APK / AAB will support.
#android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 20

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
android.ndk_path = /home/sarastanoevska/.buildozer/android/platform/android-ndk-r25b

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = venv

# (str) The format used to package the app for debug mode
# android.debug_artifact = apk

# (str) The format used to package the app for release mode
# android.release_artifact = aab

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
