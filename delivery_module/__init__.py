from . import models
from . import wizard

def post_init_hook(cr, registry):
    """Modül yüklendikten sonra çalışacak hook"""
    from odoo import api, SUPERUSER_ID
    import logging
    
    _logger = logging.getLogger(__name__)
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
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
        raise e
    
    # Teslimat programını ayarla
    try:
        from .data.setup_delivery_schedule import setup_delivery_schedule
        _logger.info("Teslimat programı ayarlanıyor...")
        setup_delivery_schedule(env)
        _logger.info("Teslimat programı başarıyla ayarlandı!")
    except Exception as e:
        _logger.error(f"Teslimat programı ayarlanırken hata: {e}")
        # Hata durumunda modülün çalışmasını engelleme
        raise e 