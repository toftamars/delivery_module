#!/usr/bin/env python3
"""
Database Migration Script
Bu script, teslimat modülü için gerekli veritabanı düzenlemelerini yapar.
"""

import logging
# Odoo import'ları sadece Odoo ortamında çalışır
# from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate_database(cr, registry):
    """Veritabanı migration işlemi"""
    try:
        _logger.info("🚀 Database migration başlatılıyor...")
        
        # 1. ir_model_data çakışmalarını temizle
        _logger.info("🧹 IR Model Data çakışmaları temizleniyor...")
        
        # Çakışan modül kayıtlarını temizle
        conflicting_names = ['module_teslimat_planlama', 'module_delivery_module', 'module_tofta_delivery_module']
        
        for name in conflicting_names:
            # Önce mevcut kayıtları kontrol et
            cr.execute("""
                SELECT id, module, name, model, res_id 
                FROM ir_model_data 
                WHERE module='base' AND name=%s
            """, (name,))
            
            records = cr.fetchall()
            if records:
                _logger.info(f"🔍 Çakışan kayıt bulundu: {name} - {len(records)} kayıt")
                
                # Çakışan kayıtları sil
                cr.execute("""
                    DELETE FROM ir_model_data 
                    WHERE module='base' AND name=%s
                """, (name,))
                
                _logger.info(f"✅ Çakışan kayıtlar temizlendi: {name}")
            else:
                _logger.info(f"✅ Çakışan kayıt bulunamadı: {name}")
        
        # 2. Eski modül kayıtlarını temizle
        _logger.info("🧹 Eski modül kayıtları temizleniyor...")
        
        old_modules = ['teslimat_planlama', 'delivery_module']
        
        for module_name in old_modules:
            # ir_module_module tablosundan temizle
            cr.execute("""
                DELETE FROM ir_module_module 
                WHERE name = %s
            """, (module_name,))
            
            if cr.rowcount > 0:
                _logger.info(f"✅ {module_name} modül kaydı silindi: {cr.rowcount} kayıt")
            
            # ir_model_data tablosundan temizle
            cr.execute("""
                DELETE FROM ir_model_data 
                WHERE module = %s
            """, (module_name,))
            
            if cr.rowcount > 0:
                _logger.info(f"✅ {module_name} model data kayıtları silindi: {cr.rowcount} kayıt")
        
        # 3. Delivery ile ilgili eski model kayıtlarını temizle
        _logger.info("🧹 Eski delivery model kayıtları temizleniyor...")
        
        cr.execute("""
            DELETE FROM ir_model_fields 
            WHERE model LIKE 'delivery.%'
        """)
        
        if cr.rowcount > 0:
            _logger.info(f"✅ Eski delivery model fields temizlendi: {cr.rowcount} kayıt")
        
        cr.execute("""
            DELETE FROM ir_model 
            WHERE model LIKE 'delivery.%'
        """)
        
        if cr.rowcount > 0:
            _logger.info(f"✅ Eski delivery model kayıtları temizlendi: {cr.rowcount} kayıt")
        
        # 4. Cache temizle
        _logger.info("🧹 Cache temizleniyor...")
        
        cr.execute("""
            DELETE FROM ir_translation 
            WHERE module IN ('teslimat_planlama', 'delivery_module')
        """)
        
        if cr.rowcount > 0:
            _logger.info(f"✅ Translation cache temizlendi: {cr.rowcount} kayıt")
        
        # 5. Commit değişiklikleri
        cr.commit()
        
        _logger.info("✅ Database migration başarıyla tamamlandı!")
        return True
        
    except Exception as e:
        _logger.error(f"❌ Database migration sırasında hata: {e}")
        cr.rollback()
        return False

def check_migration_status(cr):
    """Migration durumunu kontrol et"""
    try:
        _logger.info("🔍 Migration durumu kontrol ediliyor...")
        
        # Çakışan kayıtları kontrol et
        conflicting_names = ['module_teslimat_planlama', 'module_delivery_module']
        has_conflicts = False
        
        for name in conflicting_names:
            cr.execute("""
                SELECT COUNT(*) 
                FROM ir_model_data 
                WHERE module='base' AND name=%s
            """, (name,))
            
            count = cr.fetchone()[0]
            if count > 0:
                _logger.warning(f"⚠️ Hala çakışan kayıt var: {name} - {count} kayıt")
                has_conflicts = True
            else:
                _logger.info(f"✅ Çakışan kayıt yok: {name}")
        
        # Eski modül kayıtlarını kontrol et
        old_modules = ['teslimat_planlama', 'delivery_module']
        
        for module_name in old_modules:
            cr.execute("""
                SELECT COUNT(*) 
                FROM ir_module_module 
                WHERE name = %s
            """, (module_name,))
            
            count = cr.fetchone()[0]
            if count > 0:
                _logger.warning(f"⚠️ Hala eski modül kaydı var: {module_name} - {count} kayıt")
                has_conflicts = True
            else:
                _logger.info(f"✅ Eski modül kaydı yok: {module_name}")
        
        if not has_conflicts:
            _logger.info("✅ Migration başarılı - tüm çakışmalar çözüldü!")
            return True
        else:
            _logger.warning("⚠️ Migration tamamlanmadı - hala çakışmalar var!")
            return False
            
    except Exception as e:
        _logger.error(f"❌ Migration durumu kontrol edilirken hata: {e}")
        return False
