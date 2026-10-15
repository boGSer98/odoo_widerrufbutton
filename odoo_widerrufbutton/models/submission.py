"""Short-lived, session-bound form revisions. Never accessible via public RPC."""
import hashlib
from odoo import fields, models

class WiderrufSubmission(models.TransientModel):
    _name = "widerruf.submission"
    _description = "Withdrawal form draft"
    _rec_name = "token_hash"
    _transient_max_hours = 1
    _transient_max_count = 2000

    token_hash = fields.Char(string="Token hash", required=True, index=True)
    session_hash = fields.Char(string="Session hash", required=True, index=True)
    ip_hash = fields.Char(string="IP hash", required=True, index=True)
    website_id = fields.Many2one("website", required=True, ondelete="cascade")
    upload_bytes = fields.Integer(string="Upload bytes", default=0)
    values_json = fields.Json(string="Form values", required=True)
    record_id = fields.Many2one("widerruf.record", ondelete="cascade")
    _token_unique = models.Constraint("UNIQUE(token_hash)", "The form token must be unique.")

    def unlink(self):
        # Remove temporary files on vacuum; confirmed files are reparented first.
        files = self.env["ir.attachment"].sudo().search([
            ("res_model", "=", self._name), ("res_id", "in", self.ids)])
        result = super().unlink()
        files.unlink()
        return result
