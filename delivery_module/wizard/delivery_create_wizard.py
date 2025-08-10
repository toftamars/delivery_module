from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class DeliveryCreateWizard(models.TransientModel):
    _name = 'delivery.create.wizard'
    _description = 'Teslimat Oluşturma Sihirbazı'
    _transient_max_hours = 24  # 24 saat sonra otomatik temizle

    @api.model
    def default_get(self, fields_list):
        """Context'ten gelen default değerleri al"""
        res = super().default_get(fields_list)
        
        # Debug için context'i yazdır
        _logger.info(f"=== WIZARD DEBUG START ===")
        _logger.info(f"Wizard context: {self.env.context}")
        _logger.info(f"Context keys: {list(self.env.context.keys())}")
        _logger.info(f"Context values: {dict(self.env.context)}")
        _logger.info(f"Context type: {type(self.env.context)}")
        
        # URL'den gelen parametreleri kontrol et
        _logger.info(f"Request params: {self.env.context.get('params', {})}")
        
        # Context'ten default değerleri al
        if 'default_date' in self.env.context:
            res['date'] = self.env.context['default_date']
            _logger.info(f"Date set to: {res['date']}")
        else:
            _logger.info("Date NOT found in context")
        
        if 'default_vehicle_id' in self.env.context:
            res['vehicle_id'] = self.env.context['default_vehicle_id']
            _logger.info(f"Vehicle set to: {res['vehicle_id']}")
        else:
            _logger.info("Vehicle NOT found in context")
        
        if 'default_district_id' in self.env.context and self.env.context['default_district_id'] not in [False, 'False', None, 'null']:
            res['district_id'] = self.env.context['default_district_id']
            _logger.info(f"District set to: {res['district_id']}")
        else:
            _logger.info(f"District not set, context value: {self.env.context.get('default_district_id')}")
        
        if 'default_delivery_type' in self.env.context:
            res['delivery_type'] = self.env.context['default_delivery_type']
            _logger.info(f"Delivery type set to: {res['delivery_type']}")
        else:
            _logger.info("Delivery type NOT found in context")
        
        _logger.info(f"Final default_get result: {res}")
        _logger.info(f"=== WIZARD DEBUG END ===")
        return res

    # Teslimat türü seçimi
    delivery_type = fields.Selection([
        ('transfer', 'Transfer No ile Teslimat'),
        ('manual', 'Manuel Teslimat')
    ], string='Teslimat Türü', required=True, default='transfer')
    
    date = fields.Date('Teslimat Tarihi', required=True, default=fields.Date.context_today)
    vehicle_id = fields.Many2one('delivery.vehicle', string='Araç', required=True, ondelete='cascade')
    picking_name = fields.Char('Transfer Numarası', help='Transfer numarasını girin (örn: WH/OUT/00001)')
    picking_id = fields.Many2one('stock.picking', string='Seçilen Transfer', readonly=True)
    district_id = fields.Many2one('res.city.district', string='İlçe', required=True)
    available_dates = fields.Text('Uygun Teslimat Günleri', readonly=True)
    vehicle_info = fields.Text('Araç Bilgileri', readonly=True)
    
    # Manuel teslimat alanları
    manual_task = fields.Text('Yapılacak İş', help='Manuel teslimat için yapılacak işi açıklayın')
    manual_partner_id = fields.Many2one('res.partner', string='Müşteri', help='Manuel teslimat için müşteri seçin (opsiyonel)')
    phone = fields.Char('Telefon', help='İletişim için telefon numarası (opsiyonel)')
    note = fields.Text('Not', help='Teslimat hakkında ek notlar (opsiyonel)')

    @api.onchange('delivery_type')
    def _onchange_delivery_type(self):
        """Teslimat türü değiştiğinde alanları ve araç domainini güncelle"""
        if self.delivery_type == 'manual':
            # Manuel teslimat seçildiğinde transfer alanlarını temizle
            self.picking_name = False
            self.picking_id = False
            # Araç domainini Anadolu ve Avrupa dışı ile sınırla
            return {'domain': {'vehicle_id': [('vehicle_type', 'not in', ['anadolu', 'avrupa'])]}}
        else:
            # Transfer seçildiğinde manuel alanları temizle ve domaini kaldır
            self.manual_task = False
            self.manual_partner_id = False
            return {'domain': {'vehicle_id': []}}

    @api.onchange('picking_name')
    def _onchange_picking_name(self):
        if self.picking_name and self.delivery_type == 'transfer':
            # Transfer numarasını temizle (boşlukları kaldır)
            picking_name_clean = self.picking_name.strip()
            
            picking = self.env['stock.picking'].search([
                ('name', '=', picking_name_clean),
                ('state', 'in', ['confirmed', 'assigned', 'done'])
            ], limit=1)
            
            if picking:
                self.picking_id = picking.id
                # İlçe otomatik gelmez, manuel seçim yapılacak
            else:
                self.picking_id = False
                return {
                    'warning': {
                        'title': 'Uyarı',
                        'message': f'"{picking_name_clean}" numaralı transfer bulunamadı veya uygun durumda değil. Lütfen transfer numarasını kontrol edin.'
                    }
                }

    @api.onchange('district_id')
    def _onchange_district_id(self):
        if self.district_id:
            # İlçeye göre uygun teslimat günlerini getir
            # Teslimat günlerinde bu ilçenin olup olmadığını kontrol et
            delivery_days = self.env['delivery.day'].search([
                ('active', '=', True),
                ('district_ids', 'in', self.district_id.id)
            ])
            
            if delivery_days:
                # Sadece bu ilçe için uygun olan günleri göster
                available_days = []
                for day in delivery_days.sorted('sequence'):
                    if self.district_id in day.district_ids:
                        available_days.append(day.name)
                
                if available_days:
                    days_text = ', '.join(available_days)
                    self.available_dates = f"Bu ilçede teslimat yapılabilecek günler: {days_text}"
                else:
                    self.available_dates = "Bu ilçe için teslimat günü tanımlanmamış."
            else:
                self.available_dates = "Bu ilçe için teslimat günü tanımlanmamış."
            
            # Tüm araçlar her ilçe için görünür olsun
            return {'domain': {'vehicle_id': []}}
        else:
            self.available_dates = ''
            # İlçe seçilmediğinde domaini kaldır
            return {'domain': {'vehicle_id': []}}

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        """Araç değiştiğinde ilçe domainini güncelle"""
        # Tüm ilçeler her araç için görünür olsun
        return {'domain': {'district_id': []}}

    @api.onchange('vehicle_id', 'date')
    def _onchange_vehicle_date(self):
        if self.vehicle_id and self.date and not self.env.user.has_group('delivery_module.group_delivery_manager'):
            # Aracın o günkü teslimat sayısını kontrol et
            today_count = self.env['delivery.document'].search_count([
                ('vehicle_id', '=', self.vehicle_id.id),
                ('date', '=', self.date),
                ('state', 'in', ['draft', 'ready'])
            ])
            
            remaining = self.vehicle_id.daily_limit - today_count
            self.vehicle_info = f"{self.vehicle_id.name} - Bugünkü teslimat: {today_count}/{self.vehicle_id.daily_limit} (Kalan: {remaining})"
            
            if today_count >= self.vehicle_id.daily_limit:
                # Teslimat yöneticisi için sadece uyarı ver, engelleme
                if not self.env.user.has_group('delivery_module.group_delivery_manager'):
                    return {
                        'warning': {
                            'title': 'Uyarı',
                            'message': f'{self.vehicle_id.name} aracının günlük limiti ({self.vehicle_id.daily_limit}) dolmuş. İlave teslimat için yetkilendirme gerekli.'
                        }
                    }
                else:
                    return {
                        'warning': {
                            'title': 'Uyarı - Teslimat Yöneticisi',
                            'message': f'{self.vehicle_id.name} aracının günlük limiti ({self.vehicle_id.daily_limit}) dolmuş, ancak teslimat yöneticisi olarak ilave teslimat oluşturabilirsiniz.'
                        }
                    }
        else:
            self.vehicle_info = ''

    @api.onchange('date')
    def _onchange_date(self):
        # Sadece transfer teslimatları için tarih kontrolü yap (manuel teslimatlar için kontrol yok)
        if self.date and self.district_id and self.delivery_type == 'transfer' and not self.env.user.has_group('delivery_module.group_delivery_manager'):
            day_of_week = str(self.date.weekday())
            
            # Debug için gün bilgisini yazdır
            day_names = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
            selected_day_name = day_names[self.date.weekday()]
            
            available_day = self.env['delivery.day'].search([
                ('day_of_week', '=', day_of_week),
                ('active', '=', True),
                ('district_ids', 'in', self.district_id.id)
            ], limit=1)
            
            if not available_day:
                day_names = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
                selected_day_name = day_names[self.date.weekday()]
                
                # Teslimat yöneticisi için sadece uyarı ver, engelleme
                if not self.env.user.has_group('delivery_module.group_delivery_manager'):
                    raise UserError(_(f'Seçilen tarih ({self.date.strftime("%d/%m/%Y")} - {selected_day_name}) bu ilçe için uygun bir teslimat günü değil.'))
                else:
                    # Teslimat yöneticisi için uyarı ver ama devam et
                    print(f"Teslimat yöneticisi uygun olmayan tarihte teslimat oluşturuyor: {self.date.strftime('%d/%m/%Y')} - {selected_day_name}")

    def action_create_delivery(self):
        if self.delivery_type == 'transfer':
            # Transfer teslimatı için kontroller
            if not self.picking_name:
                raise UserError(_('Lütfen transfer numarası girin.'))
            
            # Transfer numarasını temizle ve tekrar ara
            picking_name_clean = self.picking_name.strip()
            picking = self.env['stock.picking'].search([
                ('name', '=', picking_name_clean),
                ('state', 'in', ['confirmed', 'assigned', 'done'])
            ], limit=1)
            
            if not picking:
                raise UserError(_(f'"{picking_name_clean}" numaralı transfer bulunamadı veya uygun durumda değil. Lütfen transfer numarasını kontrol edin.'))

            # Transfer zaten bir teslimat belgesine atanmış mı kontrol et
            existing_delivery = self.env['delivery.document'].search([
                ('picking_ids', 'in', picking.id)
            ], limit=1)
            
            if existing_delivery:
                raise UserError(_(f'Bu transfer zaten "{existing_delivery.name}" teslimat belgesine atanmış.'))
            
            partner_id = picking.partner_id.id
            delivery_address = picking.partner_id.street or ""
            picking_ids = [(4, picking.id)]
            
        else:
            # Manuel teslimat için kontroller
            if not self.manual_task:
                raise UserError(_('Lütfen yapılacak işi açıklayın.'))
            
            # Müşteri seçimi opsiyonel - eğer seçilmişse kullan, seçilmemişse None
            partner_id = self.manual_partner_id.id if self.manual_partner_id else False
            delivery_address = ""
            picking_ids = []

        if not self.district_id:
            raise UserError(_('Lütfen ilçe seçin.'))

        if not self.vehicle_id:
            raise UserError(_('Lütfen araç seçin.'))

        # İlçe-gün uyumluluğu kontrolü (sadece transfer teslimatları için)
        if self.delivery_type == 'transfer' and not self.env.user.has_group('delivery_module.group_delivery_manager'):
            day_of_week = str(self.date.weekday())
            day_names = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
            selected_day_name = day_names[self.date.weekday()]
            
            # Debug için log ekle
            print(f"=== İLÇE-GÜN KONTROLÜ (TRANSFER) ===")
            print(f"Seçilen tarih: {self.date} ({selected_day_name})")
            print(f"Seçilen ilçe: {self.district_id.name}")
            print(f"Gün numarası: {day_of_week}")
            
            available_day = self.env['delivery.day'].search([
                ('day_of_week', '=', day_of_week),
                ('active', '=', True),
                ('district_ids', 'in', self.district_id.id)
            ], limit=1)
            
            print(f"Bulunan teslimat günü: {available_day.name if available_day else 'BULUNAMADI'}")
            print(f"Bu günün ilçeleri: {[d.name for d in available_day.district_ids] if available_day else 'YOK'}")
            print(f"İlçe bu günde var mı: {self.district_id in available_day.district_ids if available_day else False}")
            print(f"=== KONTROL SONU ===")
            
            if not available_day:
                raise UserError(_(f'Seçilen tarih ({self.date.strftime("%d/%m/%Y")} - {selected_day_name}) bu ilçe için uygun bir teslimat günü değil.'))
            
            # İlçe bu günde var mı kontrol et
            if self.district_id not in available_day.district_ids:
                raise UserError(_(f'"{self.district_id.name}" ilçesi {selected_day_name} gününde teslimat yapılamaz. Uygun günler: {", ".join([d.name for d in available_day.district_ids])}'))

        # Aracın günlük limitini kontrol et
        today_count = self.env['delivery.document'].search_count([
            ('vehicle_id', '=', self.vehicle_id.id),
            ('date', '=', self.date),
            ('state', 'in', ['draft', 'ready'])
        ])
        
        if today_count >= self.vehicle_id.daily_limit:
            # Teslimat yöneticisi için sadece uyarı ver, engelleme
            if not self.env.user.has_group('delivery_module.group_delivery_manager'):
                raise UserError(_(f'{self.vehicle_id.name} aracının günlük limiti ({self.vehicle_id.daily_limit}) dolmuş. İlave teslimat için yetkilendirme gerekli.'))
            else:
                # Teslimat yöneticisi için uyarı ver ama devam et
                print(f"Teslimat yöneticisi limit aşımında teslimat oluşturuyor: {self.vehicle_id.name} - {today_count}/{self.vehicle_id.daily_limit}")

        # Teslimat gününü belirle
        day_of_week = str(self.date.weekday())
        delivery_day = self.env['delivery.day'].search([
            ('day_of_week', '=', day_of_week),
            ('active', '=', True)
        ], limit=1)
        
        # Manuel teslimatlar için teslimat günü kontrolü yapma
        if self.delivery_type == 'transfer' and not delivery_day:
            raise UserError(_('Seçilen tarih için teslimat günü bulunamadı.'))
        
        # Manuel teslimatlar için teslimat günü yoksa None olarak bırak
        delivery_day_id = delivery_day.id if delivery_day else False

        delivery = self.env['delivery.document'].create({
            'date': self.date,
            'vehicle_id': self.vehicle_id.id,
            'partner_id': partner_id,
            'district_id': self.district_id.id,
            'delivery_day_id': delivery_day_id,
            'picking_ids': picking_ids,
            'note': self.note,
            'state': 'ready',
        })

        return {
            'name': _('Teslimat Belgesi'),
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.document',
            'view_mode': 'form',
            'res_id': delivery.id,
        }
