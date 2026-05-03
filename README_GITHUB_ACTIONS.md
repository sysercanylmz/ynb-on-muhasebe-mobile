# GitHub Actions ile APK Oluşturma

Bu proje Android APK üretmek için hazır GitHub Actions ayarı içerir.

## Önemli

GitHub'a ZIP dosyasını tek parça olarak yüklemek işe yaramaz. ZIP'i açıp `on_muhasebe_mobile` klasörünün içindeki dosyaları GitHub reposunun köküne yüklemelisin.

Repo kökünde şunlar görünmeli:

```text
main.py
buildozer.spec
requirements.txt
app/
assets/
.github/workflows/build-apk.yml
```

## Adımlar

1. GitHub'da yeni repository oluştur.
2. Bu ZIP'i bilgisayarda çıkar.
3. `on_muhasebe_mobile` klasörünün içindeki bütün dosya ve klasörleri repository içine yükle.
4. GitHub'da `Actions` sekmesine gir.
5. Soldan `Build Android APK` workflow'unu seç.
6. `Run workflow` düğmesine bas.
7. İşlem bitince aynı çalışma ekranının altındaki `Artifacts` bölümünden `YNB-On-Muhasebe-APK` dosyasını indir.
8. İndirdiğin artifact ZIP'inin içinde `.apk` dosyası olacak.

## Hata olursa

Eğer build kırılırsa GitHub Actions ekranında logları aç. Ayrıca workflow hata durumunda `buildozer-error-logs` adlı ek bir artifact üretmeye çalışır. Onu indirip hata metniyle birlikte kontrol edebilirsin.

## APK türü

Bu workflow debug APK üretir. Test için telefona yüklenebilir. Play Store'a koymak için ayrıca imzalı release APK/AAB süreci gerekir.
