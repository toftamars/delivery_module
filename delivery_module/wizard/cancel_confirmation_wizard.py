from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CancelConfirmationWizard(models.TransientModel):
    _name = 'cancel.confirmation.wizard'
    _description = 'İptal Onay Wizard'

    delivery_document_id = fields.Many2one('delivery.document', string='Teslimat Belgesi', required=True)
    reason = fields.Text('İptal Sebebi', required=True)
    
    def action_confirm_cancel(self):
        """İptal işlemini onayla"""
        self.ensure_one()
        
        if not self.reason:
            raise UserError(_('İptal sebebi zorunludur.'))
        
        # Teslimat belgesini iptal et
        self.delivery_document_id.write({
            'state': 'cancel'
        })
        
        # İptal mesajı ekle
        self.delivery_document_id.message_post(
            body=_('Teslimat iptal edildi. Sebep: %s') % self.reason,
            subject=_('Teslimat İptal Edildi')
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Başarılı'),
                'message': _('Teslimat başarıyla iptal edildi.'),
                'type': 'success',
            }
        }
