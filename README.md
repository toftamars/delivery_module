# Teslimat Planlama Modülü

Bu Odoo modülü teslimat planlama ve rota optimizasyonu için geliştirilmiştir.

## Özellikler

- **Teslimat Planlama**: Teslimat planları oluşturma ve yönetme
- **Teslimat Noktaları**: Teslimat noktalarını tanımlama ve sıralama
- **Araç Yönetimi**: Araç kapasitesi ve müsaitlik durumu takibi
- **Rota Optimizasyonu**: Mesafe ve süre hesaplamaları
- **Durum Takibi**: Teslimat durumlarının takibi

## Kurulum

1. Modülü Odoo addons klasörüne kopyalayın
2. Odoo'yu yeniden başlatın
3. Uygulamalar menüsünden "Teslimat Planlama" modülünü yükleyin

## Kullanım

### Teslimat Planı Oluşturma

1. "Teslimat Planlama" menüsüne gidin
2. "Teslimat Planları" alt menüsünü seçin
3. "Oluştur" butonuna tıklayın
4. Plan adı, tarih, araç ve sürücü bilgilerini girin
5. Teslimat noktalarını ekleyin

### Teslimat Noktası Ekleme

1. Teslimat planı formunda "Teslimat Noktaları" sekmesine gidin
2. "Ekle" butonuna tıklayın
3. Müşteri, adres ve diğer bilgileri girin
4. Mesafe ve süre bilgilerini ekleyin

## Modeller

### delivery.planning
Teslimat planlarını yönetir.

**Alanlar:**
- name: Plan adı
- date: Plan tarihi
- vehicle_id: Araç
- driver_id: Sürücü
- state: Durum (taslak, onaylandı, devam ediyor, tamamlandı, iptal edildi)
- total_distance: Toplam mesafe
- estimated_duration: Tahmini süre

### delivery.point
Teslimat noktalarını yönetir.

**Alanlar:**
- name: Nokta adı
- partner_id: Müşteri
- address: Adres
- distance_from_previous: Önceki noktadan mesafe
- estimated_time: Tahmini süre
- state: Durum

## Güvenlik

Modül aşağıdaki güvenlik kurallarını içerir:
- Kullanıcılar: Okuma, yazma, oluşturma (silme yok)
- Yöneticiler: Tam erişim

## Geliştirme

Bu modül Odoo 16.0 ile uyumlu olarak geliştirilmiştir.

## Lisans

LGPL-3
