"""Bounded input validation shared by HTTP and ORM entrypoints."""
from odoo.tools import email_normalize

LIMITS = {"customer_name": 200, "customer_email": 254, "order_reference": 128,
          "withdrawal_type": 16, "message": 10000, "website_url": 256}
TYPES = ("full", "partial", "message")

def single_email(value):
    if not isinstance(value, str) or len(value) > 254 or (any(c in value for c in "\r\n,;") or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        return False
    return email_normalize(value.strip(), strict=True) or False

def validate_values(post, translate=None):
    _ = translate or str
    values = {key: "" for key in LIMITS}
    errors = {}
    if not isinstance(post, dict):
        return values, {"form": _("Invalid form data. Please check your entries.")}
    for key, limit in LIMITS.items():
        value = post.get(key, "full" if key == "withdrawal_type" else "")
        if not isinstance(value, str) or len(value) > limit:
            errors[key] = _("Invalid value or maximum length exceeded.")
            continue
        values[key] = value.strip()
    for key in ("customer_name", "order_reference"):
        if not values[key] or any(ord(c) < 32 for c in values[key]):
            errors[key] = _("Please complete this field with a valid value.")
    email = single_email(values["customer_email"])
    if not email:
        errors["customer_email"] = _("Please enter one valid email address.")
    else:
        values["customer_email"] = email
    if values["withdrawal_type"] not in TYPES:
        errors["withdrawal_type"] = _("Please select a valid withdrawal type.")
    if values["website_url"]:
        errors["website_url"] = _("The request could not be processed.")
    return values, errors
