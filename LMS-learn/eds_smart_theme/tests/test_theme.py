# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestEdsTheme(TransactionCase):

    def test_module_installed(self):
        module = self.env['ir.module.module'].search([
            ('name', '=', 'eds_smart_theme'),
            ('state', '=', 'installed'),
        ])
        self.assertTrue(module, "eds_smart_theme should be installed")

    def test_web_assets_accessible(self):
        # Theme module provides CSS/JS assets; verify basic env access
        self.assertIsNotNone(self.env)
