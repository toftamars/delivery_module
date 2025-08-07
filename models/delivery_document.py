from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class DeliveryDocument(models.Model):
    _name = 'delivery.document'
    _description = 'Teslimat Belgesi'
    _order = 'date desc, id desc'
    _rec_name = 'reference'

    # Otomatik Referans Numarası
    reference = fields.Char('Referans No', required=True, copy=False, readonly=True, 
                           default=lambda self: _('New'))
    
    # Temel Bilgiler
    date = fields.Date('Teslimat Tarihi', required=True, default=fields.Date.today)
    partner_id = fields.Many2one('res.partner', 'Müşteri', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Araç', required=True)
    district_id = fields.Many2one('res.city.district', 'İlçe', required=True)
    
    # Durum
    state = fields.Selection([
        ('draft', 'Taslak'),
        ('confirmed', 'Onaylandı'),
        ('in_progress', 'Devam Ediyor'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi')
    ], string='Durum', default='draft', required=True)
    
    # İstatistikler
    transfer_count = fields.Integer('Transfer Sayısı', default=1)
    district_count = fields.Integer('İlçe Sayısı', compute='_compute_district_count')
    
    # Fotoğraf Alanları
    photo_before_installation = fields.Binary('Kurulum Öncesi Fotoğraf')
    photo_during_installation = fields.Binary('Kurulum Sırasında Fotoğraf')
    photo_after_installation = fields.Binary('Kurulum Sonrası Fotoğraf')
    photo_issue = fields.Binary('Sorun/Arıza Fotoğrafı')
    photo_completion = fields.Binary('Tamamlanma Fotoğrafı')
    photo_other = fields.Binary('Diğer Fotoğraf')
    
    # Notlar
    notes = fields.Text('Notlar')
    
    @api.model
    def create(self, vals):
        """Otomatik referans numarası oluşturur"""
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self._generate_reference()
        return super().create(vals)
    
    def _generate_reference(self):
        """DEL/YYYY/XXXXX formatında referans numarası oluşturur"""
        year = fields.Date.today().year
        last_doc = self.search([
            ('reference', 'like', f'DEL/{year}/%')
        ], order='reference desc', limit=1)
        
        if last_doc and last_doc.reference:
            # Son numarayı al ve artır
            last_number = int(last_doc.reference.split('/')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f'DEL/{year}/{new_number:05d}'
    
    @api.depends('district_id')
    def _compute_district_count(self):
        """İlçe sayısını hesaplar"""
        for record in self:
            if record.date and record.district_id:
                # Aynı günde teslimat yapılan ilçe sayısı
                district_count = self.search_count([
                    ('date', '=', record.date),
                    ('district_id', '!=', False)
                ])
                record.district_count = district_count
            else:
                record.district_count = 0
    
    @api.constrains('date', 'vehicle_id', 'district_id')
    def _check_delivery_compatibility(self):
        """Teslimat uygunluk kontrollerini yapar"""
        for record in self:
            # Tarih kontrolü
            if not self._check_date_compatibility(record.date, record.district_id):
                raise ValidationError(_('Seçilen tarih bu ilçe için uygun teslimat günü değil.'))
            
            # Araç kontrolü
            if not self._check_vehicle_compatibility(record.vehicle_id, record.district_id):
                raise ValidationError(_('Araç seçilen ilçe için uygun değil.'))
            
            # Kapasite kontrolü (sadece normal kullanıcılar için)
            if not self.env.user.has_group('delivery_planning.group_delivery_manager'):
                if not self._check_capacity_compatibility(record.vehicle_id, record.date):
                    raise ValidationError(_('Araç kapasitesi yetersiz.'))
    
    def _check_date_compatibility(self, date, district):
        """Tarih uygunluk kontrolü"""
        # Pazar günü kontrolü
        if date.weekday() == 6:
            return False
        
        # Günlük program kontrolü
        day_number = date.weekday()
        schedule_day = self.env['delivery.schedule.day'].search([
            ('day_number', '=', day_number),
            ('is_active', '=', True)
        ], limit=1)
        
        if not schedule_day:
            return False
        
        # İlçe-gün eşleştirmesi kontrolü
        if district:
            region = self.env['delivery.region'].search([
                ('name', 'ilike', district.name)
            ], limit=1)
            
            if region:
                if region.continent == 'anadolu':
                    return district.id in schedule_day.anadolu_regions.ids
                elif region.continent == 'avrupa':
                    return district.id in schedule_day.avrupa_regions.ids
        
        return True
    
    def _check_vehicle_compatibility(self, vehicle, district):
        """Araç uygunluk kontrolü"""
        if not district:
            return True
        
        region = self.env['delivery.region'].search([
            ('name', 'ilike', district.name)
        ], limit=1)
        
        if region:
            return vehicle.can_assign_to_region(region.continent)
        
        return True
    
    def _check_capacity_compatibility(self, vehicle, date):
        """Kapasite uygunluk kontrolü"""
        daily_deliveries = self.search_count([
            ('vehicle_id', '=', vehicle.id),
            ('date', '=', date),
            ('state', 'in', ['confirmed', 'in_progress', 'completed'])
        ])
        
        return daily_deliveries < vehicle.daily_delivery_limit
    
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
