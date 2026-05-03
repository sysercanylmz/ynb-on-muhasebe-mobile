# YNB Ön Muhasebe Mobil

Bu proje, masaüstü ön muhasebe programının APK'ya uygun Kivy mobil sürümüdür.

## İçindeki Özellikler

- Ana sayfa özetleri
- Gelir / gider / tahsilat / ödeme kaydı
- Faturalı, fişli, dekontlu, e-arşiv/e-fatura veya belgesiz kayıt
- Kasa / banka oluşturma
- Kasa / banka açılış bakiyesi
- Kasa / banka güncel bakiyesi
- Cariler
- Kategoriler
- Raporlar
- İşlem düzenleme / silme / detay görme
- Belge dosyası ekleme altyapısı
- Telefonu +90 formatına çevirme
- Takvimle tarih seçme

## Bilgisayarda Test

```bash
pip install -r requirements.txt
python main.py
```

Windows'ta `run_desktop.bat` dosyasını da çalıştırabilirsin.

## APK Oluşturma

Buildozer Android paketleme işlemi Windows üzerinde doğrudan sağlıklı çalışmaz. En temiz yöntem Ubuntu veya Windows üzerinde WSL Ubuntu kullanmaktır.

Ubuntu / WSL Ubuntu içinde:

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git zip unzip openjdk-17-jdk
python3 -m pip install --user --upgrade buildozer cython
cd on_muhasebe_mobile
buildozer android debug
```

APK çıktı dosyası genelde burada oluşur:

```text
bin/ynbonmuhasebe-1.0-arm64-v8a-debug.apk
```

Alternatif olarak:

```bash
./build_apk.sh
```

## Veritabanı Nerede Tutulur?

Android'de uygulama verisi, uygulamanın kendi güvenli veri klasörüne yazılır. Bu yüzden APK güncellenirken normal şartlarda veriler korunur; uygulama kaldırılırsa Android uygulama verisini de silebilir.

## Önemli Not

Bu uygulama fatura kesmez. GİB/e-Arşiv/e-Fatura yerine geçmez. Sadece kişisel ön muhasebe, gelir-gider, kasa-banka, cari ve belge takip yazılımıdır.

---

## GitHub Actions ile APK alma

Bu pakette `.github/workflows/build-apk.yml` dosyası hazır gelir. Bilgisayarında Ubuntu/WSL kurmadan APK üretmek için GitHub Actions kullanabilirsin.

Kısa kullanım:

1. ZIP'i aç.
2. `on_muhasebe_mobile` klasörünün içindeki dosyaları GitHub reposunun köküne yükle.
3. GitHub > Actions > Build Android APK > Run workflow.
4. Çalışma bitince Artifacts bölümünden `YNB-On-Muhasebe-APK` dosyasını indir.

Detaylı adımlar için `README_GITHUB_ACTIONS.md` dosyasına bak.
