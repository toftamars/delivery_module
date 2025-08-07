from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ManualSetupWizard(models.TransientModel):
    _name = 'manual.setup.wizard'
    _description = 'Manuel Kurulum Wizard'

    def action_setup_delivery_schedule(self):
        """Teslimat programını manuel olarak ayarla"""
        try:
            from ..data.setup_delivery_schedule import setup_delivery_schedule
            setup_delivery_schedule(self.env)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Başarılı'),
                    'message': _('Teslimat programı başarıyla ayarlandı!'),
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_(f'Teslimat programı ayarlanırken hata oluştu: {str(e)}'))

    def action_check_data(self):
        """Mevcut verileri kontrol et"""
        try:
            # Teslimat günlerini kontrol et
            delivery_days = self.env['delivery.day'].search([])
            print(f"Teslimat günleri: {len(delivery_days)}")
            for day in delivery_days:
                print(f"- {day.name}: {len(day.district_ids)} ilçe")
            
            # İlçeleri kontrol et
            districts = self.env['res.city.district'].search([])
            print(f"İlçeler: {len(districts)}")
            for district in districts:
                print(f"- {district.name} ({district.city_id.name})")
            
            # Araçları kontrol et
            vehicles = self.env['delivery.vehicle'].search([])
            print(f"Araçlar: {len(vehicles)}")
            for vehicle in vehicles:
                print(f"- {vehicle.name} ({vehicle.vehicle_type})")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Bilgi'),
                    'message': _('Kontrol tamamlandı. Lütfen logları kontrol edin.'),
                    'type': 'info',
                }
            }
        except Exception as e:
            raise UserError(_(f'Kontrol sırasında hata oluştu: {str(e)}'))
