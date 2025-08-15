# -*- coding: utf-8 -*-

def setup_delivery_schedule(env):
    """
    Teslimat programını otomatik olarak ayarlar
    """
    
    print("Teslimat programı ayarlanıyor...")
    
    # Teslimat günlerini al
    monday = env.ref('teslimat_planlama.delivery_day_monday')
    tuesday = env.ref('teslimat_planlama.delivery_day_tuesday')
    wednesday = env.ref('teslimat_planlama.delivery_day_wednesday')
    thursday = env.ref('teslimat_planlama.delivery_day_thursday')
    friday = env.ref('teslimat_planlama.delivery_day_friday')
    saturday = env.ref('teslimat_planlama.delivery_day_saturday')
    
    print(f"Teslimat günleri bulundu: {monday.name}, {tuesday.name}, {wednesday.name}, {thursday.name}, {friday.name}, {saturday.name}")
    
    # İlçeleri al
    # Anadolu Yakası
    maltepe = env.ref('teslimat_planlama.district_maltepe')
    kartal = env.ref('teslimat_planlama.district_kartal')
    pendik = env.ref('teslimat_planlama.district_pendik')
    tuzla = env.ref('teslimat_planlama.district_tuzla')
    uskudar = env.ref('teslimat_planlama.district_uskudar')
    kadikoy = env.ref('teslimat_planlama.district_kadikoy')
    atasehir = env.ref('teslimat_planlama.district_atasehir')
    umraniye = env.ref('teslimat_planlama.district_umraniye')
    sancaktepe = env.ref('teslimat_planlama.district_sancaktepe')
    cekmekoy = env.ref('teslimat_planlama.district_cekmekoy')
    beykoz = env.ref('teslimat_planlama.district_beykoz')
    sile = env.ref('teslimat_planlama.district_sile')
    sultanbeyli = env.ref('teslimat_planlama.district_sultanbeyli')
    
    # Avrupa Yakası
    beyoglu = env.ref('teslimat_planlama.district_beyoglu')
    sisli = env.ref('teslimat_planlama.district_sisli')
    besiktas = env.ref('teslimat_planlama.district_besiktas')
    kagithane = env.ref('teslimat_planlama.district_kagithane')
    sariyer = env.ref('teslimat_planlama.district_sariyer')
    bakirkoy = env.ref('teslimat_planlama.district_bakirkoy')
    bahcelievler = env.ref('teslimat_planlama.district_bahcelievler')
    gungoren = env.ref('teslimat_planlama.district_gungoren')
    esenler = env.ref('teslimat_planlama.district_esenler')
    bagcilar = env.ref('teslimat_planlama.district_bagcilar')
    eyupsultan = env.ref('teslimat_planlama.district_eyupsultan')
    gaziosmanpasa = env.ref('teslimat_planlama.district_gaziosmanpasa')
    kucukcekmece = env.ref('teslimat_planlama.district_kucukcekmece')
    avcilar = env.ref('teslimat_planlama.district_avcilar')
    basaksehir = env.ref('teslimat_planlama.district_basaksehir')
    sultangazi = env.ref('teslimat_planlama.district_sultangazi')
    arnavutkoy = env.ref('teslimat_planlama.district_arnavutkoy')
    fatih = env.ref('teslimat_planlama.district_fatih')
    zeytinburnu = env.ref('teslimat_planlama.district_zeytinburnu')
    bayrampasa = env.ref('teslimat_planlama.district_bayrampasa')
    esenyurt = env.ref('teslimat_planlama.district_esenyurt')
    beylikduzu = env.ref('teslimat_planlama.district_beylikduzu')
    silivri = env.ref('teslimat_planlama.district_silivri')
    catalca = env.ref('teslimat_planlama.district_catalca')
    
    print(f"İlçeler bulundu: {len([maltepe, kartal, pendik, tuzla, uskudar, kadikoy, atasehir, umraniye, sancaktepe, cekmekoy, beykoz, sile, sultanbeyli, beyoglu, sisli, besiktas, kagithane, sariyer, bakirkoy, bahcelievler, gungoren, esenler, bagcilar, eyupsultan, gaziosmanpasa, kucukcekmece, avcilar, basaksehir, sultangazi, arnavutkoy, fatih, zeytinburnu, bayrampasa, esenyurt, beylikduzu, silivri, catalca])} ilçe")
    
    # Önce tüm teslimat günlerini temizle
    print("Teslimat günleri temizleniyor...")
    monday.district_ids = [(5, 0, 0)]
    tuesday.district_ids = [(5, 0, 0)]
    wednesday.district_ids = [(5, 0, 0)]
    thursday.district_ids = [(5, 0, 0)]
    friday.district_ids = [(5, 0, 0)]
    saturday.district_ids = [(5, 0, 0)]
    
    # Pazartesi - Anadolu Yakası + Avrupa Yakası
    print("Pazartesi ilçeleri atanıyor...")
    monday.district_ids = [(4, maltepe.id), (4, kartal.id), (4, pendik.id), (4, tuzla.id),
                          (4, beyoglu.id), (4, sisli.id), (4, besiktas.id), (4, kagithane.id)]
    
    # Salı - Anadolu Yakası + Avrupa Yakası
    print("Salı ilçeleri atanıyor...")
    tuesday.district_ids = [(4, uskudar.id), (4, kadikoy.id), (4, atasehir.id), (4, umraniye.id),
                           (4, sariyer.id), (4, bakirkoy.id), (4, bahcelievler.id), (4, gungoren.id), (4, esenler.id), (4, bagcilar.id)]
    
    # Çarşamba - Anadolu Yakası + Avrupa Yakası
    print("Çarşamba ilçeleri atanıyor...")
    wednesday.district_ids = [(4, uskudar.id), (4, kadikoy.id), (4, atasehir.id), (4, umraniye.id),
                             (4, beyoglu.id), (4, sisli.id), (4, besiktas.id), (4, kagithane.id)]
    
    # Perşembe - Anadolu Yakası + Avrupa Yakası
    print("Perşembe ilçeleri atanıyor...")
    thursday.district_ids = [(4, uskudar.id), (4, kadikoy.id), (4, atasehir.id), (4, umraniye.id),
                            (4, eyupsultan.id), (4, gaziosmanpasa.id), (4, kucukcekmece.id), (4, avcilar.id), (4, basaksehir.id), (4, sultangazi.id), (4, arnavutkoy.id)]
    
    # Cuma - Anadolu Yakası + Avrupa Yakası
    print("Cuma ilçeleri atanıyor...")
    friday.district_ids = [(4, maltepe.id), (4, kartal.id), (4, pendik.id),
                          (4, fatih.id), (4, zeytinburnu.id), (4, bayrampasa.id)]
    
    # Cumartesi - Anadolu Yakası + Avrupa Yakası
    print("Cumartesi ilçeleri atanıyor...")
    saturday.district_ids = [(4, sancaktepe.id), (4, cekmekoy.id), (4, beykoz.id), (4, sile.id), (4, sultanbeyli.id),
                            (4, esenyurt.id), (4, beylikduzu.id), (4, silivri.id), (4, catalca.id)]
    
    # Veritabanını kaydet
    env.cr.commit()
    
    print("Teslimat programı başarıyla ayarlandı!")
    print(f"Pazartesi: {len(monday.district_ids)} ilçe")
    print(f"Salı: {len(tuesday.district_ids)} ilçe")
    print(f"Çarşamba: {len(wednesday.district_ids)} ilçe")
    print(f"Perşembe: {len(thursday.district_ids)} ilçe")
    print(f"Cuma: {len(friday.district_ids)} ilçe")
    print(f"Cumartesi: {len(saturday.district_ids)} ilçe")
    
    print("\nANADOLU YAKASI:")
    print("Pazartesi: Maltepe, Kartal, Pendik, Tuzla")
    print("Salı: Üsküdar, Kadıköy, Ataşehir, Ümraniye")
    print("Çarşamba: Üsküdar, Kadıköy, Ataşehir, Ümraniye")
    print("Perşembe: Üsküdar, Kadıköy, Ataşehir, Ümraniye")
    print("Cuma: Maltepe, Kartal, Pendik")
    print("Cumartesi: Sancaktepe, Çekmeköy, Beykoz, Şile, Sultanbeyli")
    
    print("\nAVRUPA YAKASI:")
    print("Pazartesi: Beyoğlu, Şişli, Beşiktaş, Kağıthane")
    print("Salı: Sarıyer, Bakırköy, Bahçelievler, Güngören, Esenler, Bağcılar")
    print("Çarşamba: Beyoğlu, Şişli, Beşiktaş, Kağıthane")
    print("Perşembe: Eyüpsultan, Gaziosmanpaşa, Küçükçekmece, Avcılar, Başakşehir, Sultangazi, Arnavutköy")
    print("Cuma: Fatih, Zeytinburnu, Bayrampaşa")
    print("Cumartesi: Esenyurt, Beylikdüzü, Silivri, Çatalca") 