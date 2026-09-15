# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class GradingAssignmentType(models.Model):
    _inherit = "grading.assignment.type"

    assign_type = fields.Selection(
        selection_add=[("exam", "Exam")],
        ondelete={"exam": "set default"},
    )
