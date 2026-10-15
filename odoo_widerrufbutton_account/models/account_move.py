from odoo import api, fields, models, _
from odoo.exceptions import AccessError

class AccountMove(models.Model):
    _inherit = "account.move"

    widerruf_ids = fields.One2many("widerruf.record", "invoice_id", string="Withdrawals", readonly=True,
                                  groups="odoo_widerrufbutton.group_widerruf_user,base.group_system")
    widerruf_count = fields.Integer(string="Withdrawals", compute="_compute_widerruf_count", compute_sudo=False)

    def _withdrawal_document_domain(self):
        self.ensure_one()
        domain = [("company_id", "=", self.company_id.id)]
        orders = self.env["sale.order"].browse() if "sale.order" in self.env else False
        if "sale_order_id" in self.env["widerruf.record"]._fields and "sale_line_ids" in self.env["account.move.line"]._fields:
            try:
                orders = self.invoice_line_ids.sale_line_ids.order_id
            except AccessError:
                pass
        if orders:
            domain += ["|", ("invoice_id", "=", self.id), ("sale_order_id", "in", orders.ids)]
        else:
            domain += [("invoice_id", "=", self.id)]
        return domain

    @api.depends(lambda m: ["widerruf_ids"] + (["invoice_line_ids.sale_line_ids.order_id.widerruf_ids"]
                    if "sale.order" in m.env and "widerruf_ids" in m.env["sale.order"]._fields else []))
    @api.depends_context("uid", "company")
    def _compute_widerruf_count(self):
        Model = self.env["widerruf.record"]
        for move in self:
            try:
                move.widerruf_count = Model.search_count(move._withdrawal_document_domain()) if Model.has_access("read") else 0
            except AccessError:
                move.widerruf_count = 0

    def action_view_widerrufe(self):
        self.ensure_one()
        self.check_access("read")
        self.env["widerruf.record"].check_access("read")
        records = self.env["widerruf.record"].search(self._withdrawal_document_domain())
        action = {"type":"ir.actions.act_window", "name":_("Withdrawals"), "res_model":"widerruf.record",
                  "view_mode":"list,form", "domain":[("id","in",records.ids)],
                  "context":{"default_invoice_id":self.id,"default_customer_name":self.partner_id.name,
                             "default_customer_email":self.partner_id.email,"default_order_reference":self.name if self.name != '/' else self.ref}}
        if len(records)==1:action.update(view_mode="form",res_id=records.id)
        return action
