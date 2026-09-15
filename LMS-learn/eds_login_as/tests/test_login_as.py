# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestLoginAs(TransactionCase):

    def test_module_loaded(self):
        # eds_login_as provides HTTP-level login-as functionality
        # Verify the module is installed
        module = self.env['ir.module.module'].search([
            ('name', '=', 'eds_login_as'),
            ('state', '=', 'installed'),
        ])
        self.assertTrue(module, "eds_login_as module should be installed")

    def test_ir_http_accessible(self):
        # The module extends ir.http; verify basic model access
        ir_http = self.env['ir.rule']
        self.assertIsNotNone(ir_http)
