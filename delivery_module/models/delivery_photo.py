from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DeliveryPhoto(models.Model):
    _name = 'delivery.photo'
    _description = 'Teslimat Fotoğrafı'
    _order = 'create_date desc'

    name = fields.Char('Ad', required=True)
    delivery_document_id = fields.Many2one('delivery.document', string='Teslimat Belgesi', required=True, ondelete='cascade')
    photo = fields.Binary('Fotoğraf', required=True)
    photo_filename = fields.Char('Fotoğraf Dosya Adı')
    description = fields.Text('Açıklama')
    create_date = fields.Datetime('Oluşturma Tarihi', default=fields.Datetime.now, readonly=True)
    create_uid = fields.Many2one('res.users', string='Oluşturan', readonly=True)
    
    # İlişkiler
    delivery_day_id = fields.Many2one('delivery.day', string='Teslimat Günü', related='delivery_document_id.delivery_day_id', store=True)
    delivery_vehicle_id = fields.Many2one('delivery.vehicle', string='Teslimat Aracı', related='delivery_document_id.vehicle_id', store=True)
    partner_id = fields.Many2one('res.partner', string='Müşteri', related='delivery_document_id.partner_id', store=True)
    
    @api.constrains('photo')
    def _check_photo(self):
        for record in self:
            if not record.photo:
                raise ValidationError(_('Fotoğraf alanı zorunludur.'))
    
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = f"Fotoğraf - {fields.Datetime.now().strftime('%Y-%m-%d %H:%M')}"
        return super().create(vals)

    def action_preview_photo(self):
        self.ensure_one()
        filename = self.photo_filename or 'photo.jpg'
        url = f"/web/content?model=delivery.photo&id={self.id}&field=photo&filename_field=photo_filename&filename={filename}"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def action_download_photo(self):
        self.ensure_one()
        filename = self.photo_filename or 'photo.jpg'
        url = f"/web/content?model=delivery.photo&id={self.id}&field=photo&filename_field=photo_filename&filename={filename}&download=true"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }
