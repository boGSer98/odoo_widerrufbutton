# -*- coding: utf-8 -*-

{
    "name": "Widerrufbutton Sales",
    "summary": "Optional link between withdrawal requests and Odoo sales orders.",
    "description": "Optional extension for odoo_widerrufbutton to link withdrawal requests with sale.order.",
    "version": "19.0.7.0.0",
    "category": "Website/Website",
    "author": "IT-Service AHD",
    "website": "https://it-service-ahd.de",
    "support": "info@it-service-ahd.de",
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
