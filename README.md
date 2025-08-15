# Teslimat Modülü v1.0.3

## 📋 Genel Bakış

Teslimat yönetimi için geliştirilmiş Odoo modülü. Transfer belgelerinden otomatik teslimat oluşturma, SMS bildirimleri, araç yönetimi ve ilçe bazlı teslimat programı özelliklerini içerir.

## 🚀 Özellikler

### ✅ Ana Özellikler
- **Transfer Belgesi Entegrasyonu**: Stock picking'lerden otomatik teslimat oluşturma
- **SMS Bildirimleri**: Durum değişikliklerinde müşteriye SMS gönderimi
- **Araç Yönetimi**: Günlük kapasite kontrolü ve araç takibi
- **Teslimat Günleri**: İlçe bazlı haftalık teslimat programı
- **Geçici Kapatma**: Araç ve gün bazında geçici kapatma özelliği
- **Yetki Yönetimi**: Teslimat yöneticisi ve normal kullanıcı yetkileri

### 📅 Teslimat Günleri
- **Pazartesi**: Anadolu + Avrupa yakası ilçeleri
- **Salı**: Anadolu + Avrupa yakası ilçeleri
- **Çarşamba**: Anadolu + Avrupa yakası ilçeleri
- **Perşembe**: Anadolu + Avrupa yakası ilçeleri
- **Cuma**: Anadolu + Avrupa yakası ilçeleri
- **Cumartesi**: Anadolu + Avrupa yakası ilçeleri
- **Pazar**: ❌ Teslimat yapılmıyor

### 🚗 Araç Tipleri
- **Anadolu Yakası**: Anadolu yakası ilçeleri için
- **Avrupa Yakası**: Avrupa yakası ilçeleri için
- **Küçük Araç 1/2**: Ek araçlar
- **Ek Araç**: Geçici araçlar

## 📦 Kurulum

### 1. Modülü Yükle
```bash
python3 -m odoo -d your_database -i teslimat_planlama --stop-after-init
```

### 2. Odoo'yu Yeniden Başlat
```bash
sudo systemctl restart odoo
```

### 3. Teslimat Programını Ayarla
- Odoo'ya giriş yapın
- **Teslimat** → **Teslimat Programı Kurulumu**
- "Teslimat Programını Ayarla" butonuna tıklayın

## 🔧 Kullanım

### Teslimat Belgesi Oluşturma
1. **Teslimat** → **Teslimat Belgesi Oluştur**
2. Transfer numarasını girin
3. İlçe seçin
4. Araç seçin
5. "Teslimat Oluştur" butonuna tıklayın

### Teslimat Durumu Yönetimi
- **Yolda**: Teslimatı yola çıkarır ve SMS gönderir
- **Tamamla**: Teslimatı tamamlar ve SMS gönderir
- **İptal**: Teslimatı iptal eder ve SMS gönderir

### Araç Yönetimi
- **Kapasite Kontrolü**: Günlük teslimat limiti
- **Geçici Kapatma**: Araçları geçici olarak kapatma
- **Durum Takibi**: Bugünkü teslimat sayısı

## 🛠️ Teknik Detaylar

### Model Yapısı
- `delivery.document`: Ana teslimat belgesi
- `delivery.vehicle`: Araç yönetimi
- `delivery.day`: Teslimat günleri
- `res.city`: İl yönetimi
- `res.city.district`: İlçe yönetimi
- `res.partner`: Müşteri bilgileri (genişletilmiş)

### Güvenlik
- `group_delivery_manager`: Teslimat yöneticisi grubu
- Model erişim hakları
- Kayıt seviyesi kuralları

### SMS Entegrasyonu
- Durum değişikliklerinde otomatik SMS
- Hata durumunda işlem devam eder
- Müşteri telefon numarası kontrolü

## 🐛 Sorun Giderme

### Veritabanı Şeması Sorunları
```bash
# Modülü yeniden yükle
python3 -m odoo -d your_database -u teslimat_planlama --stop-after-init
python3 -m odoo -d your_database -i teslimat_planlama --stop-after-init
```

### SMS Sorunları
- SMS modülünün yüklü olduğundan emin olun
- Müşteri telefon numarasının doğru olduğunu kontrol edin

### Kapasite Sorunları
- Araç günlük limitini kontrol edin
- Teslimat yöneticisi yetkilerini kontrol edin

## 📝 Sürüm Geçmişi

### v1.0.3 (Temiz Versiyon)
- ✅ Hata yönetimi iyileştirildi
- ✅ SMS fonksiyonu güvenli hale getirildi
- ✅ Gereksiz dosyalar temizlendi
- ✅ Log sistemi eklendi
- ✅ Manifest sürümü güncellendi
- ✅ Modül adı teslimat_planlama olarak değiştirildi

### v1.0.2
- ✅ CloudPepper durum raporu eklendi
- ✅ Modül stabil çalışır durumda

### v1.0.1
- ✅ Fotoğraf wizard'ı geçici olarak devre dışı bırakıldı
- ✅ Modül yükleme hataları çözüldü

## 📞 Destek

Sorunlar için:
- GitHub Issues: https://github.com/toftamars/teslimat_planlama/issues
- Email: [your-email@example.com]

## 📄 Lisans

LGPL-3 License

---

**Not**: Bu modül Odoo 16.0 ile uyumludur ve test edilmiştir.