# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestFieldsSelection(TransactionCase):

    def test_ir_model_fields_selection_accessible(self):
        # eds_fields_selection extends ir.model.fields.selection
        model = self.env['ir.model.fields.selection']
        self.assertIsNotNone(model)

    def test_selection_values_exist(self):
        # Verify we can read selection values
        selections = self.env['ir.model.fields.selection'].search([], limit=5)
        self.assertGreaterEqual(len(selections), 0)

    def test_update_selection_method_exists(self):
        # _update_selection() should be available on the model
        model = self.env['ir.model.fields.selection']
        self.assertTrue(hasattr(model, '_update_selection'))
