"""Offer / order matching and rights-aware native document navigation."""
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError

class WithdrawalDocumentLink(models.Model):
    _inherit = "widerruf.record"

    sale_order_id = fields.Many2one("sale.order", string="Linked offer / order", check_company=True, readonly=True, tracking=True, groups="sales_team.group_sale_salesman,account.group_account_invoice,account.group_account_readonly")
    sale_reference_found = fields.Boolean(string="Offer / order available", compute="_compute_sale_documents", compute_sudo=False)
    related_sale_order_ids = fields.Many2many("sale.order", compute="_compute_sale_relations", compute_sudo=False, groups="sales_team.group_sale_salesman,account.group_account_invoice,account.group_account_readonly", string="Offers / orders")
    sale_document_count = fields.Integer(compute="_compute_sale_documents", compute_sudo=False, string="Offers / orders")
    sale_email_matches = fields.Boolean(compute="_compute_sale_email_match_warning", compute_sudo=False, string="Document email matches")
    sale_email_mismatch_warning = fields.Char(compute="_compute_sale_email_match_warning", compute_sudo=False, string="Document email warning")

    def _document_link_fields(self):
        return super()._document_link_fields() + ["sale_order_id"]

    @api.depends(lambda m: ["sale_order_id"] + (["invoice_id.invoice_line_ids.sale_line_ids.order_id"] if "invoice_id" in m._fields else []))
    @api.depends_context("uid", "company")
    def _compute_sale_documents(self):
        for rec in self:
            documents = rec._related_sale_documents()
            rec.sale_document_count = len(documents)
            rec.sale_reference_found = bool(documents)

    @api.depends(lambda m: ["sale_order_id"] + (["invoice_id.invoice_line_ids.sale_line_ids.order_id"] if "invoice_id" in m._fields else []))
    @api.depends_context("uid", "company")
    def _compute_sale_relations(self):
        for rec in self:
            rec.related_sale_order_ids = rec._related_sale_documents()

    def _related_sale_documents(self):
        self.ensure_one()
        self.check_access("read")
        # Read private link IDs only after receipt access; reveal documents through native ACLs.
        candidates = self.sudo().sale_order_id.with_env(self.env)

        if "invoice_id" in self._fields and self.sudo().invoice_id:
            try:
                invoice = self.sudo().invoice_id.with_env(self.env)
                invoice.check_access("read")
                candidates |= invoice.invoice_line_ids.sale_line_ids.order_id
            except AccessError:
                pass

        return self._visible_documents(candidates)

    @api.depends("customer_email", "related_sale_order_ids.partner_id.email")
    def _compute_sale_email_match_warning(self):
        for rec in self:
            documents = rec._related_sale_documents()
            emails = {(d.partner_id.email or "").strip().lower() for d in documents}
            email = (rec.customer_email or "").strip().lower()
            rec.sale_email_matches = bool(email and email in emails)
            rec.sale_email_mismatch_warning = (_("The submitted email differs from the linked document. Please review the assignment.") if documents and not rec.sale_email_matches else False)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec, values in zip(records, vals_list):
            if values.get("sale_order_id"):
                rec._validate_selected_document(self.env["sale.order"].browse(values["sale_order_id"]))
            if any(values.get(name) for name in rec._document_link_fields()):
                rec._set_manual_document_assignment(True)
            else:
                rec._try_link_sale_document(force=True)
        return records

    def write(self, vals):
        if "sale_order_id" in vals and vals["sale_order_id"] and not self.env.su:
            for rec in self:
                rec._validate_selected_document(self.env["sale.order"].browse(vals["sale_order_id"]))
        result = super().write(vals)
        if "sale_order_id" in vals and not self.env.su:
            self._set_manual_document_assignment(True)
        if "order_reference" in vals:
            self._try_link_sale_document(force=True)
        return result

    def _find_sale_document(self):
        self.ensure_one()
        Model = self.env["sale.order"].sudo()
        reference = (self.order_reference or "").strip()
        if not reference or reference == "/":
            return Model.browse()
        domain = [("company_id", "=", self.company_id.id)]
        domain += ["|"] + [('name', '=', reference), ('client_order_ref', '=', reference)]
        matches = Model.search(domain, limit=2)
        return matches if len(matches) == 1 else Model.browse()

    def _try_link_sale_document(self, force=False):
        for rec in self:
            if rec.documents_manually_assigned:
                continue
            if rec.sudo().sale_order_id and not force:
                continue
            document = rec._find_sale_document()
            old = rec.sudo().sale_order_id
            if document != old:
                rec.sudo().write({"sale_order_id": document.id or False})
                if document:
                    rec.message_post(body=_("An exact same-company document match was linked automatically."))

    def _match_documents(self):
        super()._match_documents()
        self._try_link_sale_document(force=True)

    def action_open_sale_documents(self):
        self.ensure_one()
        return self._document_window_action(self._related_sale_documents(), _("Offers / orders"))

    def action_try_link_sale_order(self):
        return self.action_find_documents()

class DocumentAssignment(models.TransientModel):
    _inherit = "widerruf.document.assignment"

    sale_order_id = fields.Many2one("sale.order", string="Offer / order", groups="sales_team.group_sale_salesman,account.group_account_invoice,account.group_account_readonly")

    def _document_types(self):
        types = super()._document_types()
        if (self.env.su or any(self.env.user.has_group(g) for g in ['sales_team.group_sale_salesman', 'account.group_account_invoice', 'account.group_account_readonly'])) and self.env["sale.order"].has_access("read"):
            types += [("sale", _("Offer / order"))]
        return types

    def _selected_document_values(self):
        values = super()._selected_document_values()
        if self.document_type == "sale":
            if not self.sale_order_id:
                raise ValidationError(_("Please select a document."))
            self.widerruf_id._validate_selected_document(self.sale_order_id)
            values["sale_order_id"] = self.sale_order_id.id
        return values
