from . import models
from . import wizard

def post_init_hook(cr, registry):
    """Modül yüklendikten sonra çalışacak hook"""
    from odoo import api, SUPERUSER_ID
    import logging
    
    _logger = logging.getLogger(__name__)
    
    # Database migration ve IR Model Data temizleme
    try:
        from .data.database_migration import migrate_database, check_migration_status
        _logger.info("🚀 Database migration başlatılıyor...")
        
        # Migration yap
        if migrate_database(cr, registry):
            _logger.info("✅ Database migration başarılı!")
        else:
            _logger.error("❌ Database migration başarısız!")
            raise Exception("Database migration başarısız!")
        
        # Migration durumunu kontrol et
        if check_migration_status(cr):
            _logger.info("✅ Migration durumu kontrol edildi - başarılı!")
        else:
            _logger.warning("⚠️ Migration durumunda sorunlar olabilir!")
            
    except Exception as e:
        _logger.error(f"❌ Database migration sırasında hata: {e}")
        # Devam et
        pass
    
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
        # Devam et
        pass
    
    # Teslimat programını ayarla
    try:
        from .data.setup_delivery_schedule import setup_delivery_schedule
        _logger.info("Teslimat programı ayarlanıyor...")
        setup_delivery_schedule(env)
        _logger.info("Teslimat programı başarıyla ayarlandı!")
    except Exception as e:
        _logger.error(f"Teslimat programı ayarlanırken hata: {e}")
        # Hata durumunda modülün çalışmasını engelleme - sadece log yaz
        _logger.warning("Teslimat programı ayarlanamadı ama modül çalışmaya devam edecek")
        # raise e  # Bu satırı kaldırdık
