# Odoo import'ları sadece Odoo ortamında çalışır
# # # from odoo import models, fields, api, _
# from odoo.exceptions import UserError

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
        ('done', 'Teslim Edildi'),
        ('cancel', 'İptal')
    ], string='Durum', default='draft', tracking=True)
    
    # Yeni alanlar
    partner_id = fields.Many2one('res.partner', string='Müşteri', required=True)

    delivery_address = fields.Char('Teslimat Adresi', related='partner_id.street', readonly=True)
    picking_ids = fields.Many2many('stock.picking', string='Transfer Belgeleri')
    picking_count = fields.Integer(compute='_compute_picking_count', string='Transfer Sayısı')

    def _compute_picking_count(self):
        for delivery in self:
            delivery.picking_count = len(delivery.picking_ids)

    def action_view_pickings(self):
        return {
            'name': _('Transfer Belgeleri'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.picking_ids.ids)],
            'context': {'default_partner_id': self.partner_id.id},
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
                if not self.env.user.has_group('teslimat_planlama.group_delivery_manager'):
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
        self._send_sms_notification('ready')

    def action_on_the_way(self):
        """Yolda butonu - Taslaktan Hazır durumuna geçer"""
        if self.state != 'draft':
            raise UserError(_('Sadece taslak durumundaki teslimatlar yola çıkabilir.'))
        
        self.write({'state': 'ready'})
        self._send_sms_notification('on_the_way')
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Başarılı'),
                'message': _('%s numaralı teslimat yola çıktı ve müşteriye SMS gönderildi.') % self.name,
                'type': 'success',
            }
        }

    def action_complete(self):
        self.write({'state': 'done'})
        self._send_sms_notification('done')

    def action_finish_delivery(self):
        """Tamamla butonu - Hazır durumundan Tamamlandı durumuna geçer"""
        if self.state != 'ready':
            raise UserError(_('Sadece hazır durumundaki teslimatlar tamamlanabilir.'))
        
        self.write({'state': 'done'})
        self._send_sms_notification('done')
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Başarılı'),
                'message': _('%s numaralı teslimat tamamlandı ve müşteriye SMS gönderildi.') % self.name,
                'type': 'success',
            }
        }

    def action_cancel(self):
        self.write({'state': 'cancel'})
        self._send_sms_notification('cancel')

    def action_draft(self):
        self.write({'state': 'draft'})

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
            'done': f'Sayın {self.partner_id.name}, {self.name} numaralı teslimatınız tamamlandı.',
            'cancel': f'Sayın {self.partner_id.name}, {self.name} numaralı teslimatınız iptal edildi.',
            'on_the_way': f'Sayın {self.partner_id.name}, {self.name} numaralı teslimatınız yola çıktı.'
        }
        return messages.get(state) 