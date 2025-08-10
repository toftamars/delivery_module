from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DeliveryRouteInfoWizard(models.TransientModel):
    _name = 'delivery.route.info.wizard'
    _description = 'Teslimat Rota Bilgileri Sihirbazı'

    delivery_id = fields.Many2one('delivery.document', string='Teslimat Belgesi', required=True)
    route_info = fields.Text('Rota Bilgisi', required=True, help='Rota detayları ve notlar')
    traffic_info = fields.Selection([
        ('normal', 'Normal'),
        ('heavy', 'Yoğun Trafik'),
        ('congested', 'Tıkanık'),
        ('clear', 'Açık')
    ], string='Trafik Durumu', default='normal', help='Mevcut trafik durumu')
    weather_info = fields.Selection([
        ('clear', 'Açık'),
        ('rainy', 'Yağmurlu'),
        ('snowy', 'Karlı'),
        ('foggy', 'Sisli'),
        ('stormy', 'Fırtınalı')
    ], string='Hava Durumu', default='clear', help='Mevcut hava durumu')
    note = fields.Text('Ek Notlar', help='Rota hakkında ek bilgiler')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('default_delivery_id'):
            delivery = self.env['delivery.document'].browse(self.env.context.get('default_delivery_id'))
            res.update({
                'delivery_id': delivery.id,
                'route_info': delivery.route_info or '',
            })
        return res

    def action_save_route_info(self):
        """Rota bilgilerini kaydet"""
        self.ensure_one()
        
        if not self.route_info:
            raise UserError(_('Rota bilgisi gereklidir.'))
        
        # Teslimat belgesini güncelle
        self.delivery_id.write({
            'route_info': self.route_info,
        })
        
        # Not ekle
        message_body = f"<strong>Rota Bilgileri Güncellendi:</strong><br/>"
        message_body += f"Rota: {self.route_info}<br/>"
        message_body += f"Trafik: {dict(self._fields['traffic_info'].selection).get(self.traffic_info)}<br/>"
        message_body += f"Hava: {dict(self._fields['weather_info'].selection).get(self.weather_info)}<br/>"
        
        if self.note:
            message_body += f"Not: {self.note}"
        
        self.delivery_id.message_post(body=message_body)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Başarılı'),
                'message': _('Rota bilgileri güncellendi.'),
                'type': 'success',
            }
        }
