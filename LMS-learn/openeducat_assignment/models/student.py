###############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
###############################################################################

from odoo import models, fields


class OpStudent(models.Model):
    _inherit = "op.student"

    allocation_ids = fields.Many2many(
        'op.assignment',
        string='Assignment(s)'
    )

    assignment_count = fields.Integer(
        compute='compute_count_assignment'
    )

    def get_assignment(self):
        action = self.env.ref(
            'openeducat_assignment.act_open_op_assignment_view'
        ).read()[0]

        student_ids = self.ids

        action['domain'] = [
            ('allocation_ids', 'in', student_ids)
        ]

        return action

    def compute_count_assignment(self):
        for record in self:
            record.assignment_count = 0

            student_id = record._origin.id

            if not student_id:
                continue

            record.assignment_count = self.env[
                'op.assignment'
            ].search_count([
                ('allocation_ids', 'in', [student_id])
            ])