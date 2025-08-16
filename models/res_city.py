from odoo import models, fields

class ResCity(models.Model):
    _name = 'res.city'
    _description = 'İl'
    _order = 'name'

    name = fields.Char('İl Adı', required=True)
    state_id = fields.Many2one('res.country.state', string='Eyalet/İl')
    country_id = fields.Many2one('res.country', string='Ülke', related='state_id.country_id', readonly=True)
    active = fields.Boolean('Aktif', default=True)
    
    # İlçe ilişkisi
    district_ids = fields.One2many('res.city.district', 'city_id', string='İlçeler')
    district_count = fields.Integer('İlçe Sayısı', compute='_compute_district_count')

    def _compute_district_count(self):
        for city in self:
            city.district_count = len(city.district_ids)

    def action_view_districts(self):
        return {
            'name': f'{self.name} - İlçeler',
            'type': 'ir.actions.act_window',
            'res_model': 'res.city.district',
            'view_mode': 'tree,form',
            'domain': [('city_id', '=', self.id)],
            'context': {'default_city_id': self.id},
        } 