from odoo import fields, models


class LateSubmission(models.Model):
    _name = "late.submission"
    _description = "Late Submission"
    _order = "name"

    name = fields.Char(string="Name", required=True)
    late_sub_line = fields.One2many(
        "late.submission.line",
        "late_submission_id",
        string="Late Submission Rules",
        copy=True,
    )
