#!/usr/bin/env python3
"""
Duplicate Key Hatası Düzeltme Scripti
Bu script, "ir_model_data_module_name_uniq_index" kısıtlamasını ihlal eden kayıtları temizler.
"""

import logging

_logger = logging.getLogger(__name__)

def fix_duplicate_key(cr):
    """Çakışan ir_model_data kayıtlarını temizle"""
    try:
        _logger.info("🔧 Çakışan ir_model_data kayıtları temizleniyor...")
        
        # Çakışan kaydı kontrol et
        cr.execute("""
            SELECT id, module, name, model, res_id 
            FROM ir_model_data 
            WHERE module='base' AND name='module_delivery_module'
        """)
        
        records = cr.fetchall()
        if records:
            _logger.info(f"🔍 Çakışan kayıtlar bulundu: {len(records)} kayıt")
            for record in records:
                _logger.info(f"   - ID: {record[0]}, Module: {record[1]}, Name: {record[2]}, Model: {record[3]}, Res_ID: {record[4]}")
            
            # Çakışan kaydı sil
            cr.execute("""
                DELETE FROM ir_model_data 
                WHERE module='base' AND name='module_delivery_module'
            """)
            
            _logger.info(f"✅ Çakışan kayıtlar silindi: {cr.rowcount} kayıt etkilendi")
        else:
            _logger.info("✅ Çakışan kayıt bulunamadı")
        
        # Modül kaydını temizle
        cr.execute("""
            DELETE FROM ir_module_module 
            WHERE name='delivery_module' AND state='uninstalled'
        """)
        
        if cr.rowcount > 0:
            _logger.info(f"✅ Kaldırılmış modül kayıtları silindi: {cr.rowcount} kayıt etkilendi")
        
        # Commit değişiklikleri
        cr.execute("COMMIT")
        _logger.info("✅ Değişiklikler kaydedildi (COMMIT)")
        
        return True
    except Exception as e:
        _logger.error(f"❌ Çakışan kayıtları temizlerken hata: {e}")
        # Rollback
        cr.execute("ROLLBACK")
        _logger.error("❌ Değişiklikler geri alındı (ROLLBACK)")
        return False
