from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DeliveryDay(models.Model):
    _name = 'delivery.day'
    _description = 'Teslimat Günü'
    _order = 'sequence, id'

    name = fields.Char('Gün Adı', required=True)
    day_of_week = fields.Selection([
        ('0', 'Pazartesi'),
        ('1', 'Salı'),
        ('2', 'Çarşamba'),
        ('3', 'Perşembe'),
        ('4', 'Cuma'),
        ('5', 'Cumartesi'),
        ('6', 'Pazar'),
    ], string='Haftanın Günü', required=True)
    sequence = fields.Integer('Sıra', default=10)
    active = fields.Boolean('Aktif', default=True)
    
    # Geçici kapatma özelliği
    is_temporarily_closed = fields.Boolean('Geçici Olarak Kapalı', default=False)
    closure_reason = fields.Text('Kapatma Sebebi')
    closure_start_date = fields.Date('Kapatma Başlangıç Tarihi')
    closure_end_date = fields.Date('Kapatma Bitiş Tarihi')
    closed_by = fields.Many2one('res.users', string='Kapatan Kullanıcı', readonly=True)
    closed_date = fields.Datetime('Kapatma Tarihi', readonly=True)
    
    # İlçe ilişkisi (sadece görüntüleme amaçlı)
    district_ids = fields.Many2many('res.city.district', string='Teslimat Yapılan İlçeler', readonly=True)
    district_count = fields.Integer('İlçe Sayısı', compute='_compute_district_count')
    district_list = fields.Text('Teslimat İlçeleri', compute='_compute_district_list', readonly=True)
    
    # Yaka bazlı ilçe listeleri
    anatolian_districts = fields.Text('Anadolu Yakası İlçeleri', compute='_compute_anatolian_districts', readonly=True)
    european_districts = fields.Text('Avrupa Yakası İlçeleri', compute='_compute_european_districts', readonly=True)
    
    # Durum hesaplama
    status = fields.Selection([
        ('active', 'Aktif'),
        ('temporarily_closed', 'Geçici Kapalı'),
        ('inactive', 'Pasif')
    ], string='Durum', compute='_compute_status', store=True)

    @api.depends('active', 'is_temporarily_closed', 'closure_start_date', 'closure_end_date')
    def _compute_status(self):
        for day in self:
            if not day.active:
                day.status = 'inactive'
            elif day.is_temporarily_closed:
                day.status = 'temporarily_closed'
            else:
                day.status = 'active'

    def _compute_district_count(self):
        for day in self:
            day.district_count = len(day.district_ids)

    def _compute_district_list(self):
        for day in self:
            if day.district_ids:
                # Anadolu Yakası ilçeleri
                anatolian_district_names = [
                    'Maltepe', 'Kartal', 'Pendik', 'Tuzla', 'Üsküdar', 'Kadıköy', 
                    'Ataşehir', 'Ümraniye', 'Sancaktepe', 'Çekmeköy', 'Beykoz', 
                    'Şile', 'Sultanbeyli'
                ]
                
                anatolian_count = 0
                european_count = 0
                
                for district in day.district_ids:
                    if district.name in anatolian_district_names:
                        anatolian_count += 1
                    else:
                        european_count += 1
                
                # Kısa özet oluştur
                parts = []
                if anatolian_count > 0:
                    parts.append(f"Anadolu: {anatolian_count} ilçe")
                if european_count > 0:
                    parts.append(f"Avrupa: {european_count} ilçe")
                
                day.district_list = " | ".join(parts)
            else:
                day.district_list = "Teslimat ilçesi tanımlanmamış"

    def _compute_anatolian_districts(self):
        """Anadolu Yakası ilçelerini hesaplar"""
        anatolian_district_names = [
            'Maltepe', 'Kartal', 'Pendik', 'Tuzla', 'Üsküdar', 'Kadıköy', 
            'Ataşehir', 'Ümraniye', 'Sancaktepe', 'Çekmeköy', 'Beykoz', 
            'Şile', 'Sultanbeyli'
        ]
        
        for day in self:
            anatolian_districts = []
            for district in day.district_ids.sorted('name'):
                if district.name in anatolian_district_names:
                    anatolian_districts.append(f"{district.name} ({district.city_id.name})")
            
            if anatolian_districts:
                day.anatolian_districts = ", ".join(anatolian_districts)
            else:
                day.anatolian_districts = "Anadolu Yakası ilçesi tanımlanmamış"

    def _compute_european_districts(self):
        """Avrupa Yakası ilçelerini hesaplar"""
        european_district_names = [
            'Beyoğlu', 'Şişli', 'Beşiktaş', 'Kağıthane', 'Sarıyer', 'Bakırköy',
            'Bahçelievler', 'Güngören', 'Esenler', 'Bağcılar', 'Eyüpsultan',
            'Gaziosmanpaşa', 'Küçükçekmece', 'Avcılar', 'Başakşehir', 'Sultangazi',
            'Arnavutköy', 'Fatih', 'Zeytinburnu', 'Bayrampaşa', 'Esenyurt',
            'Beylikdüzü', 'Silivri', 'Çatalca'
        ]
        
        for day in self:
            european_districts = []
            for district in day.district_ids.sorted('name'):
                if district.name in european_district_names:
                    european_districts.append(f"{district.name} ({district.city_id.name})")
            
            if european_districts:
                day.european_districts = ", ".join(european_districts)
            else:
                day.european_districts = "Avrupa Yakası ilçesi tanımlanmamış"

    def action_temporarily_close(self):
        """Geçici kapatma işlemi"""
        return {
            'name': _('Teslimat Gününü Geçici Kapat'),
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.day.closure.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_delivery_day_id': self.id},
        }

    def action_reopen(self):
        """Geçici kapatmayı kaldır"""
        if not self.env.user.has_group('delivery_module.group_delivery_manager'):
            raise UserError(_('Bu işlem için teslimat yöneticisi yetkisi gereklidir.'))
        
        self.write({
            'is_temporarily_closed': False,
            'closure_reason': False,
            'closure_start_date': False,
            'closure_end_date': False,
            'closed_by': False,
            'closed_date': False,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Başarılı'),
                'message': _('%s günü tekrar aktif hale getirildi.') % self.name,
                'type': 'success',
            }
        }

    def action_view_districts(self):
        return {
            'name': f'{self.name} - Teslimat İlçeleri',
            'type': 'ir.actions.act_window',
            'res_model': 'res.city.district',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.district_ids.ids)],
            'context': {'default_delivery_day_ids': [(4, self.id)]},
        }

    @api.model
    def check_availability(self, date, district_id=None):
        """Belirli bir tarih için teslimat günü müsaitlik kontrolü"""
        day_of_week = str(date.weekday())
        domain = [
            ('day_of_week', '=', day_of_week),
            ('active', '=', True),
            ('is_temporarily_closed', '=', False),
        ]
        
        # Eğer kapatma tarihleri belirtilmişse kontrol et
        domain += [
            '|',
            ('closure_start_date', '=', False),
            '|',
            ('closure_end_date', '=', False),
            '&',
            ('closure_start_date', '<=', date),
            ('closure_end_date', '>=', date),
        ]
        
        available_day = self.search(domain, limit=1)
        
        if not available_day:
            return False, _('Bu tarih için teslimat günü bulunmuyor veya geçici olarak kapalı.')
        
        if district_id and district_id not in available_day.district_ids:
            return False, _('Bu ilçe için teslimat günü tanımlanmamış.')
        
        return True, available_day 