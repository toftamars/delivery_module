#!/usr/bin/env python3
"""
Acil Durum Veritabanı Düzeltmesi
Bu script, district_id sorununu tamamen çözer.
"""

import psycopg2
import logging

_logger = logging.getLogger(__name__)

def emergency_database_fix(cr):
    """Acil durum veritabanı düzeltmesi"""
    try:
        _logger.info("🚨 ACİL DURUM: Veritabanı düzeltmesi başlatılıyor...")
        
        # 1. district_id sütununu kaldır (varsa)
        cr.execute("""
            DO $$
            BEGIN
                -- district_id sütunu varsa kaldır
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'res_partner' AND column_name = 'district_id'
                ) THEN
                    ALTER TABLE res_partner DROP COLUMN district_id;
                    RAISE NOTICE 'district_id sütunu kaldırıldı';
                ELSE
                    RAISE NOTICE 'district_id sütunu zaten yok';
                END IF;
            END $$;
        """)
        
        # 2. city_id sütununu ekle (yoksa)
        cr.execute("""
            DO $$
            BEGIN
                -- city_id sütunu yoksa ekle
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'res_partner' AND column_name = 'city_id'
                ) THEN
                    ALTER TABLE res_partner ADD COLUMN city_id INTEGER;
                    RAISE NOTICE 'city_id sütunu eklendi';
                ELSE
                    RAISE NOTICE 'city_id sütunu zaten mevcut';
                END IF;
            END $$;
        """)
        
        # 3. Modül tablolarını temizle ve yeniden oluştur
        cr.execute("""
            DROP TABLE IF EXISTS delivery_document CASCADE;
            DROP TABLE IF EXISTS delivery_vehicle CASCADE;
            DROP TABLE IF EXISTS delivery_day CASCADE;
            DROP TABLE IF EXISTS res_city_district CASCADE;
            DROP TABLE IF EXISTS res_city CASCADE;
        """)
        
        # 4. Modül kayıtlarını ve çakışan kayıtları temizle
        cr.execute("""
            DELETE FROM ir_module_module WHERE name = 'teslimat_planlama';
            DELETE FROM ir_model_data WHERE module = 'teslimat_planlama';
            DELETE FROM ir_model_data WHERE module = 'base' AND name = 'module_teslimat_planlama';
            DELETE FROM ir_model_fields WHERE model LIKE 'delivery.%';
            DELETE FROM ir_model WHERE model LIKE 'delivery.%';
        """)
        
        # 5. Cache'i temizle
        cr.execute("""
            DELETE FROM ir_translation WHERE module = 'teslimat_planlama';
        """)
        
        _logger.info("✅ Acil durum düzeltmesi tamamlandı!")
        _logger.info("📋 Yapılan işlemler:")
        _logger.info("   - district_id sütunu kaldırıldı")
        _logger.info("   - city_id sütunu eklendi")
        _logger.info("   - Modül tabloları temizlendi")
        _logger.info("   - Modül kayıtları temizlendi")
        _logger.info("   - Cache temizlendi")
        
    except Exception as e:
        _logger.error(f"❌ Acil durum düzeltmesi sırasında hata: {e}")
        raise e

def check_fix_status(cr):
    """Düzeltme durumunu kontrol et"""
    try:
        _logger.info("🔍 Düzeltme durumu kontrol ediliyor...")
        
        # district_id sütunu kontrol et
        cr.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'res_partner' 
            AND column_name = 'district_id'
        """)
        
        district_exists = cr.fetchone() is not None
        
        # city_id sütunu kontrol et
        cr.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'res_partner' 
            AND column_name = 'city_id'
        """)
        
        city_exists = cr.fetchone() is not None
        
        if not district_exists and city_exists:
            _logger.info("✅ Düzeltme başarılı!")
            _logger.info("   - district_id sütunu: YOK ✅")
            _logger.info("   - city_id sütunu: VAR ✅")
            return True
        else:
            _logger.warning("❌ Düzeltme tamamlanmadı!")
            _logger.warning(f"   - district_id sütunu: {'VAR ❌' if district_exists else 'YOK ✅'}")
            _logger.warning(f"   - city_id sütunu: {'VAR ✅' if city_exists else 'YOK ❌'}")
            return False
            
    except Exception as e:
        _logger.error(f"❌ Durum kontrolü sırasında hata: {e}")
        return False
