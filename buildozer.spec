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

# Use only one of include_patterns/exclude_patterns correctly
source.include_patterns = UI/*.kv, screens/*.py, assets/*.png, assets/*.ttf, *.env, icon.png

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# Use the master branch of KivyMD instead of deprecated 1.2.0
requirements = python3==3.10.13,kivy,https://github.com/kivymd/KivyMD/archive/master.zip,setuptools,six,idna,urllib3,requests,pymysql,bcrypt,cryptography,python-dotenv,twilio,sdl2,pyjnius,cython==0.29.33

# (str) Icon of the application
icon.filename = icon.png

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, SEND_SMS, ACCESS_FINE_LOCATION

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android NDK directory (optional if downloaded automatically)
android.ndk_path = /home/sarastanoevska/.buildozer/android/platform/android-ndk-r25b

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (list) List of directory to exclude
source.exclude_dirs = venv, __pycache__


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
