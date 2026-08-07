# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    widerruf_internal_notify_email = fields.Char(
        string="Interne Benachrichtigungsadresse",
        config_parameter="odoo_widerrufbutton.internal_notify_email",
        help="E-Mail-Adresse, die bei neuen Widerrufen intern informiert wird.",
    )
    widerruf_activity_user_id = fields.Many2one(
        "res.users",
        string="Zuständiger Benutzer für Widerrufe",
        config_parameter="odoo_widerrufbutton.activity_user_id",
        help="Für diesen Benutzer wird bei neuen Widerrufen automatisch eine Aktivität erstellt.",
    )
    widerruf_send_customer_status_mail = fields.Boolean(
        string="Kunden bei Statusänderungen per E-Mail informieren",
        config_parameter="odoo_widerrufbutton.send_customer_status_mail",
        default=True,
    )
    widerruf_create_activity = fields.Boolean(
        string="Aktivität bei neuem Widerruf erstellen",
        config_parameter="odoo_widerrufbutton.create_activity",
        default=True,
    )
    widerruf_send_internal_mail = fields.Boolean(
        string="Interne E-Mail bei neuem Widerruf senden",
        config_parameter="odoo_widerrufbutton.send_internal_mail",
        default=True,
    )
    widerruf_upload_enabled = fields.Boolean(
        string="Dateiupload im Widerrufsformular aktivieren",
        config_parameter="odoo_widerrufbutton.upload_enabled",
        default=True,
    )
    widerruf_allowed_file_extensions = fields.Char(
        string="Erlaubte Dateiendungen",
        config_parameter="odoo_widerrufbutton.allowed_file_extensions",
        default="pdf,jpg,jpeg,png",
        help="Kommagetrennte Liste erlaubter Dateiendungen ohne Punkt, z. B. pdf,jpg,png.",
    )
    widerruf_max_upload_size_mb = fields.Integer(
        string="Maximale Dateigröße in MB",
        config_parameter="odoo_widerrufbutton.max_upload_size_mb",
        default=10,
    )
    widerruf_show_portal = fields.Boolean(
        string="Widerrufe im Kundenportal anzeigen",
        config_parameter="odoo_widerrufbutton.show_portal",
        default=True,
    )
    widerruf_activity_deadline_days = fields.Integer(
        string="Fälligkeit der Aktivität in Tagen",
        config_parameter="odoo_widerrufbutton.activity_deadline_days",
        default=1,
    )
    widerruf_footer_button_enabled = fields.Boolean(
        string="Footer-Button anzeigen",
        config_parameter="odoo_widerrufbutton.footer_button_enabled",
        default=True,
    )
    widerruf_customer_intro_text = fields.Char(
        string="Einleitungstext auf der Widerrufsseite",
        config_parameter="odoo_widerrufbutton.customer_intro_text",
        default="Füllen Sie die folgenden Angaben aus. Im nächsten Schritt können Sie Ihre Eingaben prüfen und den Widerruf ausdrücklich bestätigen.",
    )
