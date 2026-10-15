import hashlib
from unittest.mock import patch
from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import TransactionCase, tagged
from ..validation import validate_values

@tagged("post_install", "-at_install")
class TestWithdrawalSecurity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Record = cls.env["widerruf.record"].with_context(tracking_disable=True, mail_create_nosubscribe=True, mail_notify_force_send=False)
        cls.config = cls.env["ir.config_parameter"].sudo()
        cls.config.set_param("odoo_widerrufbutton.create_activity", "False")
        cls.config.set_param("odoo_widerrufbutton.send_internal_mail", "False")
        cls.config.set_param("odoo_widerrufbutton.send_customer_status_mail", "False")
        cls.data = {"name":"AHD-TEST-NO-SEQUENCE", "customer_name":"Test", "customer_email":"test@example.invalid", "order_reference":"TEST", "withdrawal_type":"full", "message":"Test"}
        def user(login, groups):
            return cls.env["res.users"].with_context(no_reset_password=True).create({"name":login,"login":login,"company_id":cls.env.company.id,"company_ids":[(6,0,cls.env.company.ids)],"group_ids":[(6,0,groups)]})
        cls.basic = user("withdrawal-basic-test", [cls.env.ref("base.group_user").id])
        cls.operator = user("withdrawal-operator-test", [cls.env.ref("odoo_widerrufbutton.group_widerruf_user").id])
        cls.other = cls.env["res.company"].create({"name":"Withdrawal isolated test company"})

    def test_ordinary_internal_user_denied(self):
        rec = self.Record.create(self.data)
        with self.assertRaises(AccessError):
            rec.with_user(self.basic).read(["message"])
        with self.assertRaises(AccessError):
            rec.with_user(self.basic).action_send_confirmation_mail()
        with self.assertRaises(AccessError):
            self.Record.with_user(self.basic).create(self.data)

    def test_operator_company_isolation(self):
        own = self.Record.create(self.data)
        other = self.Record.create(dict(self.data, company_id=self.other.id))
        self.assertTrue(self.Record.with_user(self.operator).search([("id","=",own.id)]))
        self.assertFalse(self.Record.with_user(self.operator).search([("id","=",other.id)]))
        with self.assertRaises(AccessError):
            other.with_user(self.operator).write({"message":"Forbidden"})
        with self.assertRaises(AccessError):
            own.with_user(self.operator).unlink()

    def test_immutable_receipt(self):
        rec = self.Record.create(self.data)
        snapshot = dict(rec.original_submission)
        rec.with_user(self.operator).write({"message":"Corrected working note"})
        self.assertEqual(rec.original_submission,snapshot)
        for values in [{"original_submission":{}},{"company_id":self.other.id},{"partner_id":self.basic.partner_id.id},{"attachment_ids":[]},{"confirmation_mail_sent":True}]:
            with self.assertRaises(AccessError):
                rec.with_user(self.operator).write(values)

    def test_invalid_shape_and_types(self):
        for value in [None, [], 123, {"customer_name":123}, {"message": []}]:
            self.assertTrue(validate_values(value)[1])

    def test_invalid_email_addresses(self):
        for email in ["x@", "a@example.invalid,b@example.invalid", "a@example.invalid\nBcc: b@example.invalid", "a@example.invalid;b@example.invalid"]:
            self.assertTrue(validate_values(dict(self.data,customer_email=email))[1])

    def test_limits_honeypot_and_type(self):
        for patch_values in [{"message":"A"*10001},{"customer_name":"A"*201},{"order_reference":"A"*129},{"website_url":"bot"},{"withdrawal_type":"unknown"}]:
            self.assertTrue(validate_values(dict(self.data,**patch_values))[1])
        self.assertFalse(validate_values(dict(self.data,message="A"*10000))[1])

    def test_orm_validation(self):
        with self.assertRaises(ValidationError):
            self.Record.create(dict(self.data,customer_email="x@"))
        rec = self.Record.create(self.data)
        with self.assertRaises(ValidationError):
            rec.write({"message":"A"*10001})

    def test_all_mail_envelopes(self):
        rec = self.Record.create(self.data)
        for xid in ["mail_template_widerruf_confirmation","mail_template_widerruf_internal_notification","mail_template_widerruf_status_update"]:
            t = self.env.ref("odoo_widerrufbutton."+xid).with_context(widerruf_internal_notify_email="internal@example.invalid")
            for f in ["subject","email_from","email_to"]:
                value = t._render_field(f,rec.ids)[rec.id]
                self.assertNotIn("${",value)
                self.assertNotIn("{{",value)
            self.assertIn("@example.invalid",t._render_field("email_to",rec.ids)[rec.id])

    def test_queued_mail_no_synchronous_send(self):
        rec = self.Record.create(self.data)
        with patch.object(type(self.env["mail.mail"]),"send",side_effect=AssertionError("Synchronous SMTP forbidden")):
            rec.with_user(self.operator).action_send_confirmation_mail()
        self.assertTrue(rec.confirmation_mail_id)
        self.assertEqual(rec.confirmation_mail_id.email_to,"test@example.invalid")
        self.assertEqual(rec.confirmation_mail_state,"outgoing")
        self.assertFalse(rec.confirmation_mail_sent)
        first = rec.confirmation_mail_id
        rec.action_send_confirmation_mail()
        self.assertEqual(rec.confirmation_mail_id,first)

    def test_failed_delivery_never_marked_sent(self):
        rec = self.Record.create(self.data)
        rec.action_send_confirmation_mail()
        rec.confirmation_mail_id.write({"state":"exception"})
        self.assertFalse(rec.confirmation_mail_sent)
        self.assertFalse(rec.confirmation_mail_sent_at)
        rec.confirmation_mail_id.write({"state":"sent"})
        self.assertTrue(rec.confirmation_mail_sent)
        self.assertTrue(rec.confirmation_mail_sent_at)

    def test_template_error_does_not_lose_receipt(self):
        rec = self.Record.create(self.data)
        with patch.object(type(self.env["mail.template"]),"send_mail",side_effect=ValueError("Audit error")):
            rec.action_send_confirmation_mail()
        self.assertTrue(rec.exists())
        self.assertFalse(rec.confirmation_mail_sent)
        self.assertTrue(rec.mail_error)

    def test_public_and_portal_have_no_rpc_model_access(self):
        rec = self.Record.create(self.data)
        for user in [self.env.ref("base.public_user"),self.basic]:
            with self.assertRaises(AccessError):
                rec.with_user(user).read(["customer_email"])

    def test_upload_config_validation(self):
        Settings = self.env["res.config.settings"]
        for vals in [{"widerruf_max_upload_size_mb":0},{"widerruf_max_upload_size_mb":11},{"widerruf_allowed_file_extensions":"svg"},{"widerruf_activity_deadline_days":-1},{"widerruf_internal_notify_email":"x@"}]:
            with self.assertRaises(ValidationError), self.cr.savepoint():
                Settings.create(vals)

    def _file_request(self, uploads):
        from types import SimpleNamespace
        from werkzeug.datastructures import MultiDict
        return SimpleNamespace(env=self.env,httprequest=SimpleNamespace(files=MultiDict(("attachments",f) for f in uploads)))

    def test_upload_validated_server_side(self):
        import io
        from PIL import Image
        from werkzeug.datastructures import FileStorage
        from ..controllers import main as cm
        buf=io.BytesIO();Image.new("RGB",(2,2),"red").save(buf,format="PNG")
        upload=FileStorage(stream=io.BytesIO(buf.getvalue()),filename="test.png",content_type="text/plain")
        with patch.object(cm,"request",self._file_request([upload])):
            values=cm.WebsiteWiderrufController()._upload_values()
        self.assertEqual(values[0]["mimetype"],"image/png")
        self.assertFalse(values[0]["public"])

    def test_upload_disabled_and_file_count(self):
        import io
        from werkzeug.datastructures import FileStorage
        from ..controllers import main as cm
        self.config.set_param("odoo_widerrufbutton.upload_enabled","False")
        with patch.object(cm,"request",self._file_request([FileStorage(stream=io.BytesIO(b"test"),filename="x.pdf")])):
            with self.assertRaises(ValueError):cm.WebsiteWiderrufController()._upload_values()
        self.config.set_param("odoo_widerrufbutton.upload_enabled","True")
        files=[FileStorage(stream=io.BytesIO(b"test"),filename="x.pdf") for _ in range(4)]
        with patch.object(cm,"request",self._file_request(files)):
            with self.assertRaises(ValueError):cm.WebsiteWiderrufController()._upload_values()

    def test_upload_content_name_and_size(self):
        import io
        from werkzeug.datastructures import FileStorage
        from ..controllers import main as cm
        self.config.set_param("odoo_widerrufbutton.max_upload_size_mb","1")
        for name,data in [("bad.pdf",b"<html>not pdf</html>"),("x.svg",b"<svg/>"),("x.png",b"not image"),("x.pdf",b"A"*(1024*1024+1)),("bad\nname.pdf",b"%PDF-test\n%%EOF")]:
            f=FileStorage(stream=io.BytesIO(data),filename=name)
            with patch.object(cm,"request",self._file_request([f])):
                with self.assertRaises(ValueError):cm.WebsiteWiderrufController()._upload_values()

    def test_draft_binding_expiry_and_website(self):
        from datetime import timedelta
        from types import SimpleNamespace
        from ..controllers import main as cm
        website=self.env["website"].search([],limit=1)
        fake=SimpleNamespace(env=self.env,website=website,session={"widerruf_binding":"unit-test"})
        controller=cm.WebsiteWiderrufController();token="A"*43
        with patch.object(cm,"request",fake):
            sub=self.env["widerruf.submission"].create({"token_hash":hashlib.sha256(token.encode()).hexdigest(),"session_hash":controller._binding_hash(),"ip_hash":"test","website_id":website.id,"values_json":self.data})
            self.assertEqual(controller._submission(token),sub)
            fake.session={"widerruf_binding":"another-session"}
            self.assertFalse(controller._submission(token))
            fake.session={"widerruf_binding":"unit-test"}
            self.cr.execute("UPDATE widerruf_submission SET create_date=%s WHERE id=%s",[fields.Datetime.now()-timedelta(minutes=21),sub.id]);sub.invalidate_recordset()
            self.assertFalse(controller._submission(token))
            for bad in ["[]","null","123",None,{},"A"*100000]:self.assertFalse(controller._submission(bad))

    def test_aggregate_storage_quota(self):
        from types import SimpleNamespace
        from ..controllers import main as cm
        fake=SimpleNamespace(env=self.env,session={"widerruf_binding":"quota-test"},httprequest=SimpleNamespace(remote_addr="127.0.0.1"))
        c=cm.WebsiteWiderrufController()
        with patch.object(cm,"request",fake):
            self.env["widerruf.submission"].create({"token_hash":"quota-token","session_hash":c._binding_hash(),"ip_hash":c._ip_hash(),"website_id":self.env["website"].search([],limit=1).id,"values_json":self.data,"upload_bytes":20*1024*1024})
            self.assertTrue(c._storage_limited(1))
            self.assertFalse(c._storage_limited(0))
