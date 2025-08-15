from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SetupDeliveryScheduleWizard(models.TransientModel):
    _name = 'setup.delivery.schedule.wizard'
    _description = 'Teslimat Programı Kurulum Sihirbazı'

    def action_setup_schedule(self):
        """Teslimat programını manuel olarak ayarlar"""
        try:
            from ..data.setup_delivery_schedule import setup_delivery_schedule
            setup_delivery_schedule(self.env)
            
            # Teslimat yöneticisi grubunu oluştur veya güncelle
            self._setup_delivery_manager_group()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Başarılı'),
                    'message': _('Teslimat programı ve yönetici yetkileri başarıyla ayarlandı!'),
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_(f'Teslimat programı ayarlanırken hata oluştu: {str(e)}'))

    def _setup_delivery_manager_group(self):
        """Teslimat yöneticisi grubunu ve yetkilerini ayarlar"""
        # Teslimat yöneticisi grubunu bul veya oluştur
        delivery_manager_group = self.env.ref('delivery_module.group_delivery_manager', raise_if_not_found=False)
        
        if not delivery_manager_group:
            # Grup yoksa oluştur
            delivery_manager_group = self.env['res.groups'].create({
                'name': 'Teslimat Yöneticisi',
                'category_id': self.env.ref('base.module_category_hidden').id,
                'comment': 'Teslimat yöneticisi yetkileri - araç ve tarih kapatma izinleri',
            })
        
        # Gerekli yetkileri ekle
        self._add_delivery_manager_permissions(delivery_manager_group)
        
        print(f"Teslimat yöneticisi grubu ayarlandı: {delivery_manager_group.name}")
        
        # Kullanıcıya bilgi ver
        print(_('Teslimat Yöneticisi Yetkileri'))
        print(_('Teslimat yöneticisi grubu oluşturuldu. Kullanıcıları bu gruba atamak için:'))
        print(_('1. Ayarlar > Kullanıcılar ve Şirketler > Kullanıcılar'))
        print(_('2. İlgili kullanıcıyı seçin'))
        print(_('3. Erişim Hakları sekmesinde "Teslimat Yöneticisi" grubunu işaretleyin'))
        print(_('4. Kaydedin'))

    def _add_delivery_manager_permissions(self, group):
        """Teslimat yöneticisi grubuna gerekli yetkileri ekler"""
        # Araç yönetimi yetkileri
        vehicle_access = self.env['ir.model.access'].search([
            ('name', '=', 'delivery.vehicle.manager'),
            ('model_id.model', '=', 'delivery.vehicle')
        ], limit=1)
        
        if vehicle_access:
            vehicle_access.write({
                'group_id': group.id,
                'perm_read': True,
                'perm_write': True,
                'perm_create': True,
                'perm_unlink': True,
            })
        
        # Teslimat günü yönetimi yetkileri (kapatma dahil)
        day_access = self.env['ir.model.access'].search([
            ('name', '=', 'delivery.day.manager'),
            ('model_id.model', '=', 'delivery.day')
        ], limit=1)
        
        if day_access:
            day_access.write({
                'group_id': group.id,
                'perm_read': True,
                'perm_write': True,
                'perm_create': True,
                'perm_unlink': True,
            })
        
        # Teslimat belgesi yönetimi yetkileri
        document_access = self.env['ir.model.access'].search([
            ('name', '=', 'delivery.document.manager'),
            ('model_id.model', '=', 'delivery.document')
        ], limit=1)
        
        if document_access:
            document_access.write({
                'group_id': group.id,
                'perm_read': True,
                'perm_write': True,
                'perm_create': True,
                'perm_unlink': True,
            })
        
        # İl ve ilçe yönetimi yetkileri
        city_access = self.env['ir.model.access'].search([
            ('name', '=', 'res.city.manager'),
            ('model_id.model', '=', 'res.city')
        ], limit=1)
        
        if city_access:
            city_access.write({
                'group_id': group.id,
                'perm_read': True,
                'perm_write': True,
                'perm_create': True,
                'perm_unlink': True,
            })
        
        district_access = self.env['ir.model.access'].search([
            ('name', '=', 'res.city.district.manager'),
            ('model_id.model', '=', 'res.city.district')
        ], limit=1)
        
        if district_access:
            district_access.write({
                'group_id': group.id,
                'perm_read': True,
                'perm_write': True,
                'perm_create': True,
                'perm_unlink': True,
            })
        
        print(f"Teslimat yöneticisi yetkileri eklendi: Araç, Tarih, Belge, İl/İlçe yönetimi") 