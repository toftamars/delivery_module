# -*- coding: utf-8 -*-

def setup_delivery_schedule(env):
    """
    Teslimat programını otomatik olarak ayarlar
    """
    
    print("Teslimat programı ayarlanıyor...")
    
    # Teslimat günlerini al - ref yerine search kullanarak
    monday = env['delivery.day'].search([('name', '=', 'Pazartesi')], limit=1)
    tuesday = env['delivery.day'].search([('name', '=', 'Salı')], limit=1)
    wednesday = env['delivery.day'].search([('name', '=', 'Çarşamba')], limit=1)
    thursday = env['delivery.day'].search([('name', '=', 'Perşembe')], limit=1)
    friday = env['delivery.day'].search([('name', '=', 'Cuma')], limit=1)
    saturday = env['delivery.day'].search([('name', '=', 'Cumartesi')], limit=1)
    
    # Eğer günler bulunamazsa, oluştur
    if not monday:
        monday = env['delivery.day'].create({'name': 'Pazartesi', 'day_of_week': 0, 'sequence': 10})
    if not tuesday:
        tuesday = env['delivery.day'].create({'name': 'Salı', 'day_of_week': 1, 'sequence': 20})
    if not wednesday:
        wednesday = env['delivery.day'].create({'name': 'Çarşamba', 'day_of_week': 2, 'sequence': 30})
    if not thursday:
        thursday = env['delivery.day'].create({'name': 'Perşembe', 'day_of_week': 3, 'sequence': 40})
    if not friday:
        friday = env['delivery.day'].create({'name': 'Cuma', 'day_of_week': 4, 'sequence': 50})
    if not saturday:
        saturday = env['delivery.day'].create({'name': 'Cumartesi', 'day_of_week': 5, 'sequence': 60})
    
    print(f"Teslimat günleri bulundu: {monday.name}, {tuesday.name}, {wednesday.name}, {thursday.name}, {friday.name}, {saturday.name}")
    
    # İlçeleri al
    # Anadolu Yakası
    maltepe = env['res.city.district'].search([('name', '=', 'Maltepe')], limit=1)
    kartal = env['res.city.district'].search([('name', '=', 'Kartal')], limit=1)
    pendik = env['res.city.district'].search([('name', '=', 'Pendik')], limit=1)
    tuzla = env['res.city.district'].search([('name', '=', 'Tuzla')], limit=1)
    uskudar = env['res.city.district'].search([('name', '=', 'Üsküdar')], limit=1)
    kadikoy = env['res.city.district'].search([('name', '=', 'Kadıköy')], limit=1)
    atasehir = env['res.city.district'].search([('name', '=', 'Ataşehir')], limit=1)
    umraniye = env['res.city.district'].search([('name', '=', 'Ümraniye')], limit=1)
    sancaktepe = env['res.city.district'].search([('name', '=', 'Sancaktepe')], limit=1)
    cekmekoy = env['res.city.district'].search([('name', '=', 'Çekmeköy')], limit=1)
    beykoz = env['res.city.district'].search([('name', '=', 'Beykoz')], limit=1)
    sile = env['res.city.district'].search([('name', '=', 'Şile')], limit=1)
    sultanbeyli = env['res.city.district'].search([('name', '=', 'Sultanbeyli')], limit=1)
    
    # Avrupa Yakası
    beyoglu = env['res.city.district'].search([('name', '=', 'Beyoğlu')], limit=1)
    sisli = env['res.city.district'].search([('name', '=', 'Şişli')], limit=1)
    besiktas = env['res.city.district'].search([('name', '=', 'Beşiktaş')], limit=1)
    kagithane = env['res.city.district'].search([('name', '=', 'Kağıthane')], limit=1)
    sariyer = env['res.city.district'].search([('name', '=', 'Sarıyer')], limit=1)
    bakirkoy = env['res.city.district'].search([('name', '=', 'Bakırköy')], limit=1)
    bahcelievler = env['res.city.district'].search([('name', '=', 'Bahçelievler')], limit=1)
    gungoren = env['res.city.district'].search([('name', '=', 'Güngören')], limit=1)
    esenler = env['res.city.district'].search([('name', '=', 'Esenler')], limit=1)
    bagcilar = env['res.city.district'].search([('name', '=', 'Bağcılar')], limit=1)
    eyupsultan = env['res.city.district'].search([('name', '=', 'Eyüpsultan')], limit=1)
    gaziosmanpasa = env['res.city.district'].search([('name', '=', 'Gaziosmanpaşa')], limit=1)
    kucukcekmece = env['res.city.district'].search([('name', '=', 'Küçükçekmece')], limit=1)
    avcilar = env['res.city.district'].search([('name', '=', 'Avcılar')], limit=1)
    basaksehir = env['res.city.district'].search([('name', '=', 'Başakşehir')], limit=1)
    sultangazi = env['res.city.district'].search([('name', '=', 'Sultangazi')], limit=1)
    arnavutkoy = env['res.city.district'].search([('name', '=', 'Arnavutköy')], limit=1)
    fatih = env['res.city.district'].search([('name', '=', 'Fatih')], limit=1)
    zeytinburnu = env['res.city.district'].search([('name', '=', 'Zeytinburnu')], limit=1)
    bayrampasa = env['res.city.district'].search([('name', '=', 'Bayrampaşa')], limit=1)
    esenyurt = env['res.city.district'].search([('name', '=', 'Esenyurt')], limit=1)
    beylikduzu = env['res.city.district'].search([('name', '=', 'Beylikdüzü')], limit=1)
    silivri = env['res.city.district'].search([('name', '=', 'Silivri')], limit=1)
    catalca = env['res.city.district'].search([('name', '=', 'Çatalca')], limit=1)
    
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