from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    city_id = fields.Many2one('res.city', string='İl')
    is_driver = fields.Boolean('Sürücü mü?', default=False) 