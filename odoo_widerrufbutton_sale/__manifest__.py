# -*- coding: utf-8 -*-

{
    "name": "Widerrufbutton Verkauf",
    "summary": "Optionale Verknuepfung von Widerrufen mit Odoo-Verkaufsauftraegen.",
    "description": "Optionale Erweiterung fuer odoo_widerrufbutton zur Verknuepfung mit sale.order.",
    "version": "19.0.1.1.0",
    "category": "Website/Website",
    "author": "IT-Service AHD",
    "website": "https://it-service-ahd.de",
    "license": "LGPL-3",
    "depends": [
        "odoo_widerrufbutton",
        "sale",
    ],
    "data": [
        "views/widerruf_record_sale_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
