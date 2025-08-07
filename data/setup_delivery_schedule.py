def setup_delivery_schedule(env):
    """Teslimat programını otomatik olarak ayarlar"""
    
    # Varsayılan teslimat programı
    schedule_data = {
        0: {  # Pazartesi
            'name': 'Pazartesi',
            'anadolu': ['Maltepe', 'Kartal', 'Pendik', 'Tuzla'],
            'avrupa': ['Şişli', 'Beşiktaş', 'Beyoğlu', 'Kağıthane']
        },
        1: {  # Salı
            'name': 'Salı',
            'anadolu': ['Üsküdar', 'Kadıköy', 'Ümraniye', 'Ataşehir'],
            'avrupa': ['Sarıyer', 'Eyüpsultan', 'Sultangazi', 'Gaziosmanpaşa']
        },
        2: {  # Çarşamba
            'name': 'Çarşamba',
            'anadolu': ['Üsküdar', 'Kadıköy', 'Ümraniye', 'Ataşehir'],
            'avrupa': ['Bağcılar', 'Bahçelievler', 'Bakırköy', 'Güngören', 'Esenler', 'Zeytinburnu', 'Bayrampaşa', 'Fatih']
        },
        3: {  # Perşembe
            'name': 'Perşembe',
            'anadolu': ['Maltepe', 'Kartal', 'Pendik', 'Tuzla'],
            'avrupa': ['Küçükçekmece', 'Silivri', 'Çatalca', 'Arnavutköy', 'Bakırköy']
        },
        4: {  # Cuma
            'name': 'Cuma',
            'anadolu': ['Üsküdar', 'Kadıköy', 'Ümraniye', 'Ataşehir'],
            'avrupa': ['Küçükçekmece', 'Silivri', 'Çatalca', 'Arnavutköy', 'Bakırköy']
        },
        5: {  # Cumartesi
            'name': 'Cumartesi',
            'anadolu': ['Beykoz', 'Çekmeköy', 'Sancaktepe', 'Şile', 'Sultanbeyli'],
            'avrupa': ['Küçükçekmece', 'Silivri', 'Çatalca', 'Arnavutköy', 'Bakırköy']
        },
        6: {  # Pazar
            'name': 'Pazar',
            'anadolu': [],
            'avrupa': []
        }
    }
    
    for day_num, data in schedule_data.items():
        # Günü oluştur
        day = env['delivery.schedule.day'].search([('day_number', '=', day_num)], limit=1)
        if not day:
            day = env['delivery.schedule.day'].create({
                'name': data['name'],
                'day_number': day_num,
                'is_active': day_num != 6  # Pazar pasif
            })
        
        # Bölgeleri oluştur ve ata
        for continent, regions in [('anadolu', data['anadolu']), ('avrupa', data['avrupa'])]:
            for region_name in regions:
                region = env['delivery.region'].search([('name', '=', region_name)], limit=1)
                if not region:
                    region = env['delivery.region'].create({
                        'name': region_name,
                        'code': region_name.upper().replace(' ', '_'),
                        'continent': continent
                    })
                
                if continent == 'anadolu':
                    day.anadolu_regions = [(4, region.id)]
                else:
                    day.avrupa_regions = [(4, region.id)]
    
    print("Teslimat programı başarıyla ayarlandı!")
