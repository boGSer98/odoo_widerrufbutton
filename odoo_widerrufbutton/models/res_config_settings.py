# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from ..validation import single_email


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    widerruf_internal_notify_email = fields.Char(
        string="Internal notification address",
        config_parameter="odoo_widerrufbutton.internal_notify_email",
        help="Email address notified internally about new withdrawals.",
    )
    widerruf_activity_user_id = fields.Many2one(
        "res.users",
        string="Withdrawal responsible user",
        config_parameter="odoo_widerrufbutton.activity_user_id",
        help="User assigned to the activity for new withdrawals.",
    )
    widerruf_send_customer_status_mail = fields.Boolean(
        string="Email customers on status changes",
        config_parameter="odoo_widerrufbutton.send_customer_status_mail",
        default=True,
    )
    widerruf_create_activity = fields.Boolean(
        string="Create activity on new withdrawal",
        config_parameter="odoo_widerrufbutton.create_activity",
        default=True,
    )
    widerruf_send_internal_mail = fields.Boolean(
        string="Send internal email on new withdrawal",
        config_parameter="odoo_widerrufbutton.send_internal_mail",
        default=True,
    )
    widerruf_upload_enabled = fields.Boolean(
        string="Enable file uploads",
        config_parameter="odoo_widerrufbutton.upload_enabled",
        default=True,
    )
    widerruf_allowed_file_extensions = fields.Char(
        string="Allowed file extensions",
        config_parameter="odoo_widerrufbutton.allowed_file_extensions",
        default="pdf,jpg,jpeg,png",
        help="Comma-separated allowed extensions without a dot, for example pdf,jpg,png.",
    )
    widerruf_max_upload_size_mb = fields.Integer(
        string="Maximum upload size in MB",
        config_parameter="odoo_widerrufbutton.max_upload_size_mb",
        default=10,
    )
    widerruf_show_portal = fields.Boolean(
        string="Show withdrawals in customer portal",
        config_parameter="odoo_widerrufbutton.show_portal",
        default=True,
    )
    widerruf_activity_deadline_days = fields.Integer(
        string="Activity deadline in days",
        config_parameter="odoo_widerrufbutton.activity_deadline_days",
        default=1,
    )
    widerruf_footer_button_enabled = fields.Boolean(
        string="Show footer button",
        config_parameter="odoo_widerrufbutton.footer_button_enabled",
        default=True,
    )
    widerruf_customer_intro_text = fields.Char(
        string="Withdrawal introduction",
        config_parameter="odoo_widerrufbutton.customer_intro_text",
        default="Complete your details. You can review and explicitly confirm your withdrawal in the next step.",
    )

    @api.constrains("widerruf_max_upload_size_mb", "widerruf_activity_deadline_days", "widerruf_allowed_file_extensions", "widerruf_internal_notify_email")
    def _check_withdrawal_settings(self):
        for rec in self:
            if not 1 <= rec.widerruf_max_upload_size_mb <= 10:
                raise ValidationError(_("Upload size must be between 1 and 10 MB."))
            if not 0 <= rec.widerruf_activity_deadline_days <= 365:
                raise ValidationError(_("Activity deadline must be between 0 and 365 days."))
            extensions = set((rec.widerruf_allowed_file_extensions or "").lower().replace(" ", "").split(","))
            if not extensions or not extensions <= {"pdf", "jpg", "jpeg", "png"}:
                raise ValidationError(_("Allowed extensions are pdf, jpg, jpeg and png only."))
            if rec.widerruf_internal_notify_email and not single_email(rec.widerruf_internal_notify_email):
                raise ValidationError(_("Please enter one valid email address."))
