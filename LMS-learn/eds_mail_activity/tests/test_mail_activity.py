# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestMailActivity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Activity Partner'})
        cls.activity_type = cls.env.ref('mail.mail_activity_data_todo')

    def test_mail_activity_has_res_type(self):
        # Verify mail.activity has res_type field from eds_mail_activity
        activity = self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get_id('res.partner'),
            'res_id': self.partner.id,
            'activity_type_id': self.activity_type.id,
            'summary': 'Test Activity',
        })
        self.assertTrue(hasattr(activity, 'res_type'))

    def test_activity_created_on_partner(self):
        activity = self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get_id('res.partner'),
            'res_id': self.partner.id,
            'activity_type_id': self.activity_type.id,
            'summary': 'Follow Up',
        })
        self.assertEqual(activity.res_id, self.partner.id)
        self.assertEqual(activity.res_model, 'res.partner')

    def test_mail_activity_menu_model_exists(self):
        menu_model = self.env['mail.activity.menu']
        self.assertIsNotNone(menu_model)
