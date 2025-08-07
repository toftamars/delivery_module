from odoo import models, fields, api, _


class DeliveryVehicle(models.Model):
    _name = 'delivery.vehicle'
    _description = 'Teslimat Aracı'
    
    # Araç tipi ve bölge ataması
    vehicle_type = fields.Selection([
        ('anadolu', 'Anadolu Yakası'),
        ('avrupa', 'Avrupa Yakası'),
        ('kucuk_arac_1', 'Küçük Araç 1'),
        ('kucuk_arac_2', 'Küçük Araç 2'),
        ('ek_arac', 'Ek Araç')
    ], string='Araç Tipi', required=True)
    
    assigned_continent = fields.Selection([
        ('anadolu', 'Anadolu'),
        ('avrupa', 'Avrupa'),
        ('both', 'Her İkisi')
    ], string='Atanan Kıta', default='both')
    
    # Kapasite yönetimi
    daily_delivery_limit = fields.Integer('Günlük Teslimat Limiti', default=7)
    current_daily_deliveries = fields.Integer('Bugünkü Teslimat Sayısı', default=0)
    remaining_capacity = fields.Integer('Kalan Kapasite', compute='_compute_remaining_capacity')
    
    # Durum yönetimi
    is_available = fields.Boolean('Müsait', default=True)
    is_temporarily_closed = fields.Boolean('Geçici Kapatma', default=False)
    closed_reason = fields.Text('Kapatma Nedeni')
    closed_by = fields.Many2one('res.users', 'Kapatan Kullanıcı')
    closed_date = fields.Datetime('Kapatma Tarihi')
    
    # Fiziksel özellikler
    delivery_capacity = fields.Float('Teslimat Kapasitesi (kg)')
    fuel_type = fields.Selection([
        ('gasoline', 'Benzin'),
        ('diesel', 'Dizel'),
        ('electric', 'Elektrik'),
        ('hybrid', 'Hibrit')
    ], string='Yakıt Tipi')
    
    current_location = fields.Char('Mevcut Konum')
    
    # Teslimat istatistikleri
    total_deliveries = fields.Integer('Toplam Teslimat', compute='_compute_delivery_stats')
    total_distance = fields.Float('Toplam Mesafe (km)', compute='_compute_delivery_stats')
    average_delivery_time = fields.Float('Ortalama Teslimat Süresi (saat)', compute='_compute_delivery_stats')
    
    @api.depends('delivery_planning_ids')
    def _compute_delivery_stats(self):
        for vehicle in self:
            deliveries = self.env['delivery.planning'].search([
                ('vehicle_id', '=', vehicle.id),
                ('state', '=', 'completed')
            ])
            
            vehicle.total_deliveries = len(deliveries)
            vehicle.total_distance = sum(deliveries.mapped('total_distance'))
            vehicle.average_delivery_time = sum(deliveries.mapped('estimated_duration')) / len(deliveries) if deliveries else 0.0
    
    @api.depends('daily_delivery_limit', 'current_daily_deliveries')
    def _compute_remaining_capacity(self):
        for vehicle in self:
            vehicle.remaining_capacity = vehicle.daily_delivery_limit - vehicle.current_daily_deliveries
    
    def action_mark_available(self):
        self.is_available = True
    
    def action_mark_unavailable(self):
        self.is_available = False
    
    def action_temporarily_close(self):
        """Aracı geçici olarak kapatır (sadece yöneticiler)"""
        if not self.env.user.has_group('base.group_system'):
            raise ValidationError(_('Bu işlem için yönetici yetkisi gereklidir.'))
        
        return {
            'name': _('Araç Geçici Kapatma'),
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.vehicle.close.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_vehicle_id': self.id}
        }
    
    def action_reopen_vehicle(self):
        """Aracı tekrar açar (sadece yöneticiler)"""
        if not self.env.user.has_group('base.group_system'):
            raise ValidationError(_('Bu işlem için yönetici yetkisi gereklidir.'))
        
        self.is_temporarily_closed = False
        self.closed_reason = False
        self.closed_by = False
        self.closed_date = False
    
    def reset_daily_deliveries(self):
        """Günlük teslimat sayısını sıfırlar (cron job için)"""
        self.current_daily_deliveries = 0
    
    def can_assign_to_region(self, continent):
        """Aracın belirtilen bölgeye atanabilir olup olmadığını kontrol eder"""
        if self.assigned_continent == 'both':
            return True
        return self.assigned_continent == continent
