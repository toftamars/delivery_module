from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DeliveryCreateWizard(models.TransientModel):
    _name = 'delivery.create.wizard'
    _description = 'Teslimat Oluşturma Sihirbazı'

    date = fields.Date('Teslimat Tarihi', required=True, default=fields.Date.context_today)
    vehicle_id = fields.Many2one('delivery.vehicle', string='Araç', required=True)
    picking_name = fields.Char('Transfer Numarası', required=True, help='Transfer numarasını girin (örn: WH/OUT/00001)')
    picking_id = fields.Many2one('stock.picking', string='Seçilen Transfer', readonly=True)
    district_id = fields.Many2one('res.city.district', string='İlçe', required=True)
    available_dates = fields.Text('Uygun Teslimat Günleri', readonly=True)
    vehicle_info = fields.Text('Araç Bilgileri', readonly=True)

    @api.onchange('picking_name')
    def _onchange_picking_name(self):
        if self.picking_name:
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
                days_text = ', '.join([day.name for day in delivery_days.sorted('sequence')])
                self.available_dates = f"Bu ilçede teslimat yapılabilecek günler: {days_text}"
            else:
                self.available_dates = "Bu ilçe için teslimat günü tanımlanmamış."
        else:
            self.available_dates = ''

    @api.onchange('vehicle_id', 'date')
    def _onchange_vehicle_date(self):
        if self.vehicle_id and self.date:
            # Aracın o günkü teslimat sayısını kontrol et
            today_count = self.env['delivery.document'].search_count([
                ('vehicle_id', '=', self.vehicle_id.id),
                ('date', '=', self.date),
                ('state', 'in', ['draft', 'ready'])
            ])
            
            remaining = self.vehicle_id.daily_limit - today_count
            self.vehicle_info = f"{self.vehicle_id.name} - Bugünkü teslimat: {today_count}/{self.vehicle_id.daily_limit} (Kalan: {remaining})"
            
            if today_count >= self.vehicle_id.daily_limit:
                return {
                    'warning': {
                        'title': 'Uyarı',
                        'message': f'{self.vehicle_id.name} aracının günlük limiti ({self.vehicle_id.daily_limit}) dolmuş. İlave teslimat için yetkilendirme gerekli.'
                    }
                }
        else:
            self.vehicle_info = ''

    @api.onchange('date')
    def _onchange_date(self):
        if self.date and self.district_id:
            # Seçilen tarihin uygun bir gün olup olmadığını kontrol et
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
        # Transfer numarasını tekrar kontrol et
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

        if not self.district_id:
            raise UserError(_('Lütfen ilçe seçin.'))

        if not self.vehicle_id:
            raise UserError(_('Lütfen araç seçin.'))

        # Aracın günlük limitini kontrol et
        today_count = self.env['delivery.document'].search_count([
            ('vehicle_id', '=', self.vehicle_id.id),
            ('date', '=', self.date),
            ('state', 'in', ['draft', 'ready'])
        ])
        
        if today_count >= self.vehicle_id.daily_limit:
            # Yetkilendirme kontrolü - sadece teslimat yöneticileri ilave teslimat ekleyebilir
            if not self.env.user.has_group('delivery_module.group_delivery_manager'):
                raise UserError(_(f'{self.vehicle_id.name} aracının günlük limiti ({self.vehicle_id.daily_limit}) dolmuş. İlave teslimat için yetkilendirme gerekli.'))
            else:
                # Yetkili kullanıcı için uyarı ver ama devam et
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Limit Aşıldı',
                    'res_model': 'delivery.limit.warning.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_vehicle_id': self.vehicle_id.id,
                        'default_date': self.date,
                        'default_picking_id': picking.id,
                        'default_district_id': self.district_id.id,
                    }
                }

        # Transfer zaten bir teslimat belgesine atanmış mı kontrol et
        existing_delivery = self.env['delivery.document'].search([
            ('picking_ids', 'in', picking.id)
        ], limit=1)
        
        if existing_delivery:
            raise UserError(_(f'Bu transfer zaten "{existing_delivery.name}" teslimat belgesine atanmış.'))

        delivery = self.env['delivery.document'].create({
            'date': self.date,
            'vehicle_id': self.vehicle_id.id,
            'partner_id': picking.partner_id.id,
            'district_id': self.district_id.id,
            'picking_ids': [(4, picking.id)],
        })

        return {
            'name': _('Teslimat Belgesi'),
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.document',
            'view_mode': 'form',
            'res_id': delivery.id,
        } 