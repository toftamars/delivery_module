#!/usr/bin/env python3
"""
IR Model Data Temizleme ve Kontrol Scripti
Bu script, ir_model_data tablosundaki çakışan kayıtları temizler ve kontrol eder.
"""

import logging
import psycopg2
from psycopg2.extras import DictCursor

_logger = logging.getLogger(__name__)

def clean_ir_model_data(cr):
    """
    ir_model_data tablosunu temizler ve kontrol eder
    """
    try:
        _logger.info("🧹 IR Model Data temizleme ve kontrol başlatılıyor...")
        
        # 1. Çakışan kayıtları kontrol et
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
            
            # Çakışan kayıtları sil
            cr.execute("""
                DELETE FROM ir_model_data 
                WHERE module='base' AND name='module_delivery_module'
            """)
            
            _logger.info(f"✅ Çakışan kayıtlar silindi: {cr.rowcount} kayıt etkilendi")
        else:
            _logger.info("✅ 'module_delivery_module' için çakışan kayıt bulunamadı")
        
        # 2. Diğer potansiyel çakışmaları kontrol et
        cr.execute("""
            SELECT module, name, COUNT(*) as count
            FROM ir_model_data
            GROUP BY module, name
            HAVING COUNT(*) > 1
        """)
        
        duplicate_records = cr.fetchall()
        if duplicate_records:
            _logger.warning(f"⚠️ Diğer çakışan kayıtlar bulundu: {len(duplicate_records)} farklı çakışma")
            for record in duplicate_records:
                _logger.warning(f"   - Module: {record[0]}, Name: {record[1]}, Count: {record[2]}")
                
                # Her bir çakışma için detaylı bilgi
                cr.execute("""
                    SELECT id, module, name, model, res_id 
                    FROM ir_model_data 
                    WHERE module=%s AND name=%s
                """, (record[0], record[1]))
                
                details = cr.fetchall()
                for detail in details:
                    _logger.warning(f"      * ID: {detail[0]}, Module: {detail[1]}, Name: {detail[2]}, Model: {detail[3]}, Res_ID: {detail[4]}")
                
                # İlk kayıt dışındakileri sil
                cr.execute("""
                    DELETE FROM ir_model_data 
                    WHERE module=%s AND name=%s AND id NOT IN (
                        SELECT MIN(id) 
                        FROM ir_model_data 
                        WHERE module=%s AND name=%s
                    )
                """, (record[0], record[1], record[0], record[1]))
                
                _logger.info(f"✅ Çakışan kayıtlar temizlendi: {cr.rowcount} kayıt silindi")
        else:
            _logger.info("✅ Diğer çakışan kayıt bulunamadı")
        
        # 3. delivery_module ile ilgili kayıtları temizle
        cr.execute("""
            DELETE FROM ir_model_data 
            WHERE module='delivery_module' AND model='ir.module.module'
        """)
        
        if cr.rowcount > 0:
            _logger.info(f"✅ Modül kayıtları temizlendi: {cr.rowcount} kayıt silindi")
        
        # 4. Kaldırılmış modül kayıtlarını temizle
        cr.execute("""
            DELETE FROM ir_module_module 
            WHERE name='delivery_module' AND state='uninstalled'
        """)
        
        if cr.rowcount > 0:
            _logger.info(f"✅ Kaldırılmış modül kayıtları temizlendi: {cr.rowcount} kayıt silindi")
        
        # 5. Yetim kayıtları temizle (res_id'si olmayan kayıtlar)
        cr.execute("""
            DELETE FROM ir_model_data 
            WHERE model != 'ir.model.fields' AND res_id NOT IN (
                SELECT id FROM ONLY ir_model WHERE ir_model_data.model = 'ir.model'
                UNION ALL
                SELECT id FROM ONLY ir_model_fields WHERE ir_model_data.model = 'ir.model.fields'
                UNION ALL
                SELECT id FROM ONLY ir_model_constraint WHERE ir_model_data.model = 'ir.model.constraint'
                UNION ALL
                SELECT id FROM ONLY ir_ui_view WHERE ir_model_data.model = 'ir.ui.view'
                UNION ALL
                SELECT id FROM ONLY ir_ui_menu WHERE ir_model_data.model = 'ir.ui.menu'
                UNION ALL
                SELECT id FROM ONLY res_groups WHERE ir_model_data.model = 'res.groups'
            ) AND model IN ('ir.model', 'ir.model.fields', 'ir.model.constraint', 'ir.ui.view', 'ir.ui.menu', 'res.groups')
        """)
        
        if cr.rowcount > 0:
            _logger.info(f"✅ Yetim kayıtlar temizlendi: {cr.rowcount} kayıt silindi")
        
        # Değişiklikleri kaydet
        cr.execute("COMMIT")
        _logger.info("✅ Değişiklikler kaydedildi (COMMIT)")
        
        return True
    except Exception as e:
        _logger.error(f"❌ IR Model Data temizlenirken hata: {e}")
        # Rollback
        cr.execute("ROLLBACK")
        _logger.error("❌ Değişiklikler geri alındı (ROLLBACK)")
        return False

def check_ir_model_data_status(cr):
    """
    ir_model_data tablosunun durumunu kontrol eder
    """
    try:
        _logger.info("🔍 IR Model Data durumu kontrol ediliyor...")
        
        # 1. Toplam kayıt sayısı
        cr.execute("SELECT COUNT(*) FROM ir_model_data")
        total_count = cr.fetchone()[0]
        _logger.info(f"📊 Toplam kayıt sayısı: {total_count}")
        
        # 2. Modül bazlı kayıt sayısı
        cr.execute("""
            SELECT module, COUNT(*) as count
            FROM ir_model_data
            GROUP BY module
            ORDER BY count DESC
            LIMIT 10
        """)
        
        module_counts = cr.fetchall()
        _logger.info("📊 En çok kayıt içeren 10 modül:")
        for module, count in module_counts:
            _logger.info(f"   - {module}: {count} kayıt")
        
        # 3. delivery_module kayıtları
        cr.execute("SELECT COUNT(*) FROM ir_model_data WHERE module='delivery_module'")
        delivery_count = cr.fetchone()[0]
        _logger.info(f"📊 delivery_module kayıt sayısı: {delivery_count}")
        
        # 4. Çakışma kontrolü
        cr.execute("""
            SELECT module, name, COUNT(*) as count
            FROM ir_model_data
            GROUP BY module, name
            HAVING COUNT(*) > 1
            LIMIT 5
        """)
        
        duplicate_records = cr.fetchall()
        if duplicate_records:
            _logger.warning(f"⚠️ Hala çakışan kayıtlar var: {len(duplicate_records)} farklı çakışma (ilk 5)")
            for record in duplicate_records:
                _logger.warning(f"   - Module: {record[0]}, Name: {record[1]}, Count: {record[2]}")
            return False
        else:
            _logger.info("✅ Çakışan kayıt bulunamadı")
            return True
            
    except Exception as e:
        _logger.error(f"❌ IR Model Data durumu kontrol edilirken hata: {e}")
        return False
