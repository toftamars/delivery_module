# Odoo import'ları sadece Odoo ortamında çalışır
# # # from odoo import models, fields, api, _
# from odoo.exceptions import UserError

class DeliveryLimitWarningWizard(models.TransientModel):
    _name = 'delivery.limit.warning.wizard'
    _description = 'Teslimat Limiti Uyarı Sihirbazı'

    vehicle_id = fields.Many2one('delivery.vehicle', string='Araç', readonly=True)
    date = fields.Date('Teslimat Tarihi', readonly=True)
    picking_id = fields.Many2one('stock.picking', string='Transfer', readonly=True)

    warning_message = fields.Text('Uyarı Mesajı', readonly=True)
    confirm_override = fields.Boolean('Limiti Aşmayı Onaylıyorum')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('default_vehicle_id'):
            vehicle = self.env['delivery.vehicle'].browse(self.env.context.get('default_vehicle_id'))
            today_count = self.env['delivery.document'].search_count([
                ('vehicle_id', '=', vehicle.id),
                ('date', '=', self.env.context.get('default_date')),
                ('state', 'in', ['draft', 'ready'])
            ])
            
            res['warning_message'] = f"""
            {vehicle.name} aracının günlük limiti ({vehicle.daily_limit}) dolmuş.
            Bugünkü teslimat sayısı: {today_count}
            
            Bu teslimatı eklemek için yetkilendirmeniz gerekiyor.
            Devam etmek istediğinizden emin misiniz?
            """
        return res

    def action_confirm_override(self):
        if not self.confirm_override:
            raise UserError(_('Limiti aşmayı onaylamanız gerekiyor.'))
        
        # Teslimat belgesini oluştur
        delivery = self.env['delivery.document'].create({
            'date': self.date,
            'vehicle_id': self.vehicle_id.id,
            'partner_id': self.picking_id.partner_id.id,

            'picking_ids': [(4, self.picking_id.id)],
        })

        return {
            'name': _('Teslimat Belgesi'),
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.document',
            'view_mode': 'form',
            'res_id': delivery.id,
        }

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'} 