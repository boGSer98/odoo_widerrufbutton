"""Optional document integrations without imposing Sales or Accounting on the base."""
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class WithdrawalDocumentWorkflow(models.Model):
    _inherit = "widerruf.record"

    documents_manually_assigned = fields.Boolean(string="Manual document assignment", readonly=True, copy=False, tracking=True)
    document_assignment_available = fields.Boolean(compute="_compute_document_assignment_available")

    @api.depends_context("uid")
    def _compute_document_assignment_available(self):
        available = bool(self.env["widerruf.document.assignment"]._document_types())
        for rec in self:
            rec.document_assignment_available = available

    @api.model_create_multi
    def create(self, vals_list):
        return super().create([dict(vals, documents_manually_assigned=False) for vals in vals_list])

    def write(self, vals):
        if "documents_manually_assigned" in vals:
            raise AccessError(_("Document assignment origin cannot be edited directly."))
        return super().write(vals)

    def _set_manual_document_assignment(self, manual):
        return super(WithdrawalDocumentWorkflow, self).write({"documents_manually_assigned": bool(manual)})

    def _document_link_fields(self):
        return []

    def _match_documents(self):
        """Cooperative hooks implemented by optional integrations."""
        return None

    def _validate_selected_document(self, document):
        self.ensure_one()
        self.check_access("write")
        document.ensure_one()
        document.check_access("read")
        if document.company_id != self.company_id:
            raise ValidationError(_("The document must belong to the same company as the withdrawal."))

    def _visible_documents(self, documents):
        self.ensure_one()
        visible = documents.browse()
        for document in documents:
            try:
                document.check_access("read")
                if document.company_id == self.company_id:
                    visible |= document
            except AccessError:
                continue
        return visible

    def _document_window_action(self, documents, title):
        self.ensure_one()
        self.check_access("read")
        documents = self._visible_documents(documents)
        if not documents:
            raise UserError(_("No linked document is available with your access rights."))
        action = {"type": "ir.actions.act_window", "name": title,
                  "res_model": documents._name, "view_mode": "list,form",
                  "domain": [("id", "in", documents.ids)], "target": "current"}
        if len(documents) == 1:
            action.update(view_mode="form", res_id=documents.id)
        return action

    def action_assign_document(self):
        self.ensure_one()
        self.check_access("write")
        types = self.env["widerruf.document.assignment"]._document_types()
        if not types:
            raise UserError(_("No document integration is available with your access rights."))
        return {"type": "ir.actions.act_window", "name": _("Assign document"),
                "res_model": "widerruf.document.assignment", "view_mode": "form", "target": "new",
                "context": {"default_widerruf_id": self.id, "default_document_type": types[0][0]}}

    def action_find_documents(self):
        self.check_access("write")
        self._match_documents()
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_clear_document_assignment(self):
        self.check_access("write")
        fields_to_clear = {name: False for name in self._document_link_fields()}
        if fields_to_clear:
            self.write(fields_to_clear)
        self._set_manual_document_assignment(False)
        return {"type": "ir.actions.client", "tag": "reload"}

class WithdrawalDocumentAssignment(models.TransientModel):
    _name = "widerruf.document.assignment"
    _description = "Assign a withdrawal to a document"

    widerruf_id = fields.Many2one("widerruf.record", string="Withdrawal", required=True, readonly=True)
    company_id = fields.Many2one(related="widerruf_id.company_id", readonly=True)
    document_type = fields.Selection(selection="_document_types", string="Document type", required=True)

    def _document_types(self):
        return []

    def _selected_document_values(self):
        return {}

    def action_assign(self):
        self.ensure_one()
        self.check_access("read")
        rec = self.widerruf_id
        rec.check_access("write")
        selected = self._selected_document_values()
        if not selected:
            raise ValidationError(_("Select an offer, order or customer invoice."))
        values = {name: False for name in rec._document_link_fields()}
        values.update(selected)
        rec.write(values)
        rec._set_manual_document_assignment(True)
        rec.message_post(body=_("Document assignment was selected manually. No document was cancelled or refunded."))
        return {"type": "ir.actions.act_window_close"}
