[app]
title = Save Pro
icon.filename = %(source.dir)s/icon.png
package.name = savepro
package.domain = com.youssefmansouri
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0

requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.1,yt_dlp,sqlite3,urllib3,requests,ffpyplayer
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
