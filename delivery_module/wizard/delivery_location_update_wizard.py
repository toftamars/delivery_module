from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DeliveryLocationUpdateWizard(models.TransientModel):
    _name = 'delivery.location.update.wizard'
    _description = 'Teslimat Konum Güncelleme Sihirbazı'

    delivery_id = fields.Many2one('delivery.document', string='Teslimat Belgesi', required=True)
    current_location = fields.Char('Mevcut Konum', required=True, help='Sürücünün mevcut konumu')
    estimated_arrival = fields.Datetime('Tahmini Varış', help='Tahmini varış zamanı')
    note = fields.Text('Not', help='Konum güncellemesi hakkında ek notlar')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('default_delivery_id'):
            delivery = self.env['delivery.document'].browse(self.env.context.get('default_delivery_id'))
            res.update({
                'delivery_id': delivery.id,
                'current_location': delivery.current_location or '',
                'estimated_arrival': delivery.estimated_arrival or False,
            })
        return res

    def action_update_location(self):
        """Konum bilgilerini güncelle"""
        self.ensure_one()
        
        if not self.current_location:
            raise UserError(_('Mevcut konum bilgisi gereklidir.'))
        
        # Teslimat belgesini güncelle
        self.delivery_id.write({
            'current_location': self.current_location,
            'estimated_arrival': self.estimated_arrival,
        })
        
        # Not ekle
        if self.note:
            self.delivery_id.message_post(
                body=f"<strong>Konum Güncellendi:</strong><br/>"
                     f"Mevcut Konum: {self.current_location}<br/>"
                     f"Tahmini Varış: {self.estimated_arrival or 'Belirtilmedi'}<br/>"
                     f"Not: {self.note}"
            )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Başarılı'),
                'message': _('Konum bilgileri güncellendi.'),
                'type': 'success',
            }
        }
