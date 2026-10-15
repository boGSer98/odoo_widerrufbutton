"""Customer invoice / credit note matching and rights-aware native document navigation."""
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError

class WithdrawalDocumentLink(models.Model):
    _inherit = "widerruf.record"

    invoice_id = fields.Many2one("account.move", string="Linked customer invoice / credit note", check_company=True, readonly=True, tracking=True, groups="account.group_account_invoice,account.group_account_readonly")
    invoice_reference_found = fields.Boolean(string="Customer invoice / credit note available", compute="_compute_invoice_documents", compute_sudo=False)
    related_invoice_ids = fields.Many2many("account.move", compute="_compute_invoice_relations", compute_sudo=False, groups="account.group_account_invoice,account.group_account_readonly", string="Invoices / credit notes")
    invoice_document_count = fields.Integer(compute="_compute_invoice_documents", compute_sudo=False, string="Invoices / credit notes")
    invoice_email_matches = fields.Boolean(compute="_compute_invoice_email_match_warning", compute_sudo=False, string="Document email matches")
    invoice_email_mismatch_warning = fields.Char(compute="_compute_invoice_email_match_warning", compute_sudo=False, string="Document email warning")

    def _validate_selected_document(self, document):
        super()._validate_selected_document(document)
        if document._name == "account.move" and document.move_type not in ("out_invoice", "out_refund"):
            raise ValidationError(_("Only customer invoices or credit notes can be assigned."))

    def _document_link_fields(self):
        return super()._document_link_fields() + ["invoice_id"]

    @api.depends(lambda m: ["invoice_id"] + (["sale_order_id.invoice_ids"] if "sale_order_id" in m._fields else []))
    @api.depends_context("uid", "company")
    def _compute_invoice_documents(self):
        for rec in self:
            documents = rec._related_invoice_documents()
            rec.invoice_document_count = len(documents)
            rec.invoice_reference_found = bool(documents)

    @api.depends(lambda m: ["invoice_id"] + (["sale_order_id.invoice_ids"] if "sale_order_id" in m._fields else []))
    @api.depends_context("uid", "company")
    def _compute_invoice_relations(self):
        for rec in self:
            rec.related_invoice_ids = rec._related_invoice_documents()

    def _related_invoice_documents(self):
        self.ensure_one()
        self.check_access("read")
        # Read private link IDs only after receipt access; reveal documents through native ACLs.
        candidates = self.sudo().invoice_id.with_env(self.env)

        if "sale_order_id" in self._fields and self.sudo().sale_order_id:
            try:
                order = self.sudo().sale_order_id.with_env(self.env)
                order.check_access("read")
                candidates |= order.invoice_ids
            except AccessError:
                pass

        return self._visible_documents(candidates)

    @api.depends("customer_email", "related_invoice_ids.partner_id.email")
    def _compute_invoice_email_match_warning(self):
        for rec in self:
            documents = rec._related_invoice_documents()
            emails = {(d.partner_id.email or "").strip().lower() for d in documents}
            email = (rec.customer_email or "").strip().lower()
            rec.invoice_email_matches = bool(email and email in emails)
            rec.invoice_email_mismatch_warning = (_("The submitted email differs from the linked document. Please review the assignment.") if documents and not rec.invoice_email_matches else False)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec, values in zip(records, vals_list):
            if values.get("invoice_id"):
                rec._validate_selected_document(self.env["account.move"].browse(values["invoice_id"]))
            if any(values.get(name) for name in rec._document_link_fields()):
                rec._set_manual_document_assignment(True)
            else:
                rec._try_link_invoice_document(force=True)
        return records

    def write(self, vals):
        if "invoice_id" in vals and vals["invoice_id"] and not self.env.su:
            for rec in self:
                rec._validate_selected_document(self.env["account.move"].browse(vals["invoice_id"]))
        result = super().write(vals)
        if "invoice_id" in vals and not self.env.su:
            self._set_manual_document_assignment(True)
        if "order_reference" in vals:
            self._try_link_invoice_document(force=True)
        return result

    def _find_invoice_document(self):
        self.ensure_one()
        Model = self.env["account.move"].sudo()
        reference = (self.order_reference or "").strip()
        if not reference or reference == "/":
            return Model.browse()
        domain = [("company_id", "=", self.company_id.id)]
        domain += [("move_type", "in", ["out_invoice", "out_refund"])]
        domain += ["|", "|"] + [('name', '=', reference), ('payment_reference', '=', reference), ('ref', '=', reference)]
        matches = Model.search(domain, limit=2)
        return matches if len(matches) == 1 else Model.browse()

    def _try_link_invoice_document(self, force=False):
        for rec in self:
            if rec.documents_manually_assigned:
                continue
            if rec.sudo().invoice_id and not force:
                continue
            document = rec._find_invoice_document()
            old = rec.sudo().invoice_id
            if document != old:
                rec.sudo().write({"invoice_id": document.id or False})
                if document:
                    rec.message_post(body=_("An exact same-company document match was linked automatically."))

    def _match_documents(self):
        super()._match_documents()
        self._try_link_invoice_document(force=True)

    def action_open_invoice_documents(self):
        self.ensure_one()
        return self._document_window_action(self._related_invoice_documents(), _("Invoices / credit notes"))

    def action_try_link_invoice(self):
        return self.action_find_documents()

class DocumentAssignment(models.TransientModel):
    _inherit = "widerruf.document.assignment"

    invoice_id = fields.Many2one("account.move", string="Customer invoice / credit note", groups="account.group_account_invoice,account.group_account_readonly")

    def _document_types(self):
        types = super()._document_types()
        if (self.env.su or any(self.env.user.has_group(g) for g in ['account.group_account_invoice', 'account.group_account_readonly'])) and self.env["account.move"].has_access("read"):
            types += [("invoice", _("Customer invoice / credit note"))]
        return types

    def _selected_document_values(self):
        values = super()._selected_document_values()
        if self.document_type == "invoice":
            if not self.invoice_id:
                raise ValidationError(_("Please select a document."))
            self.widerruf_id._validate_selected_document(self.invoice_id)
            if self.invoice_id.move_type not in ("out_invoice", "out_refund"):
                raise ValidationError(_("Only customer invoices or credit notes can be assigned."))
            values["invoice_id"] = self.invoice_id.id
        return values
