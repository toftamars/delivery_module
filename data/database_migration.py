#!/usr/bin/env python3
"""
Veritabanı Migration Script
Bu script, delivery_module için gerekli veritabanı şeması değişikliklerini yapar.
"""

import psycopg2
import logging

_logger = logging.getLogger(__name__)

def migrate_database_schema(cr):
    """Veritabanı şemasını günceller"""
    try:
        _logger.info("Veritabanı şeması güncelleniyor...")
        
        # res_partner tablosuna city_id sütununu ekle
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
        
        # res_city tablosunu oluştur (yoksa)
        cr.execute("""
            CREATE TABLE IF NOT EXISTS res_city (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                active BOOLEAN DEFAULT TRUE,
                create_uid INTEGER,
                create_date TIMESTAMP,
                write_uid INTEGER,
                write_date TIMESTAMP
            );
        """)
        
        # res_city_district tablosunu oluştur (yoksa)
        cr.execute("""
            CREATE TABLE IF NOT EXISTS res_city_district (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                city_id INTEGER REFERENCES res_city(id),
                active BOOLEAN DEFAULT TRUE,
                create_uid INTEGER,
                create_date TIMESTAMP,
                write_uid INTEGER,
                write_date TIMESTAMP
            );
        """)
        
        # Foreign key constraint'leri ekle
        cr.execute("""
            DO $$
            BEGIN
                -- city_id foreign key constraint
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.table_constraints 
                    WHERE constraint_name = 'res_partner_city_id_fkey'
                ) THEN
                    ALTER TABLE res_partner 
                    ADD CONSTRAINT res_partner_city_id_fkey 
                    FOREIGN KEY (city_id) REFERENCES res_city(id);
                    RAISE NOTICE 'city_id foreign key constraint eklendi';
                ELSE
                    RAISE NOTICE 'city_id foreign key constraint zaten mevcut';
                END IF;
            END $$;
        """)
        
        _logger.info("Veritabanı şeması başarıyla güncellendi!")
        
    except Exception as e:
        _logger.error(f"Veritabanı şeması güncellenirken hata: {e}")
        raise e

def check_database_schema(cr):
    """Veritabanı şemasını kontrol eder"""
    try:
        _logger.info("Veritabanı şeması kontrol ediliyor...")
        
        # Gerekli sütunları kontrol et
        cr.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'res_partner' 
            AND column_name IN ('city_id')
        """)
        
        columns = [row[0] for row in cr.fetchall()]
        
        if 'city_id' in columns:
            _logger.info("✅ Tüm gerekli sütunlar mevcut")
            return True
        else:
            _logger.warning("❌ Eksik sütunlar: " + str([col for col in ['city_id'] if col not in columns]))
            return False
            
    except Exception as e:
        _logger.error(f"Veritabanı şeması kontrol edilirken hata: {e}")
        return False

def emergency_fix_database(cr):
    """Acil durum veritabanı düzeltmesi"""
    try:
        _logger.info("Acil durum veritabanı düzeltmesi başlatılıyor...")
        
        # Tüm modül tablolarını temizle
        cr.execute("""
            DROP TABLE IF EXISTS delivery_document CASCADE;
            DROP TABLE IF EXISTS delivery_vehicle CASCADE;
            DROP TABLE IF EXISTS delivery_day CASCADE;
            DROP TABLE IF EXISTS res_city_district CASCADE;
            DROP TABLE IF EXISTS res_city CASCADE;
        """)
        
        # Modül kayıtlarını temizle
        cr.execute("""
            DELETE FROM ir_module_module WHERE name = 'delivery_module';
            DELETE FROM ir_model_data WHERE module = 'delivery_module';
        """)
        
        _logger.info("Veritabanı temizlendi, modül yeniden yüklenebilir")
        
    except Exception as e:
        _logger.error(f"Acil durum düzeltmesi sırasında hata: {e}")
        raise e
