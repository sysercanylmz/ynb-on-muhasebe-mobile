[app]

# Uygulama bilgileri
title = YNB Ön Muhasebe
package.name = ynbonmuhasebe
package.domain = com.yeninesilbilisim

# Kaynak klasör
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,db,ico
source.exclude_dirs = tests,bin,build,__pycache__,.git

# Ana uygulama ayarları
version = 1.0
requirements = python3,sqlite3,filetype,kivy==2.3.1
orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/assets/app_icon.png

# Android izinleri
# Veritabanı uygulama içi klasöre yazılır. Belge ekinde harici dosya seçimi için okuma izni bırakıldı.
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Android hedefleri
android.minapi = 23
android.api = 35
android.archs = arm64-v8a, armeabi-v7a

# Paket tipi: debug APK
# Release için: buildozer android release

[buildozer]
log_level = 2
warn_on_root = 1
