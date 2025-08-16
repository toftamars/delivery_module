from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_ids = fields.Many2many('delivery.document', string='Teslimat Belgeleri')
    delivery_count = fields.Integer(compute='_compute_delivery_count', string='Teslimat Sayısı')

    def _compute_delivery_count(self):
        for picking in self:
            picking.delivery_count = len(picking.delivery_ids)

    def action_view_deliveries(self):
        return {
            'name': 'Teslimatlar',
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.document',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.delivery_ids.ids)],
            'context': {'default_partner_id': self.partner_id.id},
        } 