# -*- coding: utf-8 -*-

{
    "name": "Widerrufbutton Rechnung",
    "summary": "Optionale Verknuepfung von Widerrufen mit Odoo-Rechnungen.",
    "description": "Optionale Erweiterung fuer odoo_widerrufbutton zur Verknuepfung mit account.move.",
    "version": "19.0.1.0.1",
    "category": "Website/Website",
    "author": "IT-Service AHD",
    "website": "https://it-service-ahd.de",
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
