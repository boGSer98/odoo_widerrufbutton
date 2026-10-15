# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    widerruf_ids = fields.One2many(
        "widerruf.record",
        "sale_order_id",
        string="Zugehoerige Widerrufe",
        readonly=True,
    )
    widerruf_count = fields.Integer(
        string="Widerrufe",
        compute="_compute_widerruf_count",
    )

    @api.depends("widerruf_ids")
    def _compute_widerruf_count(self):
        grouped_data = self.env["widerruf.record"].sudo().read_group(
            [("sale_order_id", "in", self.ids)],
            ["sale_order_id"],
            ["sale_order_id"],
        )
        mapped_counts = {
            item["sale_order_id"][0]: item["sale_order_id_count"]
            for item in grouped_data
            if item.get("sale_order_id")
        }
        for order in self:
            order.widerruf_count = mapped_counts.get(order.id, 0)

    def action_view_widerrufe(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "odoo_widerrufbutton.action_widerruf_record"
        )
        action.update({
            "name": "Widerrufe",
            "domain": [("sale_order_id", "=", self.id)],
            "context": {
                "default_sale_order_id": self.id,
                "default_partner_id": self.partner_id.commercial_partner_id.id,
                "default_customer_name": self.partner_id.name,
                "default_customer_email": self.partner_id.email,
                "default_order_reference": self.name,
            },
        })
        if self.widerruf_count == 1:
            widerruf = self.widerruf_ids[:1]
            action.update({
                "views": [(False, "form")],
                "res_id": widerruf.id,
            })
        return action
