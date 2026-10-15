import json
from pathlib import Path
from lxml import etree, html
from odoo import api, SUPERUSER_ID

LEGACY_BODIES = {'mail_template_widerruf_confirmation': '<div style="font-family: Arial, sans-serif; font-size: 14px; color: #222;">\n                <p>Guten Tag <t t-out="object.customer_name" />,</p>\n                <p>wir bestätigen den Eingang Ihres Widerrufs. Nachfolgend finden Sie die von Ihnen übermittelten Angaben:</p>\n                <table style="border-collapse: collapse; width: 100%; max-width: 700px;" cellpadding="6">\n                    <tr><td style="border: 1px solid #ddd; font-weight: bold; width: 220px;">Vorgangsnummer</td><td style="border: 1px solid #ddd;"><t t-out="object.name" /></td></tr>\n                    <tr><td style="border: 1px solid #ddd; font-weight: bold;">Name</td><td style="border: 1px solid #ddd;"><t t-out="object.customer_name" /></td></tr>\n                    <tr><td style="border: 1px solid #ddd; font-weight: bold;">E-Mail</td><td style="border: 1px solid #ddd;"><t t-out="object.customer_email" /></td></tr>\n                    <tr><td style="border: 1px solid #ddd; font-weight: bold;">Bestell- oder Rechnungsnummer</td><td style="border: 1px solid #ddd;"><t t-out="object.order_reference" /></td></tr>\n                    <tr><td style="border: 1px solid #ddd; font-weight: bold;">Art des Widerrufs</td><td style="border: 1px solid #ddd;"><t t-out="dict(object._fields[\'withdrawal_type\'].selection).get(object.withdrawal_type)" /></td></tr>\n                    <tr><td style="border: 1px solid #ddd; font-weight: bold;">Mitteilung</td><td style="border: 1px solid #ddd;"><t t-out="object.message or \'-\'" /></td></tr>\n                </table>\n                <p style="margin-top: 20px;">Diese Nachricht bestätigt den technischen Eingang Ihrer Erklärung. Die weitere Bearbeitung erfolgt im Anschluss durch unser Team.</p>\n                <p>Mit freundlichen Grüßen</p>\n                <p><t t-out="user.company_id.name" /></p>\n            </div>\n        ', 'mail_template_widerruf_internal_notification': '<div style="font-family: Arial, sans-serif; font-size: 14px; color: #222;">\n                <p>Es wurde ein neuer Widerruf über die Website eingereicht.</p>\n                <table style="border-collapse: collapse; width: 100%; max-width: 700px;" cellpadding="6">\n                    <tr><td style="border: 1px solid #ddd; font-weight: bold; width: 220px;">Vorgangsnummer</td><td style="border: 1px solid #ddd;"><t t-out="object.name" /></td></tr>\n                    <tr><td style="border: 1px solid #ddd; font-weight: bold;">Name</td><td style="border: 1px solid #ddd;"><t t-out="object.customer_name" /></td></tr>\n                    <tr><td style="border: 1px solid #ddd; font-weight: bold;">E-Mail</td><td style="border: 1px solid #ddd;"><t t-out="object.customer_email" /></td></tr>\n                    <tr><td style="border: 1px solid #ddd; font-weight: bold;">Bestell- oder Rechnungsnummer</td><td style="border: 1px solid #ddd;"><t t-out="object.order_reference" /></td></tr>\n                    <tr><td style="border: 1px solid #ddd; font-weight: bold;">Status</td><td style="border: 1px solid #ddd;"><t t-out="dict(object._fields[\'state\'].selection).get(object.state)" /></td></tr>\n                </table>\n                <p style="margin-top: 20px;">Bitte öffnen Sie den Vorgang in Odoo und bearbeiten Sie den Widerruf.</p>\n            </div>\n        ', 'mail_template_widerruf_status_update': '<div style="font-family: Arial, sans-serif; font-size: 14px; color: #222;">\n                <p>Guten Tag <t t-out="object.customer_name" />,</p>\n                <p>der Status Ihres Widerrufs wurde aktualisiert.</p>\n                <table style="border-collapse: collapse; width: 100%; max-width: 700px;" cellpadding="6">\n                    <tr><td style="border: 1px solid #ddd; font-weight: bold; width: 220px;">Vorgangsnummer</td><td style="border: 1px solid #ddd;"><t t-out="object.name" /></td></tr>\n                    <tr><td style="border: 1px solid #ddd; font-weight: bold;">Bestell- oder Rechnungsnummer</td><td style="border: 1px solid #ddd;"><t t-out="object.order_reference" /></td></tr>\n                    <tr><td style="border: 1px solid #ddd; font-weight: bold;">Aktueller Status</td><td style="border: 1px solid #ddd;"><t t-out="dict(object._fields[\'state\'].selection).get(object.state)" /></td></tr>\n                </table>\n                <p style="margin-top: 20px;">Diese E-Mail informiert Sie über den aktuellen Bearbeitungsstand.</p>\n                <p>Mit freundlichen Grüßen</p>\n                <p><t t-out="user.company_id.name" /></p>\n            </div>\n        '}

def canonical(body):
    node = html.fragment_fromstring(body or "<div/>", create_parent="div")
    def walk(el):
        return (el.tag, tuple(sorted(el.attrib.items())), (el.text or "").strip(),
                tuple((walk(child), (child.tail or "").strip()) for child in el))
    return walk(node)

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("""UPDATE widerruf_record SET original_submission=jsonb_build_object(
        'customer_name',customer_name,'customer_email',customer_email,'order_reference',order_reference,
        'withdrawal_type',withdrawal_type,'message',message,'source','legacy_upgrade_snapshot'),
        received_at=create_date,company_id=COALESCE(company_id,(SELECT company_id FROM website WHERE id=website_id),%s)
        WHERE original_submission IS NULL""",[env.company.id])
    defaults = etree.parse(str(Path(__file__).resolve().parents[2] / "data/mail_template.xml"))
    for xmlid, old in LEGACY_BODIES.items():
        template = env.ref("odoo_widerrufbutton."+xmlid).with_context(lang="en_US")
        fields = defaults.xpath("//record[@id='%s']/field" % xmlid)
        by_name = {f.get("name"): f for f in fields}
        values = {}
        for field in ("subject", "email_from", "email_to"):
            if "${" in (template[field] or ""):
                values[field] = by_name[field].text
        if not template.lang:
            values["lang"] = by_name["lang"].text
        if canonical(template.body_html) == canonical(old):
            values["body_html"] = etree.tostring(by_name["body_html"][0], encoding="unicode")
        if values:
            template.write(values)
        data = env["ir.model.data"].search([('module','=','odoo_widerrufbutton'),('name','=',xmlid)])
        data.noupdate = True

    receipts = env["widerruf.record"].search([])
    env.add_to_compute(receipts._fields["confirmation_mail_sent"], receipts)
    receipts._recompute_recordset(["confirmation_mail_sent"])
