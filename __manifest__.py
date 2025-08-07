{
    "name": "Teslimat Planlama",
    "version": "1.0",
    "category": "Inventory",
    "summary": "Teslimat planlama ve rota optimizasyonu modülü",
    "description": "Bu modül teslimat planlama ve rota optimizasyonu için geliştirilmiştir.",
    "author": "Tofta",
    "website": "https://github.com/toftamars/delivery-planning-odoo",
    "depends": ["base", "mail", "web", "contacts", "stock", "sale"],
    "data": [
        "security/delivery_security.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "data/cron_data.xml",
        "views/delivery_planning_views.xml",
        "views/delivery_point_views.xml",
        "views/vehicle_views.xml",
        "views/delivery_region_views.xml",
        "views/delivery_document_views.xml",
        "views/wizard_views.xml",
        "views/menu_views.xml"
    ],
    "demo": [
        "demo/demo_data.xml"
    ],
    "installable": true,
    "application": true,
    "auto_install": false,
    "license": "LGPL-3"
}
