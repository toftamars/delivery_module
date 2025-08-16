from odoo import models, fields, api

class ResCityDistrict(models.Model):
    _name = 'res.city.district'
    _description = 'İlçe'
    _order = 'name'

    name = fields.Char('İlçe Adı', required=True)
    city_id = fields.Many2one('res.city', string='İl', required=True)
    state_id = fields.Many2one('res.country.state', string='Eyalet/İl', related='city_id.state_id', readonly=True)
    country_id = fields.Many2one('res.country', string='Ülke', related='city_id.country_id', readonly=True)
    active = fields.Boolean('Aktif', default=True)
    
    # Teslimat günleri ilişkisi
    delivery_day_ids = fields.Many2many('delivery.day', string='Teslimat Günleri')
    delivery_day_count = fields.Integer('Teslimat Günü Sayısı', compute='_compute_delivery_day_count')
    delivery_day_list = fields.Text('Teslimat Günleri', compute='_compute_delivery_day_list', readonly=True)

    def _compute_delivery_day_count(self):
        for district in self:
            district.delivery_day_count = len(district.delivery_day_ids)

    def _compute_delivery_day_list(self):
        for district in self:
            if district.delivery_day_ids:
                day_names = []
                for day in district.delivery_day_ids.sorted('sequence'):
                    day_names.append(day.name)
                district.delivery_day_list = ", ".join(day_names)
            else:
                district.delivery_day_list = "Teslimat günü tanımlanmamış"

    @api.onchange('delivery_day_ids')
    def _onchange_delivery_day_ids(self):
        """Teslimat günleri değiştiğinde ilgili teslimat günlerini güncelle"""
        if self.delivery_day_ids:
            # Seçilen teslimat günlerini güncelle
            for day in self.delivery_day_ids:
                if self.id not in day.district_ids.ids:
                    day.district_ids = [(4, self.id)]
            
            # Kaldırılan teslimat günlerini güncelle
            all_days = self.env['delivery.day'].search([])
            for day in all_days:
                if day.id not in self.delivery_day_ids.ids and self.id in day.district_ids.ids:
                    day.district_ids = [(3, self.id)]

    def action_view_delivery_days(self):
        return {
            'name': f'{self.name} - Teslimat Günleri',
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.day',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.delivery_day_ids.ids)],
            'context': {'default_district_ids': [(4, self.id)]},
        } 