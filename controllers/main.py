# -*- coding: utf-8 -*-

import base64
import json

from odoo import http
from odoo.http import request


class WebsiteWiderrufController(http.Controller):
    """Public website routes for the electronic withdrawal function."""

    def _get_param(self, key, default=False):
        return request.env["ir.config_parameter"].sudo().get_param(key, default)

    def _get_withdrawal_types(self):
        return [
            ("full", "Vollständiger Widerruf"),
            ("partial", "Teilweiser Widerruf"),
            ("message", "Sonstige Mitteilung"),
        ]

    def _get_current_portal_partner(self):
        if request.env.user and not request.env.user._is_public():
            return request.env.user.partner_id.commercial_partner_id
        return request.env["res.partner"]

    def _get_default_form_values(self):
        partner = self._get_current_portal_partner()
        if partner:
            return {
                "customer_name": partner.name or "",
                "customer_email": partner.email or "",
            }
        return {}

    def _get_common_render_values(self):
        return {
            "withdrawal_types": self._get_withdrawal_types(),
            "intro_text": self._get_param("odoo_widerrufbutton.customer_intro_text", "Füllen Sie die folgenden Angaben aus. Im nächsten Schritt können Sie Ihre Eingaben prüfen und den Widerruf ausdrücklich bestätigen."),
        }

    def _validate_form_values(self, post):
        values = {
            "customer_name": (post.get("customer_name") or "").strip(),
            "customer_email": (post.get("customer_email") or "").strip(),
            "order_reference": (post.get("order_reference") or "").strip(),
            "withdrawal_type": (post.get("withdrawal_type") or "full").strip(),
            "message": (post.get("message") or "").strip(),
            "website_url": (post.get("website_url") or "").strip(),
        }
        errors = {}

        if values["website_url"]:
            errors["website_url"] = "Die Anfrage konnte nicht verarbeitet werden."
        if not values["customer_name"]:
            errors["customer_name"] = "Bitte geben Sie Ihren Namen ein."
        if not values["customer_email"]:
            errors["customer_email"] = "Bitte geben Sie Ihre E-Mail-Adresse ein."
        elif "@" not in values["customer_email"]:
            errors["customer_email"] = "Bitte geben Sie eine gültige E-Mail-Adresse ein."
        if not values["order_reference"]:
            errors["order_reference"] = "Bitte geben Sie Ihre Bestell- oder Rechnungsnummer ein."
        if values["withdrawal_type"] not in dict(self._get_withdrawal_types()):
            errors["withdrawal_type"] = "Bitte wählen Sie eine gültige Art des Widerrufs aus."

        return values, errors

    def _encode_payload(self, values):
        payload_values = dict(values)
        payload_values.pop("website_url", None)
        raw_payload = json.dumps(payload_values, ensure_ascii=False).encode("utf-8")
        return base64.urlsafe_b64encode(raw_payload).decode("ascii")

    def _decode_payload(self, payload):
        try:
            raw_payload = base64.urlsafe_b64decode(payload.encode("ascii"))
            return json.loads(raw_payload.decode("utf-8"))
        except Exception:
            return {}

    @http.route(["/widerruf", "/vertrag-widerrufen"], type="http", auth="public", website=True, sitemap=True, methods=["GET"])
    def widerruf_page(self, **kwargs):
        values = {
            "page_name": "widerrufbutton",
            "form_values": self._get_default_form_values(),
            "errors": {},
        }
        values.update(self._get_common_render_values())
        return request.render("odoo_widerrufbutton.widerruf_page", values)

    @http.route("/widerruf/pruefen", type="http", auth="public", website=True, sitemap=False, methods=["POST"])
    def widerruf_review(self, **post):
        form_values, errors = self._validate_form_values(post)

        if errors:
            values = {
                "page_name": "widerrufbutton",
                "form_values": form_values,
                "errors": errors,
            }
            values.update(self._get_common_render_values())
            return request.render("odoo_widerrufbutton.widerruf_page", values)

        review_values = dict(form_values)
        review_values.pop("website_url", None)

        payload = self._encode_payload(review_values)
        values = {
            "page_name": "widerrufbutton_review",
            "form_values": form_values,
            "withdrawal_type_label": dict(self._get_withdrawal_types()).get(form_values["withdrawal_type"]),
            "payload": payload,
        }
        values.update(self._get_common_render_values())
        return request.render("odoo_widerrufbutton.widerruf_review_page", values)

    @http.route("/widerruf/bestaetigen", type="http", auth="public", website=True, sitemap=False, methods=["POST"])
    def widerruf_confirm(self, **post):
        payload_values = self._decode_payload(post.get("payload") or "")
        form_values, errors = self._validate_form_values(payload_values)
        if errors:
            return request.redirect("/widerruf")

        partner = self._get_current_portal_partner()
        record = request.env["widerruf.record"].sudo().create({
            "customer_name": form_values["customer_name"],
            "customer_email": form_values["customer_email"],
            "order_reference": form_values["order_reference"],
            "withdrawal_type": form_values["withdrawal_type"],
            "message": form_values["message"],
            "website_id": request.website.id if request.website else False,
            "partner_id": partner.id if partner else False,
        })
        record.action_send_confirmation_mail()

        return request.render("odoo_widerrufbutton.widerruf_success_page", {"page_name": "widerrufbutton_success", "record": record})
