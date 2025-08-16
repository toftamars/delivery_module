from . import models
from . import wizard

def post_init_hook(cr, registry):
    """Modül yüklendikten sonra çalışacak hook"""
    from odoo import api, SUPERUSER_ID
    import logging
    
    _logger = logging.getLogger(__name__)
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Veritabanı şemasını güncelle
    try:
        from .data.database_migration import migrate_database_schema
        _logger.info("Veritabanı şeması güncelleniyor...")
        migrate_database_schema(cr)
        _logger.info("Veritabanı şeması başarıyla güncellendi!")
    except Exception as e:
        _logger.error(f"Veritabanı şeması güncellenirken hata: {e}")
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