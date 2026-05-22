# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class WiderrufRecord(models.Model):
    _inherit = "widerruf.record"

    sale_order_id = fields.Many2one(
        "sale.order",
        string="Verknüpfter Verkaufsauftrag",
        readonly=True,
        tracking=True,
    )
    sale_reference_found = fields.Boolean(
        string="Verkaufsauftrag gefunden",
        readonly=True,
        tracking=True,
    )
    sale_email_matches = fields.Boolean(
        string="E-Mail passt zum Verkaufsauftrag",
        compute="_compute_sale_email_match_warning",
        store=True,
        readonly=True,
    )
    sale_email_mismatch_warning = fields.Char(
        string="Warnhinweis Verkaufsauftrag",
        compute="_compute_sale_email_match_warning",
        store=True,
        readonly=True,
    )

    @api.depends("customer_email", "sale_order_id.partner_id.email")
    def _compute_sale_email_match_warning(self):
        for record in self:
            document_email = ""
            if record.sale_order_id and record.sale_order_id.partner_id.email:
                document_email = record.sale_order_id.partner_id.email.strip().lower()
            customer_email = (record.customer_email or "").strip().lower()
            if document_email and customer_email:
                record.sale_email_matches = document_email == customer_email
                record.sale_email_mismatch_warning = False if record.sale_email_matches else _(
                    "Die eingegebene E-Mail-Adresse weicht von der E-Mail-Adresse des verknüpften Verkaufsauftrags ab."
                )
            else:
                record.sale_email_matches = False
                record.sale_email_mismatch_warning = False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._try_link_sale_order(force=True)
        return records

    def write(self, vals):
        result = super().write(vals)
        if "order_reference" in vals:
            self._try_link_sale_order(force=True)
        return result

    def _get_clean_order_reference(self):
        self.ensure_one()
        return (self.order_reference or "").strip()

    def _find_sale_order(self):
        self.ensure_one()
        reference = self._get_clean_order_reference()
        if not reference:
            return self.env["sale.order"]

        SaleOrder = self.env["sale.order"].sudo()
        domain_exact = [
            "|",
            ("name", "=", reference),
            ("client_order_ref", "=", reference),
        ]
        sale_order = SaleOrder.search(domain_exact, limit=1)
        if sale_order:
            return sale_order

        domain_case_insensitive = [
            "|",
            ("name", "ilike", reference),
            ("client_order_ref", "ilike", reference),
        ]
        return SaleOrder.search(domain_case_insensitive, limit=1)

    def _try_link_sale_order(self, force=False):
        for record in self:
            if record.sale_order_id and not force:
                continue
            if not record.order_reference:
                continue

            sale_order = record._find_sale_order()
            if sale_order:
                values = {
                    "sale_order_id": sale_order.id,
                    "sale_reference_found": True,
                }
                if not record.partner_id:
                    values["partner_id"] = sale_order.partner_id.commercial_partner_id.id
                record.sudo().write(values)
                record.message_post(
                    body=_("Der Widerruf wurde mit dem Verkaufsauftrag %s verknüpft.") % sale_order.name
                )
            elif force:
                record.sudo().write({
                    "sale_order_id": False,
                    "sale_reference_found": False,
                })

    def action_try_link_sale_order(self):
        self._try_link_sale_order(force=True)
