# -*- coding: utf-8 -*-

import base64

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class WiderrufCustomerPortal(CustomerPortal):
    """Customer portal pages for withdrawal records."""

    def _portal_enabled(self):
        value = request.env["ir.config_parameter"].sudo().get_param("odoo_widerrufbutton.show_portal", "True")
        return value in ("True", "true", "1", True)

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "widerruf_count" in counters:
            if not self._portal_enabled():
                values["widerruf_count"] = 0
            else:
                partner = request.env.user.partner_id.commercial_partner_id
                values["widerruf_count"] = request.env["widerruf.record"].sudo().search_count([
                    ("partner_id", "=", partner.id),
                ])
        return values

    def _get_portal_widerruf_domain(self):
        partner = request.env.user.partner_id.commercial_partner_id
        return [("partner_id", "=", partner.id)]

    def _get_portal_widerruf(self, widerruf_id):
        if not self._portal_enabled():
            return request.env["widerruf.record"]
        record = request.env["widerruf.record"].sudo().browse(widerruf_id)
        partner = request.env.user.partner_id.commercial_partner_id
        if not record.exists() or record.partner_id.id != partner.id:
            return request.env["widerruf.record"]
        return record

    @http.route(["/my/widerrufe", "/my/widerrufe/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_widerrufe(self, page=1, sortby="date", **kw):
        if not self._portal_enabled():
            return request.redirect("/my")

        values = self._prepare_portal_layout_values()
        WiderrufRecord = request.env["widerruf.record"].sudo()
        domain = self._get_portal_widerruf_domain()

        searchbar_sortings = {
            "date": {"label": _("Neueste zuerst"), "order": "create_date desc"},
            "name": {"label": _("Vorgangsnummer"), "order": "name desc"},
            "state": {"label": _("Status"), "order": "state asc, create_date desc"},
        }
        sortby = sortby if sortby in searchbar_sortings else "date"
        order = searchbar_sortings[sortby]["order"]

        total = WiderrufRecord.search_count(domain)
        pager = portal_pager(
            url="/my/widerrufe",
            url_args={"sortby": sortby},
            total=total,
            page=page,
            step=self._items_per_page,
        )
        records = WiderrufRecord.search(domain, order=order, limit=self._items_per_page, offset=pager["offset"])

        values.update({
            "widerrufe": records,
            "page_name": "widerrufe",
            "pager": pager,
            "default_url": "/my/widerrufe",
            "searchbar_sortings": searchbar_sortings,
            "sortby": sortby,
        })
        return request.render("odoo_widerrufbutton.portal_my_widerrufe", values)

    @http.route(["/my/widerrufe/<int:widerruf_id>"], type="http", auth="user", website=True)
    def portal_my_widerruf_detail(self, widerruf_id, **kw):
        record = self._get_portal_widerruf(widerruf_id)
        if not record:
            return request.redirect("/my")

        values = self._prepare_portal_layout_values()
        values.update({
            "widerruf": record,
            "page_name": "widerrufe",
        })
        return request.render("odoo_widerrufbutton.portal_my_widerruf_detail", values)

    @http.route(["/my/widerrufe/<int:widerruf_id>/attachment/<int:attachment_id>"], type="http", auth="user", website=True)
    def portal_my_widerruf_attachment(self, widerruf_id, attachment_id, **kw):
        record = self._get_portal_widerruf(widerruf_id)
        if not record:
            return request.redirect("/my")

        attachment = record.attachment_ids.filtered(lambda item: item.id == attachment_id)
        if not attachment:
            return request.redirect("/my/widerrufe/%s" % widerruf_id)

        attachment = attachment[0].sudo()
        filecontent = base64.b64decode(attachment.datas or b"")
        headers = [
            ("Content-Type", attachment.mimetype or "application/octet-stream"),
            ("Content-Disposition", "attachment; filename=\"%s\"" % attachment.name),
        ]
        return request.make_response(filecontent, headers)
