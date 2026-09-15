# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class StudentProgression(models.Model):
    _inherit = "op.student.progression"

    assignment_lines = fields.One2many(
        'op.assignment.sub.line',
        'progression_id',
        string='Progression Assignment'
    )

    total_assignment = fields.Integer(
        string='Total Assignment',
        compute='_compute_total_assignment',
        store=True
    )

    @api.depends('assignment_lines')
    def _compute_total_assignment(self):
        for record in self:
            record.total_assignment = len(record.assignment_lines)