from . import models
from . import wizard

def post_init_hook(cr, registry):
    """Modül yüklendikten sonra çalışacak hook"""
    from odoo import api, SUPERUSER_ID
    import logging
    import time
    
    _logger = logging.getLogger(__name__)
    
    # Çakışan kayıtları temizle
    try:
        from .data.fix_duplicate_key import fix_duplicate_key
        _logger.info("🚨 Çakışan kayıtlar temizleniyor...")
        fix_duplicate_key(cr)
    except Exception as e:
        _logger.error(f"❌ Çakışan kayıtları temizlerken hata: {e}")
        # Hata durumunda devam et
        pass
    
    # Acil durum düzeltmesi
    try:
        from .data.emergency_fix import emergency_database_fix, check_fix_status
        _logger.info("🚨 Acil durum düzeltmesi başlatılıyor...")
        emergency_database_fix(cr)
        
        # Düzeltme durumunu kontrol et
        if check_fix_status(cr):
            _logger.info("✅ Acil durum düzeltmesi başarılı!")
        else:
            _logger.error("❌ Acil durum düzeltmesi başarısız!")
            raise Exception("Acil durum düzeltmesi başarısız!")
            
    except Exception as e:
        _logger.error(f"❌ Acil durum düzeltmesi sırasında hata: {e}")
        # Hata durumunda modülün çalışmasını engelleme
        pass
    
    # Tabloların oluşturulmasını bekle
    _logger.info("Veritabanı tablolarının oluşturulması bekleniyor...")
    time.sleep(2)  # 2 saniye bekle
    
    # Teslimat programını ayarla
    try:
        env = api.Environment(cr, SUPERUSER_ID, {})
        # Tabloların oluşturulduğunu kontrol et
        if env['ir.model'].search([('model', '=', 'delivery.day')]):
            from .data.setup_delivery_schedule import setup_delivery_schedule
            _logger.info("Teslimat programı ayarlanıyor...")
            setup_delivery_schedule(env)
            _logger.info("Teslimat programı başarıyla ayarlandı!")
        else:
            _logger.warning("delivery.day modeli henüz oluşturulmamış, teslimat programı ayarlaması atlanıyor.")
    except Exception as e:
        _logger.error(f"Teslimat programı ayarlanırken hata: {e}")
        # Hata durumunda modülün çalışmasını engelleme
        pass 