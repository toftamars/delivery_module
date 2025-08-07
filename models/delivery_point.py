from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DeliveryPoint(models.Model):
    _name = 'delivery.point'
    _description = 'Teslimat Noktası'
    _order = 'sequence, id'

    name = fields.Char('Nokta Adı', required=True)
    sequence = fields.Integer('Sıra', default=10)
    planning_id = fields.Many2one('delivery.planning', 'Teslimat Planı', required=True, ondelete='cascade')
    
    partner_id = fields.Many2one('res.partner', 'Müşteri', required=True)
    district = fields.Char('İlçe', required=True)
    address = fields.Text('Adres', required=True)
    region_id = fields.Many2one('delivery.region', 'Bölge', compute='_compute_region', store=True)
    phone = fields.Char('Telefon')
    email = fields.Char('E-posta')
    
    latitude = fields.Float('Enlem')
    longitude = fields.Float('Boylam')
    
    distance_from_previous = fields.Float('Önceki Noktadan Mesafe (km)')
    estimated_time = fields.Float('Tahmini Süre (dakika)')
    
    state = fields.Selection([
        ('pending', 'Bekliyor'),
        ('in_progress', 'Devam Ediyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız')
    ], string='Durum', default='pending')
    
    delivery_time = fields.Datetime('Teslimat Zamanı')
    notes = fields.Text('Notlar')
    
    # Teslimat detayları
    package_count = fields.Integer('Paket Sayısı', default=1)
    weight = fields.Float('Ağırlık (kg)')
    special_instructions = fields.Text('Özel Talimatlar')
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.address = self.partner_id.street
            self.phone = self.partner_id.phone
            self.email = self.partner_id.email
    
    @api.depends('district')
    def _compute_region(self):
        """İlçeye göre bölgeyi otomatik belirler"""
        for record in self:
            if record.district:
                region = self.env['delivery.region'].search([
                    ('name', 'ilike', record.district)
                ], limit=1)
                record.region_id = region.id if region else False
    
    def action_start_delivery(self):
        self.state = 'in_progress'
        self.delivery_time = fields.Datetime.now()
    
    def action_complete_delivery(self):
        self.state = 'completed'
    
    def action_fail_delivery(self):
        self.state = 'failed'
    
    def action_reset_pending(self):
        self.state = 'pending'
