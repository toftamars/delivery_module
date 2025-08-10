from odoo import models, fields, api, _
from odoo.exceptions import UserError
from urllib.parse import quote

class DeliveryDocument(models.Model):
    _name = 'delivery.document'
    _description = 'Teslimat Belgesi'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Teslimat Numarası', required=True, copy=False, readonly=True, default='New')
    date = fields.Date('Teslimat Tarihi', required=True, default=fields.Date.context_today)
    vehicle_id = fields.Many2one('delivery.vehicle', string='Araç', required=True)
    state = fields.Selection([
        ('draft', 'Taslak'),
        ('ready', 'Hazır'),
        ('on_the_way', 'Yolda'),
        ('done', 'Teslim Edildi'),
        ('cancel', 'İptal')
    ], string='Durum', default='draft', tracking=True)
    
    # Yeni alanlar
    partner_id = fields.Many2one('res.partner', string='Müşteri', required=True)
    delivery_day_id = fields.Many2one('delivery.day', string='Teslimat Günü', required=True)
    district_id = fields.Many2one('res.city.district', string='İlçe', required=True)

    delivery_address = fields.Char('Teslimat Adresi', compute='_compute_delivery_address', store=True, readonly=True)
    phone = fields.Char('Telefon', compute='_compute_phone', store=True, readonly=True)
    note = fields.Text('Not')
    manual_task = fields.Text('Yapılacak İş', help='Manuel teslimat için yapılacak iş açıklaması')

    # İlişkiler
    picking_ids = fields.Many2many('stock.picking', string='Transfer Belgeleri')
    picking_count = fields.Integer(compute='_compute_picking_count', string='Transfer Sayısı')

    photo_ids = fields.One2many('delivery.photo', 'delivery_document_id', string='Fotoğraflar')
    photo_count = fields.Integer(compute='_compute_photo_count', string='Fotoğraf Sayısı')
    
    # Harita ve rota desteği için alanlar (tutarlılık için korunuyor)
    is_on_the_way = fields.Boolean('Yolda', default=False, tracking=True)
    current_location = fields.Char('Mevcut Konum', help='Sürücünün mevcut konumu')
    estimated_arrival = fields.Datetime('Tahmini Varış', help='Tahmini varış zamanı')
    route_info = fields.Text('Rota Bilgisi', help='Rota detayları ve notlar')

    def _compute_picking_count(self):
        for delivery in self:
            delivery.picking_count = len(delivery.picking_ids)

    def _compute_photo_count(self):
        for delivery in self:
            delivery.photo_count = len(delivery.photo_ids)

    @api.depends('partner_id', 'partner_id.street', 'partner_id.street2', 'district_id', 'district_id.city_id')
    def _compute_delivery_address(self):
        for rec in self:
            parts = []
            if rec.partner_id and rec.partner_id.street:
                parts.append(rec.partner_id.street)
            if rec.partner_id and rec.partner_id.street2:
                parts.append(rec.partner_id.street2)
            if rec.district_id and rec.district_id.name:
                parts.append(rec.district_id.name)
            if rec.district_id and rec.district_id.city_id and rec.district_id.city_id.name:
                parts.append(rec.district_id.city_id.name)
            rec.delivery_address = ', '.join([p for p in parts if p])

    @api.depends('partner_id')
    def _compute_phone(self):
        for rec in self:
            phone = ''
            if rec.partner_id:
                phone = rec.partner_id.mobile or rec.partner_id.phone or ''
            rec.phone = phone

    def action_view_pickings(self):
        return {
            'name': _('Transfer Belgeleri'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.picking_ids.ids)],
            'context': {'default_partner_id': self.partner_id.id},
        }

    def action_view_photos(self):
        self.ensure_one()
        return {
            'name': _('Teslimat Fotoğrafları'),
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.photo',
            'view_mode': 'tree,form',
            'domain': [('delivery_document_id', '=', self.id)],
            'context': {'default_delivery_document_id': self.id},
        }

    def action_view_picking_count(self):
        """Transfer sayısına tıklandığında transferleri göster"""
        return self.action_view_pickings()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('delivery.document') or 'New'
        return super().create(vals_list)

    @api.onchange('vehicle_id', 'date')
    def _onchange_vehicle_date(self):
        if self.vehicle_id and self.date:
            # Aracın o günkü teslimat sayısını kontrol et
            today_count = self.env['delivery.document'].search_count([
                ('vehicle_id', '=', self.vehicle_id.id),
                ('date', '=', self.date),
                ('state', 'in', ['draft', 'ready']),
                ('id', '!=', self.id)
            ])
            
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

    def action_approve(self):
        self.write({'state': 'ready'})

    def action_on_the_way(self):
        """Yolda butonu - Hazır durumundan 'Yolda' durumuna geçer"""
        if self.state != 'ready':
            raise UserError(_('Sadece hazır durumundaki teslimatlar yola çıkabilir.'))
        
        self.write({
            'state': 'on_the_way',
            'is_on_the_way': True
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Başarılı'),
                'message': _('%s numaralı teslimat yola çıktı.') % self.name,
                'type': 'success',
            }
        }

    def action_complete(self):
        """Tamamla butonu - 'Yolda' durumundan Teslim Edildi durumuna geçer ve fotoğraf ekleme wizard'ını açar"""
        if self.state != 'on_the_way':
            raise UserError(_('Sadece yolda durumundaki teslimatlar tamamlanabilir.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Teslimat Fotoğrafı Ekle'),
            'res_model': 'delivery.photo.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_delivery_document_id': self.id,
            }
        }

    def action_finish_delivery(self):
        """Tamamla butonu - Hazır durumundan Teslim Edildi durumuna geçer"""
        if self.state != 'ready':
            raise UserError(_('Sadece hazır durumundaki teslimatlar tamamlanabilir.'))
        
        self.write({'state': 'done'})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Başarılı'),
                'message': _('%s numaralı teslimat TESLİM EDİLDİ.') % self.name,
                'type': 'success',
            }
        }

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_open_navigation(self):
        """Navigasyon butonu - Sadece 'Yolda' durumundaki teslimatlar için rota talimatlarını açar"""
        self.ensure_one()
        
        if self.state != 'on_the_way':
            raise UserError(_('Harita sadece yolda olan teslimatlar için açılabilir.'))
        
        address = self.delivery_address or (self.partner_id and self.partner_id.contact_address) or ''
        if not address:
            raise UserError(_('Navigasyon için adres bulunamadı.'))
        
        # Google Maps Directions (rota) URL'i oluştur
        url = f"https://www.google.com/maps/dir/?api=1&destination={quote(address)}"
        
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def action_update_location(self):
        """Mevcut konum güncelleme"""
        self.ensure_one()
        if self.state != 'on_the_way':
            raise UserError(_('Konum güncellemesi sadece yolda olan teslimatlar için yapılabilir.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Konum Güncelle'),
            'res_model': 'delivery.location.update.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_delivery_id': self.id,
                'default_current_location': self.current_location or '',
                'default_estimated_arrival': self.estimated_arrival or False,
            }
        }

    def action_view_route(self):
        """Rota bilgilerini görüntüleme"""
        self.ensure_one()
        if self.state != 'on_the_way':
            raise UserError(_('Rota bilgileri sadece yolda olan teslimatlar için görüntülenebilir.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Rota Bilgileri'),
            'res_model': 'delivery.route.info.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_delivery_id': self.id,
                'default_route_info': self.route_info or '',
            }
        }

    def _send_sms_notification(self, state):
        """SMS bildirimi gönder"""
        if not self.partner_id.mobile:
            return
        
        try:
            message = self._get_sms_message(state)
            if message:
                self.env['sms.api']._send_sms(
                    self.partner_id.mobile,
                    message
                )
        except Exception as e:
            # SMS gönderimi başarısız olsa bile teslimat işlemi devam etsin
            _logger = logging.getLogger(__name__)
            _logger.warning(f"SMS gönderilemedi: {e}")
            return

    def _get_sms_message(self, state):
        messages = {
            'ready': f'Sayın {self.partner_id.name}, {self.name} numaralı teslimatınız hazırlandı.',
            'done': f'Sayın {self.partner_id.name}, {self.name} numaralı teslimatınız teslim edildi.',
            'cancel': f'Sayın {self.partner_id.name}, {self.name} numaralı teslimatınız iptal edildi.',
            'on_the_way': f'Sayın {self.partner_id.name}, {self.name} numaralı teslimatınız yola çıktı.'
        }
        return messages.get(state) 