from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DeliveryPhotoWizard(models.TransientModel):
    _name = 'delivery.photo.wizard'
    _description = 'Teslimat Fotoğrafı Wizard'

    delivery_document_id = fields.Many2one('delivery.document', string='Teslimat Belgesi', required=True)
    photo = fields.Binary('Fotoğraf', required=True)
    photo_filename = fields.Char('Fotoğraf Dosya Adı')
    description = fields.Text('Açıklama')
    
    @api.constrains('photo')
    def _check_photo(self):
        for record in self:
            if not record.photo:
                raise ValidationError(_('Fotoğraf alanı zorunludur.'))
    
    def action_create_photo(self):
        """Fotoğraf oluştur"""
        self.ensure_one()
        
        # Fotoğraf kaydını oluştur
        photo_vals = {
            'name': f"Fotoğraf - {fields.Datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'delivery_document_id': self.delivery_document_id.id,
            'photo': self.photo,
            'photo_filename': self.photo_filename,
            'description': self.description,
        }
        
        photo = self.env['delivery.photo'].create(photo_vals)
        
        # Teslimat belgesine fotoğraf eklendi mesajı
        self.delivery_document_id.message_post(
            body=_('Fotoğraf eklendi: %s') % photo.name,
            subject=_('Fotoğraf Eklendi')
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Başarılı'),
                'message': _('Fotoğraf başarıyla eklendi.'),
                'type': 'success',
            }
        }
