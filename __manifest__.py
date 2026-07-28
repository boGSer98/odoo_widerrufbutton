# -*- coding: utf-8 -*-

{
    "name": "Widerrufbutton Website",
    "summary": "Website withdrawal form with portal and backend management.",
    "description": "Website withdrawal form with portal and backend management.",
    "version": "saas~19.4.6.0.7",
    "category": "Website/Website",
    "author": "IT-Service AHD",
    "website": "https://it-service-ahd.de",
    "license": "LGPL-3",
    "depends": [
        "website",
        "mail",
        "portal",
    ],
    "data": [
        "security/ir.access.csv",
        "data/sequence.xml",
        "data/mail_template.xml",
        "views/res_config_settings_views.xml",
        "views/widerruf_record_views_19.xml",
        "views/website_widerruf_templates.xml",
        "views/portal_widerruf_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "odoo_widerrufbutton/static/src/scss/widerrufbutton.scss",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
