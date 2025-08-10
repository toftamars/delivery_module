{
    'name': 'Teslimat Modülü',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Teslimat belgeleri ve araç yönetimi',
    'description': """
        Teslimat belgeleri oluşturma ve yönetimi
        Araç kapasite kontrolü
        Uygunluk kontrolü
        Teslimat fotoğrafları
        İlçe bazlı teslimat programı
    """,
    'author': 'Tofta',
    'website': 'https://www.example.com',
    'depends': [
        'base',
        'stock',
        'sale',
        'mail',
    ],
    'data': [
        'security/delivery_security.xml',
        'security/ir.model.access.csv',
        'data/delivery_data.xml',
        'data/ir_sequence_data.xml',
        'data/setup_delivery_schedule_data.xml',
        'views/action_views.xml',
        'views/delivery_views.xml',
        'views/delivery_day_views.xml',
        'views/delivery_vehicle_views.xml',
        'views/delivery_photo_views.xml',
        'views/availability_check_views.xml',
        'views/res_city_views.xml',
        'views/res_city_district_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
        'wizard/delivery_create_wizard_views.xml',
        'wizard/delivery_photo_wizard_views.xml',
        'wizard/cancel_confirmation_wizard_views.xml',
        'wizard/delivery_day_closure_wizard_views.xml',
        'wizard/delivery_vehicle_closure_wizard_views.xml',
        'wizard/delivery_limit_warning_wizard_views.xml',
        'wizard/setup_delivery_schedule_wizard_views.xml',
        'wizard/delivery_location_update_wizard_views.xml',
        'wizard/delivery_route_info_wizard_views.xml',

    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
} 