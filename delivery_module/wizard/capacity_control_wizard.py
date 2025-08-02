from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CapacityControlWizard(models.TransientModel):
    _name = 'capacity.control.wizard'
    _description = 'Kapasite Kontrol Sihirbazı'

    date = fields.Date(string='Tarih', required=True, default=fields.Date.context_today)
    vehicle_id = fields.Many2one('delivery.vehicle', string='Araç', required=True)
    result = fields.Text(string='Kapasite Sonucu', readonly=True)
    
    @api.onchange('date')
    def _onchange_date(self):
        """Tarih değiştiğinde araç seçimini temizle"""
        if self.date:
            self.vehicle_id = False
            self.result = False

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        """Araç değiştiğinde sonucu temizle"""
        if self.vehicle_id:
            self.result = False

    def action_query_capacity(self):
        """Kapasite sorgulaması yapar"""
        self.ensure_one()
        
        if not self.date or not self.vehicle_id:
            raise UserError(_('Lütfen tarih ve araç seçin.'))
        
        # Seçilen tarih için teslimat günü kontrolü
        day_of_week = str(self.date.weekday())
        delivery_day = self.env['delivery.day'].search([
            ('day_of_week', '=', day_of_week),
            ('active', '=', True),
            ('is_temporarily_closed', '=', False)
        ], limit=1)
        
        if not delivery_day:
            self.result = f"❌ {self.date.strftime('%d/%m/%Y')} tarihi için teslimat günü tanımlanmamış."
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'capacity.control.wizard',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new',
            }
        
        # Araç kapasitesini hesapla
        deliveries = self.env['delivery.document'].search([
            ('vehicle_id', '=', self.vehicle_id.id),
            ('date', '=', self.date),
            ('state', '!=', 'cancel')
        ])
        
        used = len(deliveries)
        total = self.vehicle_id.daily_limit
        remaining = total - used
        
        # Sonuç formatını geliştir
        status_icon = "✅" if remaining > 0 else "❌"
        status_text = "Müsait" if remaining > 0 else "Dolu"
        
        result_text = f"""
📅 Tarih: {self.date.strftime('%d/%m/%Y')}
🚚 Araç: {self.vehicle_id.name}
{status_icon} Durum: {status_text}

📊 Kapasite Bilgileri:
   • Toplam Kapasite: {total}
   • Kullanılan: {used}
   • Kalan: {remaining}

📋 Mevcut Teslimatlar:
"""
        
        if deliveries:
            for delivery in deliveries:
                result_text += f"   • {delivery.name} - {delivery.partner_id.name} - {delivery.state}\n"
        else:
            result_text += "   • Henüz teslimat yok\n"
        
        self.result = result_text
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'capacity.control.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
