{
    'name': 'Teslimat Planlama',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Teslimat planlama ve rota optimizasyonu modülü',
    'description': '''
        Teslimat planlama ve rota optimizasyonu için modül.
        Özellikler:
        - Teslimat noktaları yönetimi
        - Rota planlama
        - Araç yönetimi
        - Teslimat takibi
        - SMS bildirimleri
        - Raporlama
        - İlçe bazlı gün kısıtlamaları
        - Araç bazlı teslimat yönetimi
        - Günlük teslimat limitleri
    ''',
    'author': 'Tofta',
    'website': 'https://github.com/toftamars/delivery-planning-odoo',
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'stock',
        'sale'
    ],
    'data': [
        'security/delivery_security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/delivery_data.xml',
        'data/ir_sequence_data.xml',
        'data/cron_data.xml',
        'views/delivery_planning_views.xml',
        'views/delivery_point_views.xml',
        'views/vehicle_views.xml',
        'views/delivery_region_views.xml',
        'views/delivery_document_views.xml',
        'views/wizard_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
}
