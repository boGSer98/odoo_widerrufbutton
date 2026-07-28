# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import api, fields, models, _


class WiderrufRecord(models.Model):
    _name = "widerruf.record"
    _description = "Widerruf"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(string="Vorgangsnummer", required=True, copy=False, readonly=True, default=lambda self: _("Neu"), tracking=True)
    customer_name = fields.Char(string="Name", required=True, tracking=True)
    customer_email = fields.Char(string="E-Mail", required=True, tracking=True)
    order_reference = fields.Char(string="Bestell- oder Rechnungsnummer", required=True, tracking=True)
    partner_id = fields.Many2one("res.partner", string="Kundenkonto", readonly=True, tracking=True)
    withdrawal_type = fields.Selection([
        ("full", "Vollständiger Widerruf"),
        ("partial", "Teilweiser Widerruf"),
        ("message", "Sonstige Mitteilung"),
    ], string="Art des Widerrufs", default="full", required=True, tracking=True)
    message = fields.Text(string="Mitteilung")
    state = fields.Selection([
        ("confirmed", "Bestätigt"),
        ("in_progress", "In Bearbeitung"),
        ("done", "Erledigt"),
        ("cancelled", "Abgebrochen"),
    ], string="Status", default="confirmed", required=True, tracking=True)
    website_id = fields.Many2one("website", string="Website", readonly=True)
    company_id = fields.Many2one("res.company", string="Unternehmen", default=lambda self: self.env.company, readonly=True)
    attachment_ids = fields.Many2many("ir.attachment", "widerruf_record_ir_attachment_rel", "widerruf_id", "attachment_id", string="Anhänge", readonly=True)
    attachment_count = fields.Integer(string="Anzahl Anhänge", compute="_compute_attachment_count", store=True)
    confirmation_mail_sent = fields.Boolean(string="E-Mail versendet", readonly=True)
    confirmation_mail_sent_at = fields.Datetime(string="E-Mail versendet am", readonly=True)
    internal_mail_sent = fields.Boolean(string="Interne E-Mail versendet", readonly=True)
    internal_mail_sent_at = fields.Datetime(string="Interne E-Mail versendet am", readonly=True)
    customer_status_mail_sent_at = fields.Datetime(string="Letzte Status-E-Mail an Kunden", readonly=True)

    @api.depends("attachment_ids")
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = len(record.attachment_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("Neu")) == _("Neu"):
                vals["name"] = self.env["ir.sequence"].next_by_code("widerruf.record") or _("Neu")
        records = super().create(vals_list)
        for record in records:
            record._create_initial_activity()
            record._send_internal_notification_mail()
        return records

    def write(self, vals):
        old_states = {record.id: record.state for record in self}
        result = super().write(vals)
        if "state" in vals:
            for record in self:
                if old_states.get(record.id) != record.state:
                    record._send_customer_status_mail()
        return result

    def _get_config_bool(self, key, default=True):
        value = self.env["ir.config_parameter"].sudo().get_str(key)
        if value in (None, False):
            return default
        return value in ("True", "true", "1", True)

    def _get_config_int(self, key, default=False):
        value = self.env["ir.config_parameter"].sudo().get_str(key)
        try:
            return int(value) if value else default
        except (TypeError, ValueError):
            return default

    def _create_initial_activity(self):
        if not self._get_config_bool("odoo_widerrufbutton.create_activity", default=True):
            return
        activity_type = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        if not activity_type:
            return
        configured_user_id = self._get_config_int("odoo_widerrufbutton.activity_user_id")
        fallback_user = self.env.ref("base.user_admin", raise_if_not_found=False) or self.env.user
        deadline_days = self._get_config_int("odoo_widerrufbutton.activity_deadline_days", default=1) or 0
        deadline_date = fields.Date.context_today(self) + timedelta(days=deadline_days)
        for record in self:
            note = _("Bitte prüfen Sie den Widerruf %s und bearbeiten Sie den Vorgang.") % record.name
            if record.attachment_count:
                note += _("\n\nDer Widerruf enthält %s Anhang/Anhänge.") % record.attachment_count
            record.activity_schedule(activity_type_id=activity_type.id, user_id=configured_user_id or fallback_user.id, date_deadline=deadline_date, summary=_("Neuen Widerruf prüfen"), note=note)

    def _send_internal_notification_mail(self):
        if not self._get_config_bool("odoo_widerrufbutton.send_internal_mail", default=True):
            return
        template = self.env.ref("odoo_widerrufbutton.mail_template_widerruf_internal_notification", raise_if_not_found=False)
        notify_email = self.env["ir.config_parameter"].sudo().get_str("odoo_widerrufbutton.internal_notify_email")
        for record in self:
            if template and notify_email:
                template.sudo().with_context(widerruf_internal_notify_email=notify_email).send_mail(record.id, force_send=True)
                record.sudo().write({"internal_mail_sent": True, "internal_mail_sent_at": fields.Datetime.now()})

    def _send_customer_status_mail(self):
        if not self._get_config_bool("odoo_widerrufbutton.send_customer_status_mail", default=True):
            return
        template = self.env.ref("odoo_widerrufbutton.mail_template_widerruf_status_update", raise_if_not_found=False)
        for record in self:
            if template and record.customer_email:
                template.sudo().send_mail(record.id, force_send=True)
                record.sudo().write({"customer_status_mail_sent_at": fields.Datetime.now()})

    def action_set_in_progress(self):
        self.write({"state": "in_progress"})

    def action_set_done(self):
        self.write({"state": "done"})

    def action_set_cancelled(self):
        self.write({"state": "cancelled"})

    def action_send_confirmation_mail(self):
        template = self.env.ref("odoo_widerrufbutton.mail_template_widerruf_confirmation", raise_if_not_found=False)
        for record in self:
            if template and record.customer_email:
                template.sudo().send_mail(record.id, force_send=True)
                record.sudo().write({"confirmation_mail_sent": True, "confirmation_mail_sent_at": fields.Datetime.now()})
