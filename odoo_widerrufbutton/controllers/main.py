"""Public withdrawal flow: bounded drafts, one-time receipt and queued delivery."""
import base64
import hashlib
import hmac
import io
import re
import secrets
from datetime import timedelta
from pathlib import PurePath
from PIL import Image, UnidentifiedImageError
from odoo import http, fields
from odoo.http import request
from ..validation import validate_values

MAX_BODY = 32 * 1024 * 1024
TOKEN = re.compile(r"[A-Za-z0-9_-]{43}\Z")

class WebsiteWiderrufController(http.Controller):
    def _get_param(self, key, default=False):
        return request.env["ir.config_parameter"].sudo().get_param("odoo_widerrufbutton." + key, default)

    def _get_withdrawal_types(self):
        return [("full", request.env._("Full withdrawal")), ("partial", request.env._("Partial withdrawal")), ("message", request.env._("Other message"))]

    def _get_current_portal_partner(self):
        return (request.env.user.partner_id.commercial_partner_id
                if not request.env.user._is_public() else request.env["res.partner"])

    def _binding_hash(self):
        if not request.session.get("widerruf_binding"):
            request.session["widerruf_binding"] = secrets.token_urlsafe(32)
        return hashlib.sha256(request.session["widerruf_binding"].encode()).hexdigest()

    def _ip_hash(self):
        secret = request.env["ir.config_parameter"].sudo().get_param("database.secret")
        if not secret:
            raise ValueError("Missing database secret")
        return hmac.new(secret.encode(), (request.httprequest.remote_addr or "unknown").encode(), hashlib.sha256).hexdigest()

    def _render(self, template, values, status=200):
        response = request.render("odoo_widerrufbutton." + template, values, status=status)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "same-origin"
        if status == 429:
            response.headers["Retry-After"] = "600"
        return response

    def _common(self, values=None, errors=None, draft="", files=None):
        self._binding_hash()
        intro = self._get_param("customer_intro_text")
        if not intro or intro in (
            "Complete your details. You can review and explicitly confirm your withdrawal in the next step.",
            "Füllen Sie die folgenden Angaben aus. Im nächsten Schritt können Sie Ihre Eingaben prüfen und den Widerruf ausdrücklich bestätigen."):
            intro = request.env._("Complete your details. You can review and explicitly confirm your withdrawal in the next step.")
        return {"page_name": "widerrufbutton", "form_values": values or {}, "errors": errors or {},
                "withdrawal_types": self._get_withdrawal_types(),
                "intro_text": intro,
                "draft": draft, "existing_files": files or [],
                "upload_enabled": self._get_param("upload_enabled", "True") in ("True", "true", "1", True)}

    def _submission(self, token, allow_confirmed=True):
        if not isinstance(token, str) or not TOKEN.fullmatch(token):
            return request.env["widerruf.submission"]
        sub = request.env["widerruf.submission"].sudo().search([
            ("token_hash", "=", hashlib.sha256(token.encode()).hexdigest()),
            ("session_hash", "=", self._binding_hash()), ("website_id", "=", request.website.id)], limit=1)
        if sub and ((sub.record_id and allow_confirmed) or sub.create_date >= fields.Datetime.now() - timedelta(minutes=20)):
            return sub
        return request.env["widerruf.submission"]

    def _draft_files(self, sub):
        return request.env["ir.attachment"].sudo().search([("res_model", "=", "widerruf.submission"), ("res_id", "=", sub.id)]) if sub else request.env["ir.attachment"]

    def _rate_limited(self):
        session_hash, ip_hash = self._binding_hash(), self._ip_hash()
        # Serialize count+insert across workers, without retaining plaintext IPs.
        for key in sorted([session_hash, ip_hash]):
            lock = int.from_bytes(bytes.fromhex(key)[:8], "big", signed=True)
            request.env.cr.execute("SELECT pg_advisory_xact_lock(%s)", [lock])
        Draft = request.env["widerruf.submission"].sudo()
        cutoff = fields.Datetime.now() - timedelta(minutes=10)
        return (Draft.search_count([("create_date", ">=", cutoff), ("session_hash", "=", session_hash)]) >= 5 or
                Draft.search_count([("create_date", ">=", cutoff), ("ip_hash", "=", ip_hash)]) >= 30)

    def _storage_limited(self, size):
        if not size:
            return False
        Draft = request.env["widerruf.submission"].sudo()
        recent = [("create_date", ">=", fields.Datetime.now() - timedelta(minutes=10))]
        for field, value, cap in [("session_hash", self._binding_hash(), 20), ("ip_hash", self._ip_hash(), 30)]:
            used = Draft._read_group(recent + [(field, "=", value)], aggregates=["upload_bytes:sum"])[0][0] or 0
            if used + size > cap * 1024 * 1024:
                return True
        return False

    def _upload_values(self):
        uploads = [f for f in request.httprequest.files.getlist("attachments") if f.filename]
        if uploads and self._get_param("upload_enabled", "True") not in ("True", "true", "1", True):
            raise ValueError(request.env._("File uploads are disabled."))
        if len(uploads) > 3:
            raise ValueError(request.env._("A maximum of three files is allowed."))
        try:
            limit = max(1, min(10, int(self._get_param("max_upload_size_mb", "10")))) * 1024 * 1024
        except (ValueError, TypeError):
            limit = 10 * 1024 * 1024
        allowed = set(str(self._get_param("allowed_file_extensions", "pdf,jpg,jpeg,png")).lower().replace(" ", "").split(",")) & {"pdf", "jpg", "jpeg", "png"}
        result = []
        total = 0
        for upload in uploads:
            filename = str(upload.filename).replace("\\", "/").split("/")[-1]
            if not filename or len(filename) > 150 or any(ord(c) < 32 or ord(c) == 127 for c in filename):
                raise ValueError(request.env._("Invalid attachment filename."))
            extension = PurePath(filename).suffix.lower().lstrip(".")
            data = upload.stream.read(limit + 1)
            total += len(data)
            if total > 10 * 1024 * 1024:
                raise ValueError(request.env._("Attachments may not exceed 10 MB in total."))
            if not data or len(data) > limit or extension not in allowed:
                raise ValueError(request.env._("Invalid file type or upload size exceeded."))
            if extension == "pdf":
                if not data.startswith(b"%PDF-") or b"%%EOF" not in data[-4096:]:
                    raise ValueError(request.env._("The file content does not match its extension."))
                mimetype = "application/pdf"
            else:
                try:
                    image = Image.open(io.BytesIO(data))
                    expected = "PNG" if extension == "png" else "JPEG"
                    if image.format != expected or image.width * image.height > 20000000:
                        raise ValueError("Image format or dimensions")
                    image.verify()
                except (ValueError, UnidentifiedImageError, OSError, Image.DecompressionBombError):
                    raise ValueError(request.env._("The file content does not match its extension.")) from None
                mimetype = "image/png" if extension == "png" else "image/jpeg"
            result.append({"name": filename, "datas": base64.b64encode(data), "mimetype": mimetype,
                           "type": "binary", "public": False})
        return result

    @http.route(["/widerruf", "/vertrag-widerrufen"], type="http", auth="public", website=True, sitemap=True, methods=["GET"])
    def widerruf_page(self, draft="", **kwargs):
        sub = self._submission(draft, allow_confirmed=False) if draft else False
        if sub and sub.record_id:
            sub = False
        values = dict(sub.values_json) if sub else {}
        if not values:
            partner = self._get_current_portal_partner()
            values = {"customer_name": partner.name or "", "customer_email": partner.email or ""} if partner else {}
        return self._render("widerruf_page", self._common(values, draft=draft if sub else "", files=self._draft_files(sub)))

    @http.route("/widerruf/pruefen", type="http", auth="public", website=True, sitemap=False, methods=["POST"], max_content_length=MAX_BODY)
    def widerruf_review(self, **post):
        values, errors = validate_values(post, translate=request.env._)
        previous = self._submission(post.get("draft"), allow_confirmed=False)
        files = self._draft_files(previous) if previous and not previous.record_id else request.env["ir.attachment"]
        if errors:
            return self._render("widerruf_page", self._common(values, errors, post.get("draft", ""), files), 400)
        try:
            with request.env.cr.savepoint():
                if self._rate_limited():
                    return self._render("widerruf_page", self._common(values, {"form": request.env._("Too many requests. Please try again later.")}), 429)
                uploads = self._upload_values()
                if len(files) + len(uploads) > 3:
                    raise ValueError(request.env._("A maximum of three files is allowed."))
                upload_bytes = sum(files.mapped("file_size")) + sum(len(base64.b64decode(v["datas"])) for v in uploads)
                if upload_bytes > 10 * 1024 * 1024:
                    raise ValueError(request.env._("Attachments may not exceed 10 MB in total."))
                if self._storage_limited(upload_bytes):
                    return self._render("widerruf_page", self._common(values, {"form": request.env._("Attachment upload limit reached. Please try without files or try again later.")}), 429)
                token = secrets.token_urlsafe(32)
                clean = {k: v for k, v in values.items() if k != "website_url"}
                clean["lang"] = request.env.lang or "de_DE"
                sub = request.env["widerruf.submission"].sudo().create({
                    "token_hash": hashlib.sha256(token.encode()).hexdigest(), "session_hash": self._binding_hash(),
                    "ip_hash": self._ip_hash(), "website_id": request.website.id, "values_json": clean, "upload_bytes": upload_bytes})
                for old in files:
                    old.copy({"res_model": sub._name, "res_id": sub.id, "public": False, "access_token": False})
                for vals in uploads:
                    request.env["ir.attachment"].sudo().create(dict(vals, res_model=sub._name, res_id=sub.id))
        except ValueError as exc:
            return self._render("widerruf_page", self._common(values, {"form": str(exc)}, post.get("draft", ""), files), 400)
        return self._render("widerruf_review_page", dict(self._common(values), payload=token,
            withdrawal_type_label=dict(self._get_withdrawal_types())[values["withdrawal_type"]],
            existing_files=self._draft_files(sub)))

    @http.route("/widerruf/bestaetigen", type="http", auth="public", website=True, sitemap=False, methods=["POST"], max_content_length=65536)
    def widerruf_confirm(self, **post):
        sub = self._submission(post.get("payload"))
        if not sub:
            return self._render("widerruf_page", self._common(errors={"form": request.env._("The form has expired or is invalid. Please enter your details again.")}), 400)
        request.env.cr.execute("SELECT id FROM widerruf_submission WHERE id=%s FOR UPDATE", [sub.id])
        sub.invalidate_recordset(["record_id"])
        if not sub.record_id:
            values, errors = validate_values(sub.values_json, translate=request.env._)
            if errors:
                return self._render("widerruf_page", self._common(errors=errors), 400)
            partner = self._get_current_portal_partner()
            rec = request.env["widerruf.record"].sudo().with_context(
                lang=sub.values_json.get("lang", "de_DE"), tracking_disable=True,
                mail_create_nosubscribe=True, mail_create_nolog=True).create({
                    **{k: values[k] for k in ("customer_name", "customer_email", "order_reference", "withdrawal_type", "message")},
                    "website_id": request.website.id, "company_id": request.website.company_id.id,
                    "partner_id": partner.id or False, "submission_key": sub.token_hash})
            files = self._draft_files(sub)
            files.write({"res_model": rec._name, "res_id": rec.id, "public": False, "access_token": False})
            rec._bind_inbound_attachments(files)
            sub.record_id = rec
            rec.action_send_confirmation_mail()
        return self._render("widerruf_success_page", {"page_name": "widerrufbutton_success", "record": sub.record_id})
