from odoo import models, fields, api, _


class DeliveryRegion(models.Model):
    _name = 'delivery.region'
    _description = 'Teslimat Bölgesi'
    _order = 'name'

    name = fields.Char('Bölge Adı', required=True)
    code = fields.Char('Bölge Kodu', required=True)
    continent = fields.Selection([
        ('anadolu', 'Anadolu'),
        ('avrupa', 'Avrupa')
    ], string='Kıta', required=True)
    
    active_days = fields.Many2many('delivery.schedule.day', string='Aktif Günler')
    is_active = fields.Boolean('Aktif', default=True)
    
    # Bölge istatistikleri
    total_deliveries = fields.Integer('Toplam Teslimat', compute='_compute_region_stats')
    total_distance = fields.Float('Toplam Mesafe (km)', compute='_compute_region_stats')
    average_delivery_time = fields.Float('Ortalama Teslimat Süresi (saat)', compute='_compute_region_stats')
    
    @api.depends('delivery_point_ids')
    def _compute_region_stats(self):
        for region in self:
            points = self.env['delivery.point'].search([
                ('region_id', '=', region.id),
                ('state', '=', 'completed')
            ])
            
            region.total_deliveries = len(points)
            region.total_distance = sum(points.mapped('distance_from_previous'))
            region.average_delivery_time = sum(points.mapped('estimated_time')) / len(points) if points else 0.0


class DeliveryScheduleDay(models.Model):
    _name = 'delivery.schedule.day'
    _description = 'Teslimat Programı Günü'
    _order = 'day_number'

    name = fields.Char('Gün Adı', required=True)
    day_number = fields.Integer('Gün Numarası', required=True)  # 0=Pazartesi, 1=Salı, vb.
    is_active = fields.Boolean('Aktif', default=True)
    
    # Günlük bölge atamaları
    anadolu_regions = fields.Many2many('delivery.region', 'delivery_day_anadolu_rel', 
                                      'day_id', 'region_id', string='Anadolu Bölgeleri',
                                      domain="[('continent', '=', 'anadolu')]")
    avrupa_regions = fields.Many2many('delivery.region', 'delivery_day_avrupa_rel', 
                                     'day_id', 'region_id', string='Avrupa Bölgeleri',
                                     domain="[('continent', '=', 'avrupa')]")
    
    @api.model
    def create_default_schedule(self):
        """Varsayılan teslimat programını oluşturur"""
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
            day = self.create({
                'name': data['name'],
                'day_number': day_num,
                'is_active': day_num != 6  # Pazar pasif
            })
            
            # Bölgeleri oluştur ve ata
            for continent, regions in [('anadolu', data['anadolu']), ('avrupa', data['avrupa'])]:
                for region_name in regions:
                    region = self.env['delivery.region'].search([('name', '=', region_name)], limit=1)
                    if not region:
                        region = self.env['delivery.region'].create({
                            'name': region_name,
                            'code': region_name.upper().replace(' ', '_'),
                            'continent': continent
                        })
                    
                    if continent == 'anadolu':
                        day.anadolu_regions = [(4, region.id)]
                    else:
                        day.avrupa_regions = [(4, region.id)]
