from odoo import models, fields, api

class CancelConfirmationWizard(models.TransientModel):
    _name = 'cancel.confirmation.wizard'
    _description = 'İptal Onay Sihirbazı'

    delivery_id = fields.Many2one('delivery.document', string='Teslimat Belgesi', required=True)
    message = fields.Text(string='Mesaj', default='Bu teslimat iptal edilecektir. Emin misiniz?')

    def action_confirm_cancel(self):
        self.ensure_one()
        self.delivery_id.write({'state': 'cancel'})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'İptal Edildi',
                'message': f'{self.delivery_id.name} numaralı teslimat iptal edildi.',
                'type': 'warning',
            }
        }
