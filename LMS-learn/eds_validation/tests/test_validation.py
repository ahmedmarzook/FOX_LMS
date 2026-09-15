# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestValidationGroup(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = cls.env['ir.model'].search([('model', '=', 'res.partner')], limit=1)

    def _create_group(self, name='Test Group'):
        return self.env['validation.group'].create({
            'name': name,
            'model_id': self.model.id,
        })

    def test_create_validation_group(self):
        group = self._create_group()
        self.assertEqual(group.name, 'Test Group')
        self.assertEqual(group.model_id.model, 'res.partner')

    def test_validation_group_active_default(self):
        group = self._create_group()
        self.assertTrue(group.active)

    def test_create_validation_rule(self):
        group = self._create_group()
        rule = self.env['validation'].create({
            'name': 'Test Rule',
            'group_id': group.id,
            'type': 'raise',
            'message': 'Test validation message',
            'on_write': True,
        })
        self.assertEqual(rule.name, 'Test Rule')
        self.assertEqual(rule.type, 'raise')

    def test_validation_rule_types(self):
        group = self._create_group()
        for vtype in ['raise', 'confirm', 'log', 'notify']:
            rule = self.env['validation'].create({
                'name': f'Rule {vtype}',
                'group_id': group.id,
                'type': vtype,
                'message': f'Message for {vtype}',
            })
            self.assertEqual(rule.type, vtype)

    def test_validation_log_action(self):
        group = self._create_group('Log Group')
        rule = self.env['validation'].create({
            'name': 'Log Rule',
            'group_id': group.id,
            'type': 'log',
            'message': 'Logging this event',
            'on_write': True,
        })
        self.assertTrue(rule.active)

    def test_multiple_rules_per_group(self):
        group = self._create_group('Multi Rule Group')
        for i in range(3):
            self.env['validation'].create({
                'name': f'Rule {i}',
                'group_id': group.id,
                'type': 'log',
                'message': f'Message {i}',
            })
        rules = self.env['validation'].search([('group_id', '=', group.id)])
        self.assertEqual(len(rules), 3)
