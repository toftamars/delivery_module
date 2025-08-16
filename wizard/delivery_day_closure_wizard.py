# Odoo import'ları sadece Odoo ortamında çalışır
# Odoo import'ları sadece Odoo ortamında çalışır
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DeliveryDayClosureWizard(models.TransientModel):
    _name = 'delivery.day.closure.wizard'
    _description = 'Teslimat Günü Geçici Kapatma Sihirbazı'

    delivery_day_id = fields.Many2one('delivery.day', string='Teslimat Günü', required=True, readonly=True)
    closure_reason = fields.Text('Kapatma Sebebi', required=True, 
                                placeholder='Örn: Araç bakımı, Resmi tatil, Hava durumu...')
    closure_start_date = fields.Date('Kapatma Başlangıç Tarihi', required=True, default=fields.Date.context_today)
    closure_end_date = fields.Date('Kapatma Bitiş Tarihi', required=True)
    is_permanent = fields.Boolean('Süresiz Kapatma', default=False, 
                                 help='Bu seçenek işaretlenirse tarih aralığı belirtilmez')
    
    @api.onchange('is_permanent')
    def _onchange_is_permanent(self):
        if self.is_permanent:
            self.closure_start_date = False
            self.closure_end_date = False
        else:
            self.closure_start_date = fields.Date.context_today

    @api.onchange('closure_start_date', 'closure_end_date')
    def _onchange_dates(self):
        if self.closure_start_date and self.closure_end_date:
            if self.closure_start_date > self.closure_end_date:
                return {
                    'warning': {
                        'title': 'Uyarı',
                        'message': 'Başlangıç tarihi bitiş tarihinden sonra olamaz.'
                    }
                }

    def action_confirm_closure(self):
        """Geçici kapatmayı onayla"""
        if not self.env.user.has_group('teslimat_planlama.group_delivery_manager'):
            raise UserError(_('Bu işlem için teslimat yöneticisi yetkisi gereklidir.'))
        
        if not self.is_permanent and (not self.closure_start_date or not self.closure_end_date):
            raise UserError(_('Tarih aralığı belirtilmelidir.'))
        
        # Geçici kapatma işlemi
        closure_data = {
            'is_temporarily_closed': True,
            'closure_reason': self.closure_reason,
            'closed_by': self.env.user.id,
            'closed_date': fields.Datetime.now(),
        }
        
        if not self.is_permanent:
            closure_data.update({
                'closure_start_date': self.closure_start_date,
                'closure_end_date': self.closure_end_date,
            })
        
        self.delivery_day_id.write(closure_data)
        
        # Bildirim mesajı
        if self.is_permanent:
            message = _('%s günü süresiz olarak kapatıldı.') % self.delivery_day_id.name
        else:
            message = _('%s günü %s - %s tarihleri arasında kapatıldı.') % (
                self.delivery_day_id.name,
                self.closure_start_date.strftime('%d/%m/%Y'),
                self.closure_end_date.strftime('%d/%m/%Y')
            )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Başarılı'),
                'message': message,
                'type': 'success',
            }
        }

    def action_cancel(self):
        """İptal et"""
        return {'type': 'ir.actions.act_window_close'} 