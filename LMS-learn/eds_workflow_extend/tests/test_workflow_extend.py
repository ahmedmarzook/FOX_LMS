# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestWorkflowExtend(TransactionCase):

    def test_hr_employee_accessible(self):
        employee = self.env['hr.employee'].create({'name': 'Workflow Extend Employee'})
        self.assertEqual(employee.name, 'Workflow Extend Employee')

    def test_approval_record_model_accessible(self):
        # approval.record mixin should be available via eds_workflow
        model_obj = self.env['approval.record']
        self.assertIsNotNone(model_obj)
