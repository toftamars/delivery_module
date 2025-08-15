{
    'name': 'Teslimat Modülü',
    'version': '1.0.3',
    'category': 'Inventory',
    'summary': 'Teslimat yönetimi için modül',
    'description': """
        Teslimat yönetimi için modül.
        Özellikler:
        - Transfer belgelerinden otomatik teslimat oluşturma
        - SMS bildirim entegrasyonu
        - Rota ve harita desteği
        - İlçe bazlı gün kısıtlamaları
        - Araç bazlı teslimat yönetimi
        - Günlük teslimat limitleri
        - Geçici teslimat günü kapatma
    """,
    'author': 'Tofta',
    'website': 'https://github.com/toftamars/delivery_module',
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'stock',
        'sms',
        'base_setup',
        'resource'
    ],
    'data': [
        'security/delivery_security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/delivery_data.xml',
        'data/ir_sequence_data.xml',
        'views/delivery_views.xml',
        'views/delivery_vehicle_views.xml',
        'views/delivery_day_views.xml',
        'views/res_partner_views.xml',
        'views/res_city_views.xml',
        'views/res_city_district_views.xml',
        'views/action_views.xml',
        'wizard/delivery_create_wizard_views.xml',
        'wizard/delivery_limit_warning_wizard_views.xml',
        'wizard/delivery_day_closure_wizard_views.xml',
        'wizard/delivery_vehicle_closure_wizard_views.xml',
        'wizard/setup_delivery_schedule_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
} 