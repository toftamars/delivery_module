from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DeliveryVehicle(models.Model):
    _name = 'delivery.vehicle'
    _description = 'Teslimat Aracı'
    _order = 'name'

    name = fields.Char('Araç Adı', required=True)
    vehicle_type = fields.Selection([
        ('anadolu', 'Anadolu Yakası'),
        ('avrupa', 'Avrupa Yakası'),
        ('kucuk_arac_1', 'Küçük Araç 1'),
        ('kucuk_arac_2', 'Küçük Araç 2'),
        ('ek_arac', 'Ek Araç'),
    ], string='Araç Tipi', required=True)
    
    daily_limit = fields.Integer('Günlük Teslimat Limiti', default=7, required=True)
    active = fields.Boolean('Aktif', default=True)
    
    # Geçici kapatma özelliği
    is_temporarily_closed = fields.Boolean('Geçici Olarak Kapalı', default=False)
    closure_reason = fields.Text('Kapatma Sebebi')
    closure_start_date = fields.Date('Kapatma Başlangıç Tarihi')
    closure_end_date = fields.Date('Kapatma Bitiş Tarihi')
    closed_by = fields.Many2one('res.users', string='Kapatan Kullanıcı', readonly=True)
    closed_date = fields.Datetime('Kapatma Tarihi', readonly=True)
    
    # Bugünkü teslimat sayısını hesapla
    today_delivery_count = fields.Integer('Bugünkü Teslimat Sayısı', compute='_compute_today_delivery_count')
    remaining_capacity = fields.Integer('Kalan Kapasite', compute='_compute_remaining_capacity')

    @api.depends('daily_limit')
    def _compute_today_delivery_count(self):
        for vehicle in self:
            today = fields.Date.today()
            count = self.env['delivery.document'].search_count([
                ('vehicle_id', '=', vehicle.id),
                ('date', '=', today),
                ('state', 'in', ['draft', 'ready'])
            ])
            vehicle.today_delivery_count = count

    @api.depends('daily_limit', 'today_delivery_count')
    def _compute_remaining_capacity(self):
        for vehicle in self:
            vehicle.remaining_capacity = vehicle.daily_limit - vehicle.today_delivery_count

    def action_view_today_deliveries(self):
        today = fields.Date.today()
        return {
            'name': f'{self.name} - Bugünkü Teslimatlar',
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.document',
            'view_mode': 'tree,form',
            'domain': [
                ('vehicle_id', '=', self.id),
                ('date', '=', today),
                ('state', 'in', ['draft', 'ready'])
            ],
            'context': {'default_vehicle_id': self.id, 'default_date': today},
        }

    def action_temporarily_close(self):
        """Geçici kapatma işlemi"""
        return {
            'name': _('Teslimat Aracını Geçici Kapat'),
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.vehicle.closure.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_vehicle_id': self.id},
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
                'message': _('%s aracı tekrar aktif hale getirildi.') % self.name,
                'type': 'success',
            }
        } 