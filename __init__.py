from . import models
from . import wizard

def post_init_hook(cr, registry):
    """Modül yüklendikten sonra çalışacak hook"""
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Teslimat programını ayarla
    try:
        from .data.setup_delivery_schedule import setup_delivery_schedule
        setup_delivery_schedule(env)
    except Exception as e:
        print(f"Teslimat programı ayarlanırken hata: {e}")
