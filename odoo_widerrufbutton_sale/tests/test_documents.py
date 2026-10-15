from unittest.mock import patch
from odoo import Command
from odoo.exceptions import AccessError, ValidationError, UserError
from odoo.tests import TransactionCase, tagged

@tagged("post_install", "-at_install")
class TestWithdrawalDocuments(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for key in ["create_activity","send_internal_mail","send_customer_status_mail"]:
            cls.env["ir.config_parameter"].sudo().set_param("odoo_widerrufbutton."+key,"False")
        cls.Record=cls.env["widerruf.record"].with_context(tracking_disable=True,mail_create_nosubscribe=True,mail_notify_force_send=False)
        cls.partner=cls.env["res.partner"].create({"name":"Document integration test","email":"documents@example.invalid"})
        cls.product=cls.env["product.product"].create({"name":"Document integration service","type":"service","invoice_policy":"order","taxes_id":[Command.clear()]})
        cls.order=cls.env["sale.order"].with_context(send_email=False,tracking_disable=True).create({"partner_id":cls.partner.id,"client_order_ref":"AHD8-EXTERNAL","order_line":[Command.create({"product_id":cls.product.id,"product_uom_qty":1,"price_unit":25,"tax_ids":[Command.clear()]})]})
        cls.order.with_context(send_email=False).action_confirm()
        cls.invoice=cls.order._create_invoices()
        cls.invoice.write({"ref":"AHD8-INVOICE"})
        cls.other=cls.env["res.company"].create({"name":"Document foreign company"})

    def make_receipt(self,ref):
        return self.Record.create({"name":"AHD8-TEST","customer_name":"Document test","customer_email":"documents@example.invalid","order_reference":ref})

    def test_auto_order_and_related_invoice(self):
        rec=self.make_receipt(self.order.name)
        self.assertEqual(rec.sale_order_id,self.order)
        self.assertIn(self.order,rec.related_sale_order_ids)
        if "related_invoice_ids" in rec._fields:
            self.assertIn(self.invoice,rec.related_invoice_ids)
            action=rec.action_open_invoice_documents()
            self.assertEqual(action["res_id"],self.invoice.id)
        self.assertEqual(rec.action_open_sale_documents()["res_id"],self.order.id)

    def test_manual_order_for_unknown_reference(self):
        rec=self.make_receipt("NO-AUTOMATIC-MATCH")
        self.assertFalse(rec.sale_order_id)
        wizard=self.env["widerruf.document.assignment"].create({"widerruf_id":rec.id,"document_type":"sale","sale_order_id":self.order.id})
        wizard.action_assign()
        self.assertTrue(rec.documents_manually_assigned)
        self.assertEqual(rec.sale_order_id,self.order)
        rec.write({"order_reference":"STILL-NO-MATCH"})
        rec.action_find_documents()
        self.assertEqual(rec.sale_order_id,self.order)
        self.assertFalse(rec.partner_id)

    def test_manual_invoice_reverse_order(self):
        if "invoice_id" not in self.Record._fields:self.skipTest("Accounting integration optional")
        self.assertEqual(self.order.widerruf_count,0)
        rec=self.make_receipt("NO-MATCH-FOR-INVOICE")
        wizard=self.env["widerruf.document.assignment"].create({"widerruf_id":rec.id,"document_type":"invoice","invoice_id":self.invoice.id})
        wizard.action_assign()
        self.assertEqual(rec.invoice_id,self.invoice)
        self.assertFalse(rec.sale_order_id)
        self.assertIn(self.order,rec.related_sale_order_ids)
        self.assertIn(self.invoice,rec.related_invoice_ids)
        self.assertEqual(self.order.widerruf_count,1)
        self.assertEqual(self.order.action_view_widerrufe()["res_id"],rec.id)

    def test_exact_invoice_match(self):
        if "invoice_id" not in self.Record._fields:self.skipTest("Accounting integration optional")
        rec=self.make_receipt("AHD8-INVOICE")
        self.assertEqual(rec.invoice_id,self.invoice)
        self.assertIn(self.order,rec.related_sale_order_ids)
        self.assertFalse(rec.partner_id)

    def test_ambiguous_and_no_partial_match(self):
        duplicate=self.env["sale.order"].create({"partner_id":self.partner.id,"client_order_ref":"AHD8-EXTERNAL"})
        rec=self.make_receipt("AHD8-EXTERNAL")
        self.assertFalse(rec.sale_order_id)
        self.assertFalse(self.make_receipt(self.order.name[:-1]).sale_order_id)

    def test_reassignment_clears_stale_direct_links(self):
        if "invoice_id" not in self.Record._fields:self.skipTest("Accounting integration optional")
        rec=self.make_receipt("AHD8-INVOICE")
        wizard=self.env["widerruf.document.assignment"].create({"widerruf_id":rec.id,"document_type":"sale","sale_order_id":self.order.id})
        wizard.action_assign()
        self.assertFalse(rec.invoice_id)
        self.assertEqual(rec.sale_order_id,self.order)
        rec.action_clear_document_assignment()
        self.assertFalse(rec.sale_order_id)
        self.assertFalse(rec.documents_manually_assigned)

    def test_foreign_company_rejected(self):
        foreign=self.env["sale.order"].create({"partner_id":self.partner.id,"company_id":self.other.id})
        rec=self.make_receipt("FOREIGN-UNMATCHED")
        wizard=self.env["widerruf.document.assignment"].create({"widerruf_id":rec.id,"document_type":"sale","sale_order_id":foreign.id})
        with self.assertRaises(ValidationError):wizard.action_assign()
        with self.assertRaises(AccessError):rec.write({"documents_manually_assigned":True})

    def test_existing_financial_documents_unchanged(self):
        before=(self.order.state,self.order.amount_total,self.invoice.state,self.invoice.amount_total,self.order.order_line.ids,self.invoice.invoice_line_ids.ids)
        rec=self.make_receipt(self.order.name)
        rec.action_find_documents()
        self.assertEqual(before,(self.order.state,self.order.amount_total,self.invoice.state,self.invoice.amount_total,self.order.order_line.ids,self.invoice.invoice_line_ids.ids))

    def test_receipt_operator_without_document_rights(self):
        u=self.env["res.users"].with_context(no_reset_password=True).create({"name":"Receipt-only operator","login":"document-only-operator","group_ids":[Command.set([self.env.ref("odoo_widerrufbutton.group_widerruf_user").id])]})
        rec=self.make_receipt(self.order.name)
        limited=rec.with_user(u)
        self.assertFalse(limited.sale_document_count)
        with self.assertRaises(UserError):limited.action_open_sale_documents()
        if "invoice_id" in rec._fields:self.assertFalse(limited.invoice_document_count)

    def test_no_document_no_smartbutton_action(self):
        rec=self.make_receipt("TOTALLY-UNKNOWN")
        self.assertFalse(rec.sale_document_count)
        with self.assertRaises(UserError):rec.action_open_sale_documents()
        action=rec.action_assign_document()
        self.assertEqual(action["target"],"new")

    def test_supplier_invoice_rejected(self):
        if "invoice_id" not in self.Record._fields:self.skipTest("Accounting integration optional")
        move=self.env["account.move"].create({"partner_id":self.partner.id,"move_type":"in_invoice"})
        rec=self.make_receipt("SUPPLIER-NOT-CUSTOMER")
        wizard=self.env["widerruf.document.assignment"].create({"widerruf_id":rec.id,"document_type":"invoice","invoice_id":move.id})
        with self.assertRaises(ValidationError):wizard.action_assign()

    def test_invoice_reverse_smartbutton(self):
        if "invoice_id" not in self.Record._fields:self.skipTest("Accounting integration optional")
        self.assertEqual(self.invoice.widerruf_count,0)
        rec=self.make_receipt(self.order.name)
        self.assertEqual(self.invoice.widerruf_count,1)
        self.assertEqual(self.invoice.action_view_widerrufe()["res_id"],rec.id)

    def test_customer_credit_note_link(self):
        if "invoice_id" not in self.Record._fields:self.skipTest("Accounting integration optional")
        credit=self.env["account.move"].create({"partner_id":self.partner.id,"move_type":"out_refund","ref":"AHD8-CREDIT"})
        rec=self.make_receipt("AHD8-CREDIT")
        self.assertEqual(rec.invoice_id,credit)
        self.assertEqual(rec.action_open_invoice_documents()["res_id"],credit.id)

    def test_document_reader_without_receipt_rights(self):
        rec=self.make_receipt(self.order.name)
        u=self.env["res.users"].with_context(no_reset_password=True).create({"name":"Invoice reader only","login":"document-reader-only","group_ids":[Command.set([self.env.ref("account.group_account_invoice").id])]})
        self.assertEqual(self.order.with_user(u).widerruf_count,0)
        with self.assertRaises(AccessError):self.order.with_user(u).action_view_widerrufe()
        if "invoice_id" in rec._fields:
            self.assertEqual(self.invoice.with_user(u).widerruf_count,0)
            with self.assertRaises(AccessError):self.invoice.with_user(u).action_view_widerrufe()
