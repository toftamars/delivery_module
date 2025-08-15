# 🚀 CloudPepper İçin Teslimat Modülü Kurulum Rehberi

## ⚠️ ÖNEMLİ NOTLAR

CloudPepper kullanırken modül yüklemede yaşanan sorunların çözümleri:

## 🔧 ADIM 1: Modül Klasörünü Yeniden Adlandır

CloudPepper'da modül klasör adı ile kod içi adlandırma aynı olmalıdır.

```bash
# Mevcut klasörün adını değiştir
cd /Users/tofta/Desktop/
mv teslimat_planlama delivery_module
```

## 🔧 ADIM 2: Zip Dosyası Oluştur

CloudPepper için özel zip formatı:

```bash
cd delivery_module
zip -r delivery_module.zip . -x "*.git*" "*.DS_Store*" "__pycache__/*"
```

## 🔧 ADIM 3: CloudPepper'da Yükleme

### Yöntem 1: Manuel Yükleme
1. CloudPepper hesabınıza giriş yapın
2. **Uygulamalar** > **Özel Uygulamalar** bölümüne gidin
3. **"Uygulama Yükle"** butonuna tıklayın
4. `delivery_module.zip` dosyasını seçin
5. **"Yükle"** butonuna tıklayın

### Yöntem 2: GitHub Entegrasyonu
1. CloudPepper'da **"GitHub'dan Yükle"** seçeneğini kullanın
2. Repository URL: `https://github.com/toftamars/Teslimat-Planlama-.git`
3. Branch: `main`
4. Modül klasörü: `delivery_module` (yeniden adlandırdıktan sonra)

## 🔧 ADIM 4: Veritabanını Güncelle

CloudPepper'da modül görünmüyorsa:

1. **Ayarlar** > **Teknik** > **Veritabanı Yapısı** > **Uygulamalar Listesini Güncelle**
2. **"Güncelle"** butonuna tıklayın
3. **Uygulamalar** menüsüne geri dönün
4. Arama kutusuna **"Teslimat"** yazın

## 🔧 ADIM 5: Cache Temizleme

Modül hala görünmüyorsa:

1. CloudPepper **Dashboard**'a gidin
2. **"Veritabanını Yeniden Başlat"** seçeneğini kullanın
3. 2-3 dakika bekleyin
4. Tekrar **Uygulamalar** > **Uygulamalar Güncelle** yapın

## 🐛 SORUN GİDERME

### Problem: "Modül bulunamadı" hatası
**Çözüm**: 
- Modül klasör adının `delivery_module` olduğundan emin olun
- Zip dosyasında extra klasör olmadığından emin olun

### Problem: "Bağımlılık hatası"
**Çözüm**:
- Tüm bağımlı modüllerin yüklü olduğundan emin olun:
  - `base`, `mail`, `web`, `contacts`, `stock`, `sms`

### Problem: "İzin hatası"
**Çözüm**:
- CloudPepper'da admin yetkilerinizin olduğundan emin olun
- Özel uygulama yükleme izninizin olduğunu kontrol edin

## 📞 DESTEK

Sorun devam ediyorsa:
1. CloudPepper destek ekibiyle iletişime geçin
2. Log dosyalarını inceleyin: **Ayarlar** > **Teknik** > **Logging**

## ✅ BAŞARILI KURULUM KONTROL LİSTESİ

- [ ] Modül klasörü adı `delivery_module` olarak değiştirildi
- [ ] Zip dosyası oluşturuldu
- [ ] CloudPepper'a yüklendi
- [ ] Uygulamalar listesi güncellendi
- [ ] Modül "Teslimat Modülü" adıyla görünüyor
- [ ] Yükleme işlemi başarılı
