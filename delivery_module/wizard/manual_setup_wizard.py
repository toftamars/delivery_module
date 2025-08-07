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

    def action_create_vehicles(self):
        """Araçları manuel olarak oluştur"""
        try:
            # Mevcut araçları kontrol et
            existing_vehicles = self.env['delivery.vehicle'].search([])
            if len(existing_vehicles) >= 5:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Bilgi'),
                        'message': _('Araçlar zaten mevcut.'),
                        'type': 'info',
                    }
                }
            
            # Araçları oluştur
            vehicles_data = [
                {'name': 'Anadolu Yakası', 'vehicle_type': 'anadolu', 'daily_limit': 7},
                {'name': 'Avrupa Yakası', 'vehicle_type': 'avrupa', 'daily_limit': 7},
                {'name': 'Küçük Araç 1', 'vehicle_type': 'kucuk_arac_1', 'daily_limit': 7},
                {'name': 'Küçük Araç 2', 'vehicle_type': 'kucuk_arac_2', 'daily_limit': 7},
                {'name': 'Ek Araç', 'vehicle_type': 'ek_arac', 'daily_limit': 7},
            ]
            
            created_vehicles = []
            for vehicle_data in vehicles_data:
                # Araç zaten var mı kontrol et
                existing = self.env['delivery.vehicle'].search([('name', '=', vehicle_data['name'])], limit=1)
                if not existing:
                    vehicle = self.env['delivery.vehicle'].create(vehicle_data)
                    created_vehicles.append(vehicle.name)
                    print(f"Araç oluşturuldu: {vehicle.name}")
                else:
                    print(f"Araç zaten mevcut: {existing.name}")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Başarılı'),
                    'message': _('Araçlar başarıyla oluşturuldu!'),
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_(f'Araçlar oluşturulurken hata oluştu: {str(e)}'))
