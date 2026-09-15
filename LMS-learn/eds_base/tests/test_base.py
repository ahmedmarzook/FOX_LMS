# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestEdsBase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Base Test Partner',
            'email': 'base@test.com',
        })

    def test_get_model_name(self):
        # eds_base adds _get_model_name() to base model
        model_name = self.partner.get_model_name()
        self.assertIsNotNone(model_name)

    def test_isinstance_check(self):
        # _isinstance() method added by eds_base
        result = self.partner._isinstance('mail.thread')
        self.assertIsInstance(result, bool)

    def test_get_form_url(self):
        url = self.partner.get_form_url()
        self.assertIsNotNone(url)

    def test_base_mixin_accessible(self):
        # Verify eds_base extensions are available on res.partner
        partner = self.env['res.partner'].create({'name': 'Mixin Test'})
        self.assertTrue(hasattr(partner, '_base'))

    def test_random_password(self):
        pwd = self.partner._random_password()
        self.assertIsNotNone(pwd)
        self.assertGreater(len(pwd), 0)
