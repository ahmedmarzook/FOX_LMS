from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LateSubmissionLine(models.Model):
    _name = "late.submission.line"
    _description = "Late Submission Line"
    _order = "no_of_days"

    no_of_days = fields.Integer(string="Days", required=True)
    penalty = fields.Float(string="Penalty %", required=True)
    late_submission_id = fields.Many2one(
        "late.submission",
        string="Late Submission",
        required=True,
        ondelete="cascade",
    )

    @api.constrains("no_of_days", "penalty")
    def _check_values(self):
        for record in self:
            if record.no_of_days < 0:
                raise ValidationError("Days cannot be negative.")
            if not 0 <= record.penalty <= 100:
                raise ValidationError(
                    "Penalty must be between 0 and 100."
                )
