from odoo import api, fields, models, _
from odoo.exceptions import AccessError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    widerruf_ids = fields.One2many("widerruf.record", "sale_order_id", string="Withdrawals", readonly=True)
    widerruf_count = fields.Integer(string="Withdrawals", compute="_compute_widerruf_count", compute_sudo=False)

    def _withdrawal_document_domain(self):
        self.ensure_one()
        domain = [("company_id", "=", self.company_id.id)]
        if "invoice_id" in self.env["widerruf.record"]._fields:
            domain += ["|", ("sale_order_id", "=", self.id), ("invoice_id", "in", self.invoice_ids.ids)]
        else:
            domain += [("sale_order_id", "=", self.id)]
        return domain

    @api.depends(lambda m: ["widerruf_ids", "invoice_ids"] + (["invoice_ids.widerruf_ids"] if "widerruf_ids" in m.env["account.move"]._fields else []))
    @api.depends_context("uid", "company")
    def _compute_widerruf_count(self):
        Model = self.env["widerruf.record"]
        for order in self:
            try:
                order.widerruf_count = Model.search_count(order._withdrawal_document_domain()) if Model.has_access("read") else 0
            except AccessError:
                order.widerruf_count = 0

    def action_view_widerrufe(self):
        self.ensure_one()
        self.check_access("read")
        self.env["widerruf.record"].check_access("read")
        records = self.env["widerruf.record"].search(self._withdrawal_document_domain())
        action = {"type":"ir.actions.act_window", "name":_("Withdrawals"), "res_model":"widerruf.record",
                  "view_mode":"list,form", "domain":[("id","in",records.ids)],
                  "context":{"default_sale_order_id":self.id,"default_customer_name":self.partner_id.name,
                             "default_customer_email":self.partner_id.email,"default_order_reference":self.name}}
        if len(records)==1:
            action.update(view_mode="form",res_id=records.id)
        return action
