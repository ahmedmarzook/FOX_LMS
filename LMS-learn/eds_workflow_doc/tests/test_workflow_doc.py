# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestWorkflowDoc(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = cls.env['ir.model'].search(
            [('model', '=', 'res.partner')], limit=1
        )

    def test_approval_model_create(self):
        approval_model = self.env['approval.model'].create({
            'model_id': self.model.id,
        })
        self.assertTrue(approval_model.id)
        self.assertEqual(approval_model.model_id, self.model)

    def test_approval_model_name(self):
        approval_model = self.env['approval.model'].create({
            'model_id': self.model.id,
        })
        self.assertEqual(approval_model.model, 'res.partner')

    def test_approval_doc_model_exists(self):
        doc_model = self.env['approval.doc']
        self.assertIsNotNone(doc_model)
