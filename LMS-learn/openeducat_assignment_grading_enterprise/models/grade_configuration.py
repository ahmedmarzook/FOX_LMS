# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class OpAssignGradeConfig(models.Model):
    _name = "op.assign.grade.config"
    _description = "Assignment Grade Configuration"
    _rec_name = "grade"
    _order = "grade"

    grade = fields.Char(string="Grade", required=True, translate=True)

    _sql_constraints = [
        (
            "assignment_grade_unique",
            "unique(grade)",
            "The assignment grade must be unique.",
        ),
    ]
