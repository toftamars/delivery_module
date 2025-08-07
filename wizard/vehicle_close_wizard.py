from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DeliveryVehicleCloseWizard(models.TransientModel):
    _name = 'delivery.vehicle.close.wizard'
    _description = 'Araç Geçici Kapatma Wizard'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Araç', required=True)
    closed_reason = fields.Text('Kapatma Nedeni', required=True)
    
    def action_close_vehicle(self):
        """Aracı geçici olarak kapatır"""
        if not self.env.user.has_group('base.group_system'):
            raise ValidationError(_('Bu işlem için yönetici yetkisi gereklidir.'))
        
        self.vehicle_id.write({
            'is_temporarily_closed': True,
            'closed_reason': self.closed_reason,
            'closed_by': self.env.user.id,
            'closed_date': fields.Datetime.now()
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Başarılı'),
                'message': _('Araç geçici olarak kapatıldı.'),
                'type': 'success',
            }
        }
