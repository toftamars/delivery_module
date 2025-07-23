from odoo import models, fields, api

class CapacityControlWizard(models.TransientModel):
    _name = 'capacity.control.wizard'
    _description = 'Kapasite Kontrol Sihirbazı'

    date = fields.Date(string='Tarih', required=True, default=fields.Date.context_today)
    vehicle_id = fields.Many2one('delivery.vehicle', string='Araç', required=True)
    result = fields.Text(string='Kapasite Sonucu', readonly=True)

    def action_query_capacity(self):
        self.ensure_one()
        deliveries = self.env['delivery.document'].search([
            ('vehicle_id', '=', self.vehicle_id.id),
            ('date', '=', self.date),
            ('state', '!=', 'cancel')
        ])
        used = len(deliveries)
        total = self.vehicle_id.daily_limit
        remaining = total - used
        self.result = f"Toplam Kapasite: {total}\nKullanılan: {used}\nKalan: {remaining}"
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'capacity.control.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
