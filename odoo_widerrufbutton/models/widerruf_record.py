"""Withdrawal intake, immutable receipt snapshot and truthful queued mail status."""
import logging
from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError
from ..validation import validate_values, single_email

_logger = logging.getLogger(__name__)

class WiderrufRecord(models.Model):
    _name = "widerruf.record"
    _description = "Withdrawal"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"
    _check_company_auto = True

    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, default="/")
    customer_name = fields.Char(string="Name", required=True, tracking=True)
    customer_email = fields.Char(string="Email", required=True, tracking=True)
    order_reference = fields.Char(string="Order or invoice reference", required=True, tracking=True)
    partner_id = fields.Many2one("res.partner", string="Verified customer account", readonly=True, tracking=True)
    withdrawal_type = fields.Selection([("full", "Full withdrawal"), ("partial", "Partial withdrawal"),
                                       ("message", "Other message")], string="Withdrawal type", default="full", required=True, tracking=True)
    message = fields.Text(string="Message", tracking=True)
    state = fields.Selection([("confirmed", "Received"), ("in_progress", "In progress"),
                              ("done", "Done"), ("cancelled", "Closed without action")],
                             string="Status", default="confirmed", required=True, tracking=True)
    website_id = fields.Many2one("website", string="Website", readonly=True)
    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 default=lambda self: self.env.company, readonly=True, index=True)
    attachment_ids = fields.Many2many("ir.attachment", "widerruf_record_ir_attachment_rel", "widerruf_id", "attachment_id", string="Attachments", readonly=True)
    attachment_count = fields.Integer(string="Attachment count", compute="_compute_attachment_count", store=True)
    original_submission = fields.Json(string="Original receipt snapshot", readonly=True, copy=False)
    received_at = fields.Datetime(string="Received at", default=fields.Datetime.now, readonly=True, copy=False)
    submission_key = fields.Char(readonly=True, copy=False, index=True, groups="base.group_system")
    _submission_unique = models.Constraint("UNIQUE(submission_key)", "This submission has already been received.")

    confirmation_mail_id = fields.Many2one("mail.mail", string="Confirmation email", readonly=True, ondelete="set null", copy=False)
    internal_mail_id = fields.Many2one("mail.mail", string="Internal notification", readonly=True, ondelete="set null", copy=False)
    customer_status_mail_id = fields.Many2one("mail.mail", string="Latest status email", readonly=True, ondelete="set null", copy=False)
    confirmation_mail_state = fields.Char(string="Confirmation delivery status", compute="_compute_delivery", store=True)
    confirmation_mail_sent = fields.Boolean(string="Email sent", compute="_compute_delivery", store=True)
    confirmation_mail_sent_at = fields.Datetime(string="Email sent at", compute="_compute_delivery", store=True)
    internal_mail_sent = fields.Boolean(string="Internal email sent", compute="_compute_delivery", store=True)
    internal_mail_sent_at = fields.Datetime(string="Internal email sent at", compute="_compute_delivery", store=True)
    customer_status_mail_sent_at = fields.Datetime(string="Latest status email sent at", compute="_compute_delivery", store=True)
    mail_error = fields.Char(string="Email preparation error", readonly=True, copy=False)
    legacy_delivery_evidence = fields.Json(string="Legacy delivery evidence", readonly=True, copy=False)
    legacy_confirmation_mail_sent = fields.Boolean(string="Legacy unverified sent flag", readonly=True, copy=False)
    legacy_confirmation_mail_sent_at = fields.Datetime(string="Legacy unverified sent timestamp", readonly=True, copy=False)

    @api.depends("attachment_ids")
    def _compute_attachment_count(self):
        for rec in self:
            rec.attachment_count = len(rec.attachment_ids)

    @api.depends("confirmation_mail_id.state", "confirmation_mail_id.write_date",
                 "internal_mail_id.state", "internal_mail_id.write_date",
                 "customer_status_mail_id.state", "customer_status_mail_id.write_date")
    def _compute_delivery(self):
        for rec in self:
            confirmation = rec.confirmation_mail_id.sudo()
            internal = rec.internal_mail_id.sudo()
            status = rec.customer_status_mail_id.sudo()
            rec.confirmation_mail_state = confirmation.state or "not_created"
            rec.confirmation_mail_sent = confirmation.state == "sent"
            rec.confirmation_mail_sent_at = confirmation.write_date if confirmation.state == "sent" else False
            rec.internal_mail_sent = internal.state == "sent"
            rec.internal_mail_sent_at = internal.write_date if internal.state == "sent" else False
            rec.customer_status_mail_sent_at = status.write_date if status.state == "sent" else False

    @api.model_create_multi
    def create(self, vals_list):
        prepared = []
        for vals in vals_list:
            vals = dict(vals)
            clean, errors = validate_values({k: vals.get(k, "full" if k == "withdrawal_type" else "")
                                            for k in ("customer_name", "customer_email", "order_reference", "withdrawal_type", "message")}, translate=self.env._)
            if errors:
                raise ValidationError(_("Invalid withdrawal data: %s") % "; ".join(errors.values()))
            vals.update({k: clean[k] for k in ("customer_name", "customer_email", "order_reference", "withdrawal_type", "message")})
            for key in self._protected_delivery_fields():
                vals.pop(key, None)
            if vals.get("name", "/") in ("/", "Neu", "New"):
                vals["name"] = self.env["ir.sequence"].next_by_code("widerruf.record") or "/"
            vals["original_submission"] = {k: clean[k] for k in ("customer_name", "customer_email", "order_reference", "withdrawal_type", "message")}
            vals["original_submission"]["source"] = "website" if vals.get("submission_key") else "backend"
            vals["received_at"] = fields.Datetime.now()
            prepared.append(vals)
        records = super().create(prepared)
        for rec in records:
            rec._create_initial_activity()
            rec._send_internal_notification_mail()
        return records

    def _protected_delivery_fields(self):
        return {"confirmation_mail_id", "internal_mail_id", "customer_status_mail_id", "mail_error",
                "confirmation_mail_sent", "confirmation_mail_sent_at", "internal_mail_sent", "internal_mail_sent_at",
                "customer_status_mail_sent_at", "legacy_confirmation_mail_sent", "legacy_confirmation_mail_sent_at", "legacy_delivery_evidence"}

    def write(self, vals):
        protected = self._protected_delivery_fields() | {"original_submission", "received_at", "submission_key", "company_id", "website_id", "partner_id", "attachment_ids"}
        if protected.intersection(vals):
            raise AccessError(_("Receipt identity and delivery evidence cannot be edited directly."))
        for rec in self:
            check = {k: vals.get(k, rec[k] or "") for k in ("customer_name", "customer_email", "order_reference", "withdrawal_type", "message")}
            validated, errors = validate_values(check, translate=self.env._)
            if errors:
                raise ValidationError(_("Invalid withdrawal data: %s") % "; ".join(errors.values()))
        if "customer_email" in vals:
            vals = dict(vals, customer_email=single_email(vals["customer_email"]))
        previous = {rec.id: rec.state for rec in self}
        result = super().write(vals)
        if "state" in vals:
            for rec in self:
                if previous[rec.id] != rec.state:
                    rec._send_customer_status_mail()
        return result

    def _bind_inbound_attachments(self, files):
        self.ensure_one()
        if any(f.res_model != self._name or f.res_id != self.id for f in files):
            raise AccessError(_("Attachments must belong to this receipt."))
        snapshot = dict(self.original_submission or {})
        snapshot["attachments"] = [{"name": f.name, "checksum": f.checksum} for f in files]
        return super(WiderrufRecord, self.sudo()).write({
            "attachment_ids": [(6, 0, files.ids)], "original_submission": snapshot})

    def _set_delivery(self, values):
        return super(WiderrufRecord, self.sudo()).write(values)

    def _get_config_bool(self, key, default=True):
        value = self.env["ir.config_parameter"].sudo().get_param(key)
        return default if value in (None, False) else value in ("True", "true", "1", True)

    def _get_config_int(self, key, default=False):
        value = self.env["ir.config_parameter"].sudo().get_param(key)
        try:
            return int(value) if value else default
        except (TypeError, ValueError):
            return default

    def _create_initial_activity(self):
        if not self._get_config_bool("odoo_widerrufbutton.create_activity"):
            return
        activity_type = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        user = self.env["res.users"].sudo().browse(self._get_config_int("odoo_widerrufbutton.activity_user_id")).exists()
        user = user.filtered(lambda u: u.active and not u.share) or self.env.ref("base.user_admin")
        days = max(0, min(365, self._get_config_int("odoo_widerrufbutton.activity_deadline_days", 1)))
        if activity_type:
            for rec in self:
                try:
                    with self.env.cr.savepoint():
                        rec.with_context(mail_notify_force_send=False).activity_schedule(activity_type_id=activity_type.id, user_id=user.id,
                            date_deadline=fields.Date.context_today(rec) + timedelta(days=days),
                            summary=_("Review new withdrawal"), note=_("Please review the received declaration."))
                except Exception as exc:
                    _logger.warning("Withdrawal activity preparation failed (%s)", type(exc).__name__)

    def _queue_mail(self, template_xmlid, link_field, recipient, context=None):
        self.ensure_one()
        recipient = single_email(recipient)
        if not recipient:
            return False
        existing = self[link_field].sudo()
        if existing and existing.state == "outgoing":
            return existing
        try:
            with self.env.cr.savepoint():
                template = self.env.ref(template_xmlid)
                lang = self.partner_id.lang or self.env.context.get("lang") or "de_DE"
                mail_id = template.sudo().with_context(lang=lang, **(context or {})).send_mail(
                    self.id, force_send=False,
                    email_values={"email_to": recipient, "recipient_ids": [(5, 0, 0)]})
                if not mail_id:
                    raise ValueError("No email was generated")
                mail = self.env["mail.mail"].sudo().browse(mail_id).exists()
                if not mail:
                    raise ValueError("Generated email does not exist")
                self._set_delivery({link_field: mail.id, "mail_error": False})
                return mail
        except Exception as exc:
            _logger.warning("Withdrawal email preparation failed (%s)", type(exc).__name__)
            self._set_delivery({"mail_error": _("Email could not be queued; please review the configuration.")})
            return False

    def _send_internal_notification_mail(self):
        if self._get_config_bool("odoo_widerrufbutton.send_internal_mail"):
            recipient = self.env["ir.config_parameter"].sudo().get_param("odoo_widerrufbutton.internal_notify_email")
            for rec in self:
                rec._queue_mail("odoo_widerrufbutton.mail_template_widerruf_internal_notification", "internal_mail_id", recipient,
                                {"widerruf_internal_notify_email": recipient})

    def _send_customer_status_mail(self):
        if self._get_config_bool("odoo_widerrufbutton.send_customer_status_mail"):
            for rec in self:
                rec._queue_mail("odoo_widerrufbutton.mail_template_widerruf_status_update", "customer_status_mail_id", rec.customer_email)

    def action_set_in_progress(self):
        self.check_access("write")
        self.write({"state": "in_progress"})

    def action_set_done(self):
        self.check_access("write")
        self.write({"state": "done"})

    def action_set_cancelled(self):
        self.check_access("write")
        self.write({"state": "cancelled"})

    def action_send_confirmation_mail(self):
        self.check_access("write")
        for rec in self:
            rec._queue_mail("odoo_widerrufbutton.mail_template_widerruf_confirmation", "confirmation_mail_id", rec.customer_email)
