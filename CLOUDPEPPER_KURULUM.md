# 🚀 CloudPepper Teslimat Modülü Kurulum Rehberi

## ⚠️ ÖNEMLİ: Modül Görünmüyor Sorunu Çözümü

### 🔧 ADIM 1: Yeni Zip Dosyasını İndirin
- `delivery_module_cloudpepper.zip` dosyasını indirin
- Bu dosya Cloudpepper için özel olarak hazırlanmıştır

### 🔧 ADIM 2: CloudPepper'da Yükleme
1. **CloudPepper hesabınıza giriş yapın**
2. **Uygulamalar** > **Özel Uygulamalar** bölümüne gidin
3. **"Uygulama Yükle"** butonuna tıklayın
4. `delivery_module_cloudpepper.zip` dosyasını seçin
5. **"Yükle"** butonuna tıklayın

### 🔧 ADIM 3: Uygulamalar Listesini Güncelle
**BU ADIM ÇOK ÖNEMLİ!**
1. **Ayarlar** > **Teknik** > **Veritabanı Yapısı** > **Uygulamalar Listesini Güncelle**
2. **"Güncelle"** butonuna tıklayın
3. **Uygulamalar** menüsüne geri dönün

### 🔧 ADIM 4: Modülü Arayın
1. **Uygulamalar** menüsünde arama kutusuna **"Teslimat"** yazın
2. **"Delivery Module"** adıyla modül görünecektir
3. **"Yükle"** butonuna tıklayın

### 🔧 ADIM 5: Cache Temizleme (Gerekirse)
Modül hala görünmüyorsa:
1. CloudPepper **Dashboard**'a gidin
2. **"Veritabanını Yeniden Başlat"** seçeneğini kullanın
3. 2-3 dakika bekleyin
4. Tekrar **Uygulamalar** > **Uygulamalar Güncelle** yapın

## 🐛 SORUN GİDERME

### Problem: "Modül bulunamadı" hatası
**Çözüm**: 
- Uygulamalar listesini güncellemeyi unutmayın
- Zip dosyasında extra klasör olmadığından emin olun

### Problem: "Bağımlılık hatası"
**Çözüm**:
- Tüm bağımlı modüllerin yüklü olduğundan emin olun:
  - `base`, `mail`, `web`, `contacts`, `stock`, `sms`

### Problem: "İzin hatası"
**Çözüm**:
- CloudPepper'da admin yetkilerinizin olduğundan emin olun
- Özel uygulama yükleme izninizin olduğunu kontrol edin

## 📋 KURULUM KONTROL LİSTESİ

- [ ] `delivery_module_cloudpepper.zip` dosyası indirildi
- [ ] CloudPepper'a yüklendi
- [ ] **Uygulamalar Listesini Güncelle** yapıldı
- [ ] "Teslimat" araması yapıldı
- [ ] "Delivery Module" görüldü
- [ ] Modül başarıyla yüklendi

## 🎯 BAŞARILI KURULUM SONRASI

Modül yüklendikten sonra:
1. **Teslimat** menüsü ana menüde görünecek
2. **Teslimat Belgeleri**, **Teslimat Araçları**, **Teslimat Günleri** alt menüleri aktif olacak
3. **Konfigürasyon** menüsü altında **Şehirler** ve **İlçeler** görünecek

## 📞 DESTEK

Sorun devam ediyorsa:
1. CloudPepper destek ekibiyle iletişime geçin
2. Log dosyalarını inceleyin: **Ayarlar** > **Teknik** > **Logging**
3. Hata mesajlarını not edin

## ✅ NOT

Bu modül Cloudpepper için özel olarak optimize edilmiştir. Manifest dosyasındaki gereksiz tekrarlar kaldırılmış ve tüm bağımlılıklar doğru şekilde tanımlanmıştır.
