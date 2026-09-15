# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestWorkflow(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = cls.env['ir.model'].search(
            [('model', '=', 'res.partner')], limit=1
        )
        cls.group = cls.env.ref('base.group_user')

    def test_create_approval_config(self):
        config = self.env['approval.config'].create({
            'model_id': self.model.id,
            'state': 'test_state_01',
            'name': 'Test Approval Step',
            'group_ids': [(4, self.group.id)],
        })
        self.assertEqual(config.name, 'Test Approval Step')
        self.assertEqual(config.state, 'test_state_01')

    def test_approval_config_active_default(self):
        config = self.env['approval.config'].create({
            'model_id': self.model.id,
            'state': 'test_state_02',
            'name': 'Active Config',
            'group_ids': [(4, self.group.id)],
        })
        self.assertTrue(config.active)

    def test_approval_config_model_relation(self):
        config = self.env['approval.config'].create({
            'model_id': self.model.id,
            'state': 'test_state_03',
            'name': 'Model Config',
            'group_ids': [(4, self.group.id)],
        })
        self.assertEqual(config.model, 'res.partner')

    def test_approval_log_model_exists(self):
        # approval.log model should be accessible
        log_model = self.env['approval.log']
        self.assertIsNotNone(log_model)

    def test_state_tags_create(self):
        tag = self.env['state.tags'].create({'name': 'Pending Review'})
        self.assertEqual(tag.name, 'Pending Review')

    def test_approval_settings_create(self):
        model_id = self.env['ir.model'].search([('model', '=', 'res.partner')], limit=1)
        settings = self.env['approval.settings'].create({
            'model_id': model_id.id,
        })
        self.assertEqual(settings.model_id, model_id)
