from . import models
from . import wizard

def post_init_hook(cr, registry):
    """Modül yüklendikten sonra çalışacak hook"""
    from odoo import api, SUPERUSER_ID
    import logging
    
    _logger = logging.getLogger(__name__)
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
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