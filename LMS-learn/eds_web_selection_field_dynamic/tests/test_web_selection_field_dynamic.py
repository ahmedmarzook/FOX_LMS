# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestWebSelectionFieldDynamic(TransactionCase):

    def test_module_installed(self):
        module = self.env['ir.module.module'].search([
            ('name', '=', 'eds_web_selection_field_dynamic'),
            ('state', '=', 'installed'),
        ])
        self.assertTrue(module, "eds_web_selection_field_dynamic should be installed")

    def test_ir_model_fields_accessible(self):
        fields_model = self.env['ir.model.fields']
        self.assertIsNotNone(fields_model)
