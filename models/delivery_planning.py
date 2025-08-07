from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class DeliveryPlanning(models.Model):
    _name = 'delivery.planning'
    _description = 'Teslimat Planlama'
    _order = 'date desc'

    name = fields.Char('Plan Adı', required=True)
    date = fields.Date('Teslimat Tarihi', default=fields.Date.today, required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Araç', required=True)
    driver_id = fields.Many2one('res.partner', 'Sürücü', required=True)
    
    # SMS Bildirim Durumları
    sms_sent_on_way = fields.Boolean('Yolda SMS Gönderildi', default=False)
    sms_sent_completed = fields.Boolean('Tamamlandı SMS Gönderildi', default=False)
    sms_sent_cancelled = fields.Boolean('İptal SMS Gönderildi', default=False)
    state = fields.Selection([
        ('draft', 'Taslak'),
        ('confirmed', 'Onaylandı'),
        ('in_progress', 'Devam Ediyor'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi')
    ], string='Durum', default='draft', required=True)
    
    delivery_point_ids = fields.One2many('delivery.point', 'planning_id', 'Teslimat Noktaları')
    total_distance = fields.Float('Toplam Mesafe (km)', compute='_compute_total_distance')
    estimated_duration = fields.Float('Tahmini Süre (saat)', compute='_compute_estimated_duration')
    
    notes = fields.Text('Notlar')
    
    @api.depends('delivery_point_ids')
    def _compute_total_distance(self):
        for record in self:
            total = 0.0
            for point in record.delivery_point_ids:
                total += point.distance_from_previous or 0.0
            record.total_distance = total
    
    @api.depends('total_distance')
    def _compute_estimated_duration(self):
        for record in self:
            # Ortalama hız 50 km/saat varsayımı
            record.estimated_duration = record.total_distance / 50.0 if record.total_distance > 0 else 0.0
    
    def action_confirm(self):
        self.state = 'confirmed'
    
    def action_start(self):
        self.state = 'in_progress'
    
    def action_complete(self):
        self.state = 'completed'
    
    def action_cancel(self):
        self.state = 'cancelled'
    
    def action_reset_draft(self):
        self.state = 'draft'
    
    @api.constrains('date', 'vehicle_id', 'delivery_point_ids')
    def _check_delivery_compatibility(self):
        """Teslimat uygunluk kontrollerini yapar"""
        for record in self:
            # Tarih kontrolü
            if not self._check_date_compatibility(record.date):
                raise ValidationError(_('Seçilen tarih uygun teslimat günü değil.'))
            
            # Araç kontrolü
            if not self._check_vehicle_compatibility(record.vehicle_id, record.delivery_point_ids):
                raise ValidationError(_('Araç seçilen bölgeler için uygun değil.'))
            
            # Kapasite kontrolü
            if not self._check_capacity_compatibility(record.vehicle_id, record.date):
                raise ValidationError(_('Araç kapasitesi yetersiz.'))
    
    def _check_date_compatibility(self, date):
        """Tarih uygunluk kontrolü"""
        # Pazar günü kontrolü (6 = Pazar)
        if date.weekday() == 6:
            return False
        
        # Günlük program kontrolü
        day_number = date.weekday()
        schedule_day = self.env['delivery.schedule.day'].search([
            ('day_number', '=', day_number),
            ('is_active', '=', True)
        ], limit=1)
        
        return bool(schedule_day)
    
    def _check_vehicle_compatibility(self, vehicle, delivery_points):
        """Araç uygunluk kontrolü"""
        for point in delivery_points:
            if point.region_id:
                if not vehicle.can_assign_to_region(point.region_id.continent):
                    return False
        return True
    
    def _check_capacity_compatibility(self, vehicle, date):
        """Kapasite uygunluk kontrolü"""
        # Yönetici kontrolü
        if self.env.user.has_group('base.group_system'):
            return True
        
        # Günlük teslimat sayısı kontrolü
        daily_deliveries = self.search_count([
            ('vehicle_id', '=', vehicle.id),
            ('date', '=', date),
            ('state', 'in', ['confirmed', 'in_progress', 'completed'])
        ])
        
        return daily_deliveries < vehicle.daily_delivery_limit
    
    def send_sms_notification(self, notification_type):
        """SMS bildirimi gönderir"""
        for record in self:
            for point in record.delivery_point_ids:
                if point.partner_id and point.partner_id.mobile:
                    message = self._prepare_sms_message(point, notification_type)
                    # SMS gönderme işlemi burada yapılacak
                    # self._send_sms(point.partner_id.mobile, message)
                    
                    # SMS durumunu güncelle
                    if notification_type == 'on_way':
                        record.sms_sent_on_way = True
                    elif notification_type == 'completed':
                        record.sms_sent_completed = True
                    elif notification_type == 'cancelled':
                        record.sms_sent_cancelled = True
    
    def _prepare_sms_message(self, delivery_point, notification_type):
        """SMS mesajını hazırlar"""
        messages = {
            'on_way': f'Sayın {delivery_point.partner_id.name}, teslimatınız yola çıktı. Tahmini süre: {delivery_point.estimated_time} dakika.',
            'completed': f'Sayın {delivery_point.partner_id.name}, teslimatınız tamamlandı. Teşekkürler.',
            'cancelled': f'Sayın {delivery_point.partner_id.name}, teslimatınız iptal edildi. Özür dileriz.'
        }
        return messages.get(notification_type, '')
    
    def action_start(self):
        self.state = 'in_progress'
        self.send_sms_notification('on_way')
    
    def action_complete(self):
        self.state = 'completed'
        self.send_sms_notification('completed')
    
    def action_cancel(self):
        self.state = 'cancelled'
        self.send_sms_notification('cancelled')
