# -*- coding: utf-8 -*-

{
    "name": "Widerrufbutton Invoicing",
    "summary": "Optional link between withdrawal requests and Odoo invoices.",
    "description": "Optional extension for odoo_widerrufbutton to link withdrawal requests with account.move.",
    "version": "19.0.1.0.2",
    "category": "Website/Website",
    "author": "IT-Service AHD",
    "website": "https://it-service-ahd.de",
    "support": "info@it-service-ahd.de",
    "license": "LGPL-3",
    "depends": [
        "odoo_widerrufbutton",
        "account",
    ],
    "data": [
        "views/widerruf_record_account_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
