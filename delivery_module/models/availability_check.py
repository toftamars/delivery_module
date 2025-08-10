from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import calendar
import json

class AvailabilityCheck(models.Model):
    _name = 'availability.check'
    _description = 'Uygunluk Kontrol'
    _order = 'id desc'
    _transient_max_hours = 1  # 1 saat sonra otomatik sil

    vehicle_id = fields.Many2one('delivery.vehicle', string='Araç', required=True)
    district_id = fields.Many2one('res.city.district', string='İlçe', required=False, help='Küçük araçlar için ilçe seçimi gerekmez')
    result_html = fields.Html(string='Sonuç', readonly=True)
    check_date = fields.Datetime(string='Sorgulama Tarihi', default=fields.Datetime.now, readonly=True)
    user_id = fields.Many2one('res.users', string='Sorgulayan', default=lambda self: self.env.user, readonly=True)
    result_json = fields.Text(string='Sonuç (JSON)', readonly=True)

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        """Araç değiştiğinde ilçe ve sonuç alanlarını temizle"""
        if self.vehicle_id:
            self.district_id = False
            self.result_html = False

    @api.onchange('district_id')
    def _onchange_district(self):
        """İlçe değiştiğinde sonuç alanını temizle"""
        if self.district_id:
            self.result_html = False

    def _compute_suitable_dates(self):
        """Önümüzdeki 30 gün için uygun tarihleri hesaplar ve liste döner"""
        self.ensure_one()
        suitable_dates = []
        # Küçük araçlar için ilçe kontrolü yapma
        small_vehicles = ['Küçük Araç 1', 'Küçük Araç 2', 'Ek araç', 'Ek Araç']
        is_small_vehicle = self.vehicle_id.name in small_vehicles
        # Yönetici, kısıtlamalardan muaf
        is_manager = self.env.user.has_group('delivery_module.group_delivery_manager')
        today = datetime.now().date()
        for i in range(30):
            check_date = today + timedelta(days=i)
            day_of_week = str(check_date.weekday())
            delivery_day = self.env['delivery.day'].search([
                ('day_of_week', '=', day_of_week),
                ('active', '=', True),
                ('is_temporarily_closed', '=', False)
            ], limit=1)
            if is_small_vehicle:
                deliveries = self.env['delivery.document'].search([
                    ('vehicle_id', '=', self.vehicle_id.id),
                    ('date', '=', check_date),
                    ('state', '!=', 'cancel')
                ])
                used_capacity = len(deliveries)
                total_capacity = self.vehicle_id.daily_limit
                remaining_capacity = max(total_capacity - used_capacity, 0)
                if remaining_capacity > 0 or is_manager:
                    suitable_dates.append({
                        'date': check_date.strftime('%Y-%m-%d'),
                        'day_name': calendar.day_name[check_date.weekday()],
                        'remaining': remaining_capacity,
                        'used': used_capacity,
                        'total': total_capacity,
                    })
            elif delivery_day:
                # İlçe seçildiyse, sadece o ilçede teslimat yapılan günleri göster
                if self.district_id:
                    if self.district_id in delivery_day.district_ids:
                        deliveries = self.env['delivery.document'].search([
                            ('vehicle_id', '=', self.vehicle_id.id),
                            ('date', '=', check_date),
                            ('state', '!=', 'cancel')
                        ])
                        used_capacity = len(deliveries)
                        total_capacity = self.vehicle_id.daily_limit
                        remaining_capacity = max(total_capacity - used_capacity, 0)
                        if remaining_capacity > 0 or is_manager:
                            suitable_dates.append({
                                'date': check_date.strftime('%Y-%m-%d'),
                                'day_name': calendar.day_name[check_date.weekday()],
                                'remaining': remaining_capacity,
                                'used': used_capacity,
                                'total': total_capacity,
                            })
                # İlçe seçilmediyse, tüm günleri göster (yönetici için)
                elif is_manager:
                    deliveries = self.env['delivery.document'].search([
                        ('vehicle_id', '=', self.vehicle_id.id),
                        ('date', '=', check_date),
                        ('state', '!=', 'cancel')
                    ])
                    used_capacity = len(deliveries)
                    total_capacity = self.vehicle_id.daily_limit
                    remaining_capacity = max(total_capacity - used_capacity, 0)
                    if remaining_capacity > 0 or is_manager:
                        suitable_dates.append({
                            'date': check_date.strftime('%Y-%m-%d'),
                            'day_name': calendar.day_name[check_date.weekday()],
                            'remaining': remaining_capacity,
                            'used': used_capacity,
                            'total': total_capacity,
                        })
        return suitable_dates

    def _get_suitable_dates(self):
        self.ensure_one()
        if self.result_json:
            try:
                return json.loads(self.result_json)
            except Exception:
                return []
        return []

    def action_check_availability(self):
        """Uygunluk kontrolü yap"""
        self.ensure_one()
        
        if not self.vehicle_id:
            raise UserError(_('Lütfen araç seçin.'))
        
        # Küçük araçlar için ilçe kontrolü yapma
        small_vehicles = ['Küçük Araç 1', 'Küçük Araç 2', 'Ek araç', 'Ek Araç']
        is_small_vehicle = self.vehicle_id.name in small_vehicles
        
        if not is_small_vehicle and not self.district_id:
            raise UserError(_('Lütfen ilçe seçin.'))
        
        # Araç ve ilçe uyumluluğu kontrolü
        if not is_small_vehicle and self.district_id:
            # Araç tipini kontrol et
            vehicle_type = self.vehicle_id.vehicle_type
            district_name = self.district_id.name
            
            # Avrupa yakası araçları için Avrupa ilçeleri
            if vehicle_type == 'avrupa':
                avrupa_ilceleri = ['Bağcılar', 'Bakırköy', 'Bayrampaşa', 'Beşiktaş', 'Beylikdüzü', 'Beyoğlu', 'Esenler', 'Esenyurt', 'Fatih', 'Gaziosmanpaşa', 'Güngören', 'Kağıthane', 'Küçükçekmece', 'Sarıyer', 'Silivri', 'Şişli', 'Zeytinburnu']
                if district_name not in avrupa_ilceleri:
                    raise UserError(_(f'"{district_name}" ilçesi Avrupa yakasında değil. "{self.vehicle_id.name}" aracı sadece Avrupa yakası ilçelerinde hizmet verebilir.'))
            
            # Anadolu yakası araçları için Anadolu ilçeleri
            elif vehicle_type == 'anadolu':
                anadolu_ilceleri = ['Ataşehir', 'Beykoz', 'Çekmeköy', 'Kadıköy', 'Kartal', 'Maltepe', 'Pendik', 'Sancaktepe', 'Sultanbeyli', 'Şile', 'Tuzla', 'Ümraniye', 'Üsküdar']
                if district_name not in anadolu_ilceleri:
                    raise UserError(_(f'"{district_name}" ilçesi Anadolu yakasında değil. "{self.vehicle_id.name}" aracı sadece Anadolu yakası ilçelerinde hizmet verebilir.'))
        
        # Uygun tarihleri hesapla ve JSON olarak sakla
        suitable_dates = self._compute_suitable_dates()
        self.result_json = json.dumps(suitable_dates)
        
        # HTML sonuç oluştur
        # Türkçe gün isimleri
        turkish_days = {
            'Monday': 'Pazartesi',
            'Tuesday': 'Salı',
            'Wednesday': 'Çarşamba',
            'Thursday': 'Perşembe',
            'Friday': 'Cuma',
            'Saturday': 'Cumartesi',
            'Sunday': 'Pazar'
        }

        result_html = f"""
        <div style="padding: 10px;">
            <h3 style="color: #2c3e50;">🚚 Araç: {self.vehicle_id.name}</h3>
        """
        
        if not is_small_vehicle and self.district_id:
            result_html += f'<h3 style="color: #2c3e50;">🏘️ İlçe: {self.district_id.name}</h3>'
        elif is_small_vehicle:
            result_html += '<h3 style="color: #2c3e50;">🏘️ İlçe: Kapasite Sorgulaması (İlçe Seçimi Gerekmez)</h3>'
        
        result_html += f"""
            <hr/>
            <h4 style=\"color: #34495e;\">📅 Uygun Tarihler ve Kalan Teslimat Sayıları:</h4>
        """
        
        if suitable_dates:
            result_html += '<table class="table table-striped" style="margin-top: 10px;">'
            result_html += '<thead><tr>'
            result_html += '<th>Oluştur</th>'
            result_html += '<th>Tarih</th>'
            result_html += '<th>Gün</th>'
            result_html += '<th>Kalan</th>'
            result_html += '<th>Kullanılan</th>'
            result_html += '<th>Toplam</th>'
            result_html += '<th>Doluluk</th>'
            result_html += '<th>İşlem</th>'
            result_html += '</tr></thead><tbody>'
            
            for date_info in suitable_dates:
                day_name_tr = turkish_days.get(date_info['day_name'], date_info['day_name'])
                percent_used = int((date_info['used'] / date_info['total']) * 100) if date_info['total'] else 0
                
                # Context parametrelerini hazırla
                context_params = {
                    'default_date': date_info['date'],
                    'default_vehicle_id': self.vehicle_id.id,
                    'default_district_id': self.district_id.id if self.district_id else False,
                    'default_delivery_type': 'transfer'
                }

                # Context'i JSON formatında string'e çevir
                context_str = json.dumps(context_params).replace('"', '&quot;')
                
                result_html += f"""
                <tr>
                    <td>
                        <a href="/web#action={self.env.ref('delivery_module.action_delivery_create_wizard').id}&amp;context={context_str}" 
                           class="btn btn-sm btn-secondary" 
                           style="margin: 2px; text-decoration: none; color: white; display: inline-block; padding: 5px 10px; border: none; cursor: pointer;">Oluştur</a>
                    </td>
                    <td><strong>{datetime.strptime(date_info['date'], '%Y-%m-%d').strftime('%d/%m/%Y')}</strong></td>
                    <td>{day_name_tr}</td>
                    <td><span class="badge badge-success">{date_info['remaining']}</span></td>
                    <td><span class="badge badge-info">{date_info['used']}</span></td>
                    <td><span class="badge badge-secondary">{date_info['total']}</span></td>
                    <td>
                        <div style="width:120px;background:#eee;border-radius:6px;overflow:hidden;">
                            <div style="height:10px;width:{percent_used}%;background:#3498db;"></div>
                        </div>
                        <small>{percent_used}%</small>
                    </td>
                    <td>
                        <a href="/web#action={self.env.ref('delivery_module.action_delivery_create_wizard').id}&amp;context={context_str}" 
                           class="btn btn-sm btn-primary" 
                           style="margin: 2px; text-decoration: none; color: white; display: inline-block; padding: 5px 10px; border: none; cursor: pointer;">➕ Oluştur</a>
                    </td>
                </tr>
                """
            
            result_html += '</tbody></table>'
        else:
            result_html += '<div class="alert alert-warning" style="margin-top: 10px;">❌ Önümüzdeki 30 gün içinde uygun tarih bulunamadı.</div>'
        
        result_html += '</div>'
        
        # Sonucu kaydet
        self.result_html = result_html

    def action_create_earliest(self):
        self.ensure_one()
        dates = self._get_suitable_dates()
        if not dates:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Uyarı'),
                    'message': _('Uygun tarih bulunamadı.'),
                    'type': 'warning',
                }
            }
        earliest = sorted(dates, key=lambda d: d['date'])[0]
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.create.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_date': earliest['date'],
                'default_vehicle_id': self.vehicle_id.id,
                'default_district_id': self.district_id.id if self.district_id else False,
                'default_delivery_type': 'transfer',
            }
        }

    # CSV/PDF dışa aktarma ve rapor kaldırıldı

    def action_clear_form(self):
        """Form alanlarını temizle"""
        self.ensure_one()
        # Sadece sonuç alanını temizle
        self.result_html = False
        # Sayfayı yeniden yükle
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_refresh_form(self):
        """Formu yenile - yeni sorgulama ekranı getir"""
        self.ensure_one()
        # Tüm alanları temizle ve yeni kayıt oluştur
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'availability.check',
            'view_mode': 'form',
            'target': 'current',
            'context': {'create': True},
        } 