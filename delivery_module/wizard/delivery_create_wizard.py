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
    available_date_ids = fields.Text(string='Uygun Tarih ID\'leri', compute='_compute_available_date_ids', store=False)
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
            self.picking_name = False
            self.picking_id = False
            return {'domain': {'vehicle_id': [('vehicle_type', 'not in', ['anadolu', 'avrupa'])]}}
        else:
            self.manual_task = False
            self.manual_partner_id = False
            return {'domain': {'vehicle_id': []}}

    @api.onchange('picking_name')
    def _onchange_picking_name(self):
        if self.picking_name and self.delivery_type == 'transfer':
            picking_name_clean = self.picking_name.strip()
            picking = self.env['stock.picking'].search([
                ('name', '=', picking_name_clean),
                ('state', 'in', ['confirmed', 'assigned', 'done'])
            ], limit=1)
            if picking:
                self.picking_id = picking.id
            else:
                self.picking_id = False
                return {
                    'warning': {
                        'title': 'Uyarı',
                        'message': f'"{picking_name_clean}" numaralı transfer bulunamadı veya uygun durumda değil. Lütfen transfer numarasını kontrol edin.'
                    }
                }

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.vehicle_info = f"{self.vehicle_id.name} - Günlük limit: {self.vehicle_id.daily_limit}"
            self._compute_available_date_ids()
        else:
            self.vehicle_info = ''
            self.available_date_ids = ''
            self.available_dates = ''

    @api.onchange('district_id')
    def _onchange_district_id(self):
        if self.district_id:
            self._compute_available_date_ids()
        else:
            self.available_date_ids = ''
            self.available_dates = ''

    @api.onchange('vehicle_id', 'date')
    def _onchange_vehicle_date(self):
        if self.vehicle_id and self.date:
            today_count = self.env['delivery.document'].search_count([
                ('vehicle_id', '=', self.vehicle_id.id),
                ('date', '=', self.date),
                ('state', 'in', ['draft', 'ready'])
            ])
            if today_count >= self.vehicle_id.daily_limit:
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
                            'title': 'Uyarı',
                            'message': f'{self.vehicle_id.name} aracının günlük limiti ({self.vehicle_id.daily_limit}) dolmuş. Teslimat yöneticisi olarak devam edebilirsiniz.'
                        }
                    }

    @api.depends('vehicle_id', 'district_id')
    def _compute_available_date_ids(self):
        """Uygun ve kapasitesi olan tarihleri hesapla ve kullanıcıya okunur bir liste hazırla"""
        for record in self:
            if not record.vehicle_id or not record.district_id:
                record.available_date_ids = ''
                record.available_dates = ''
                continue
            from datetime import datetime, timedelta
            import calendar as cal
            today = datetime.now().date()
            available_dates_list = []
            readable_lines = []
            day_names_tr = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
            for i in range(30):
                check_date = today + timedelta(days=i)
                day_of_week = str(check_date.weekday())
                delivery_day = self.env['delivery.day'].search([
                    ('day_of_week', '=', day_of_week),
                    ('active', '=', True),
                    ('district_ids', 'in', record.district_id.id)
                ], limit=1)
                if delivery_day:
                    today_count = self.env['delivery.document'].search_count([
                        ('vehicle_id', '=', record.vehicle_id.id),
                        ('date', '=', check_date),
                        ('state', 'in', ['draft', 'ready'])
                    ])
                    if today_count < record.vehicle_id.daily_limit:
                        ymd = check_date.strftime('%Y-%m-%d')
                        available_dates_list.append(ymd)
                        readable_lines.append(f"- {check_date.strftime('%d/%m/%Y')} ({day_names_tr[check_date.weekday()]})")
            record.available_date_ids = ','.join(available_dates_list)
            record.available_dates = '\n'.join(readable_lines)
            if record.date and record.date.strftime('%Y-%m-%d') not in available_dates_list:
                record.date = False

    @api.onchange('date')
    def _onchange_date(self):
        if self.date and self.district_id and self.vehicle_id and self.delivery_type == 'transfer' and not self.env.user.has_group('delivery_module.group_delivery_manager'):
            day_of_week = str(self.date.weekday())
            day_names = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
            selected_day_name = day_names[self.date.weekday()]
            available_day = self.env['delivery.day'].search([
                ('day_of_week', '=', day_of_week),
                ('active', '=', True),
                ('district_ids', 'in', self.district_id.id)
            ], limit=1)
            if not available_day:
                return {
                    'warning': {
                        'title': 'Uygun Olmayan Tarih',
                        'message': f'Seçilen tarih ({self.date.strftime("%d/%m/%Y")} - {selected_day_name}) bu ilçe için uygun bir teslimat günü değil.'
                    }
                }
            today_count = self.env['delivery.document'].search_count([
                ('vehicle_id', '=', self.vehicle_id.id),
                ('date', '=', self.date),
                ('state', 'in', ['draft', 'ready'])
            ])
            if today_count >= self.vehicle_id.daily_limit:
                return {
                    'warning': {
                        'title': 'Kapasite Dolu',
                        'message': f'{self.vehicle_id.name} aracının bu tarihteki kapasitesi ({self.vehicle_id.daily_limit}) dolmuş.'
                    }
                }

    def action_create_delivery(self):
        if self.delivery_type == 'transfer':
            if not self.picking_name:
                raise UserError(_('Lütfen transfer numarası girin.'))
            picking_name_clean = self.picking_name.strip()
            picking = self.env['stock.picking'].search([
                ('name', '=', picking_name_clean),
                ('state', 'in', ['confirmed', 'assigned', 'done'])
            ], limit=1)
            if not picking:
                raise UserError(_(f'"{picking_name_clean}" numaralı transfer bulunamadı veya uygun durumda değil. Lütfen transfer numarasını kontrol edin.'))
            existing_delivery = self.env['delivery.document'].search([
                ('picking_ids', 'in', picking.id)
            ], limit=1)
            if existing_delivery:
                raise UserError(_(f'Bu transfer zaten "{existing_delivery.name}" teslimat belgesine atanmış.'))
            partner_id = picking.partner_id.id
            delivery_address = picking.partner_id.street or ""
            picking_ids = [(4, picking.id)]
        else:
            if not self.manual_task:
                raise UserError(_('Lütfen yapılacak işi açıklayın.'))
            partner_id = self.manual_partner_id.id if self.manual_partner_id else False
            delivery_address = ""
            picking_ids = []

        if not self.district_id:
            raise UserError(_('Lütfen ilçe seçin.'))
        if not self.vehicle_id:
            raise UserError(_('Lütfen araç seçin.'))

        if self.delivery_type == 'transfer' and not self.env.user.has_group('delivery_module.group_delivery_manager'):
            day_of_week = str(self.date.weekday())
            day_names = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
            selected_day_name = day_names[self.date.weekday()]
            available_day = self.env['delivery.day'].search([
                ('day_of_week', '=', day_of_week),
                ('active', '=', True),
                ('district_ids', 'in', self.district_id.id)
            ], limit=1)
            if not available_day:
                raise UserError(_(f'Seçilen tarih ({self.date.strftime("%d/%m/%Y")} - {selected_day_name}) bu ilçe için uygun bir teslimat günü değil.'))
            if self.district_id not in available_day.district_ids:
                raise UserError(_(f'"{self.district_id.name}" ilçesi {selected_day_name} gününde teslimat yapılamaz. Uygun günler: {", ".join([d.name for d in available_day.district_ids])}'))

        today_count = self.env['delivery.document'].search_count([
            ('vehicle_id', '=', self.vehicle_id.id),
            ('date', '=', self.date),
            ('state', 'in', ['draft', 'ready'])
        ])
        if today_count >= self.vehicle_id.daily_limit:
            if not self.env.user.has_group('delivery_module.group_delivery_manager'):
                raise UserError(_(f'{self.vehicle_id.name} aracının günlük limiti ({self.vehicle_id.daily_limit}) dolmuş. İlave teslimat için yetkilendirme gerekli.'))
            else:
                print(f"Teslimat yöneticisi limit aşımında teslimat oluşturuyor: {self.vehicle_id.name} - {today_count}/{self.vehicle_id.daily_limit}")

        day_of_week = str(self.date.weekday())
        delivery_day = self.env['delivery.day'].search([
            ('day_of_week', '=', day_of_week),
            ('active', '=', True)
        ], limit=1)
        if self.delivery_type == 'transfer' and not delivery_day:
            raise UserError(_('Seçilen tarih için teslimat günü bulunamadı.'))
        delivery_day_id = delivery_day.id if delivery_day else False

        delivery = self.env['delivery.document'].create({
            'date': self.date,
            'vehicle_id': self.vehicle_id.id,
            'partner_id': partner_id,
            'district_id': self.district_id.id,
            'delivery_day_id': delivery_day_id,
            'picking_ids': picking_ids,
            'note': self.note,
            'manual_task': self.manual_task if self.delivery_type == 'manual' else False,
            'state': 'ready',
        })

        return {
            'name': _('Teslimat Belgesi'),
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.document',
            'view_mode': 'form',
            'res_id': delivery.id,
        }
