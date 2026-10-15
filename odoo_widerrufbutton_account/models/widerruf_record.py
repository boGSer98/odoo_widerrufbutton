# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class WiderrufRecord(models.Model):
    _inherit = "widerruf.record"

    invoice_id = fields.Many2one("account.move", check_company=True, string="Verknuepfte Rechnung", readonly=True, tracking=True)
    invoice_reference_found = fields.Boolean(string="Rechnung gefunden", readonly=True, tracking=True)
    invoice_email_matches = fields.Boolean(string="E-Mail passt zur Rechnung", compute="_compute_invoice_email_match_warning", store=True, readonly=True)
    invoice_email_mismatch_warning = fields.Char(string="Warnhinweis Rechnung", compute="_compute_invoice_email_match_warning", store=True, readonly=True)

    @api.depends("customer_email", "invoice_id.partner_id.email")
    def _compute_invoice_email_match_warning(self):
        for record in self:
            document_email = ""
            if record.invoice_id and record.invoice_id.partner_id.email:
                document_email = record.invoice_id.partner_id.email.strip().lower()
            customer_email = (record.customer_email or "").strip().lower()
            if document_email and customer_email:
                record.invoice_email_matches = document_email == customer_email
                record.invoice_email_mismatch_warning = False if record.invoice_email_matches else _("Die eingegebene E-Mail-Adresse weicht von der E-Mail-Adresse der verknuepften Rechnung ab.")
            else:
                record.invoice_email_matches = False
                record.invoice_email_mismatch_warning = False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._try_link_invoice(force=True)
        return records

    def write(self, vals):
        result = super().write(vals)
        if "order_reference" in vals:
            self._try_link_invoice(force=True)
        return result

    def _get_clean_order_reference(self):
        self.ensure_one()
        return (self.order_reference or "").strip()

    def _find_invoice(self):
        self.ensure_one()
        reference = self._get_clean_order_reference()
        Model = self.env["account.move"].sudo()
        if not reference:
            return Model.browse()
        domain = [("company_id", "=", self.company_id.id)]
        domain += [("move_type", "in", ["out_invoice", "out_refund"])]
        domain += ["|", "|", ('name', '=', reference), ('payment_reference', '=', reference), ('ref', '=', reference)]
        matches = Model.search(domain, limit=2)
        return matches if len(matches) == 1 else Model.browse()

    def _try_link_invoice(self, force=False):
        for record in self:
            if record.invoice_id and not force:
                continue
            if not record.order_reference:
                continue
            invoice = record._find_invoice()
            if invoice:
                values = {"invoice_id": invoice.id, "invoice_reference_found": True}
                record.sudo().write(values)
                record.message_post(body=_("Der Widerruf wurde mit der Rechnung %s verknuepft.") % invoice.name)
            elif force:
                record.sudo().write({"invoice_id": False, "invoice_reference_found": False})

    def action_try_link_invoice(self):
        self.check_access("write")
        self._try_link_invoice(force=True)
