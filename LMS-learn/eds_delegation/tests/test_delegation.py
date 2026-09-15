# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo import fields
from datetime import timedelta


class TestDelegation(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = cls.env['res.users'].create({
            'name': 'Delegator User',
            'login': 'delegator@test.com',
            'email': 'delegator@test.com',
        })
        cls.user2 = cls.env['res.users'].create({
            'name': 'Delegate User',
            'login': 'delegate@test.com',
            'email': 'delegate@test.com',
        })
        cls.employee1 = cls.env['hr.employee'].create({
            'name': 'Delegator Employee',
            'user_id': cls.user1.id,
        })
        cls.employee2 = cls.env['hr.employee'].create({
            'name': 'Delegate Employee',
            'user_id': cls.user2.id,
        })
        cls.group = cls.env.ref('base.group_user')

    def _create_delegation(self, date_from=None, date_to=None):
        today = fields.Date.today()
        return self.env['delegation'].create({
            'employee_id': self.employee1.id,
            'delegateTo_employee_id': self.employee2.id,
            'date_from': date_from or today,
            'date_to': date_to or today + timedelta(days=7),
        })

    def test_delegation_defaults_to_draft(self):
        delegation = self._create_delegation()
        self.assertIn(delegation.state, ['draft', 'new'])

    def test_delegation_submit_noop(self):
        delegation = self._create_delegation()
        # action_submit is a no-op (pass), state remains draft
        delegation.action_submit()
        self.assertTrue(delegation.id)

    def test_delegation_confirm_requires_lines(self):
        delegation = self._create_delegation()
        from odoo.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            delegation.action_confirm()

    def test_delegation_confirm_with_line(self):
        delegation = self._create_delegation()
        # Add a delegation line with employee to satisfy the empty check
        self.env['delegation.line'].create({
            'delegation_id': delegation.id,
            'employee_id': self.employee2.id,
            'group_id': self.group.id,
        })
        delegation.action_confirm()
        self.assertEqual(delegation.state, 'confirmed')

    def test_delegation_from_to_employees(self):
        delegation = self._create_delegation()
        self.assertEqual(delegation.employee_id, self.employee1)
        self.assertEqual(delegation.delegateTo_employee_id, self.employee2)

    def test_delegation_date_range(self):
        today = fields.Date.today()
        delegation = self._create_delegation(
            date_from=today,
            date_to=today + timedelta(days=30)
        )
        self.assertLessEqual(delegation.date_from, delegation.date_to)
