# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestEdsMail(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Mail Test Partner'})

    def test_mail_thread_inherited(self):
        # res.partner inherits mail.thread; verify eds_mail extension is loaded
        self.assertTrue(hasattr(self.env['mail.thread'], '_get_db_values'))

    def test_partner_chatter_accessible(self):
        # Partners can log messages via chatter (mail.thread)
        self.partner.message_post(body='Test message from eds_mail test')
        messages = self.env['mail.message'].search([
            ('res_id', '=', self.partner.id),
            ('model', '=', 'res.partner'),
        ])
        self.assertTrue(len(messages) >= 1)

    def test_create_partner_with_tracking(self):
        partner = self.env['res.partner'].create({
            'name': 'Tracked Partner',
            'email': 'tracked@test.com',
        })
        self.assertEqual(partner.name, 'Tracked Partner')
