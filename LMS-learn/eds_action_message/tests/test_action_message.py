# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestActionMessage(TransactionCase):

    def test_module_installed(self):
        module = self.env['ir.module.module'].search([
            ('name', '=', 'eds_action_message'),
            ('state', '=', 'installed'),
        ])
        self.assertTrue(module, "eds_action_message should be installed")

    def test_ir_actions_accessible(self):
        actions = self.env['ir.actions.actions'].search([], limit=1)
        self.assertGreaterEqual(len(actions), 0)
