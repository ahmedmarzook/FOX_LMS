# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import api, fields, models


class OpAssignmentSubLine(models.Model):
    _inherit = "op.assignment.sub.line"

    grades_id = fields.Many2one(
        "op.assign.grade.config",
        string="Grade",
        ondelete="set null",
    )
    evaluation_boolean = fields.Boolean(
        string="Grade Evaluation",
        compute="_compute_evaluation_boolean",
        store=True,
    )

    @api.depends("assignment_id", "assignment_id.evaluation_type")
    def _compute_evaluation_boolean(self):
        for record in self:
            record.evaluation_boolean = (
                record.assignment_id.evaluation_type == "grade"
            )


class OpAssignment(models.Model):
    _inherit = "op.assignment"

    evaluation_type = fields.Selection(
        [
            ("mark", "Marks"),
            ("grade", "Grade"),
        ],
        string="Evaluation Type",
        default="mark",
        required=True,
        tracking=True,
    )
