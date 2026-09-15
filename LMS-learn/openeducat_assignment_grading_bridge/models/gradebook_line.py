from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class GradebookLine(models.Model):
    _inherit = "gradebook.line"

    obtained_marks = fields.Float(string="Obtained Mark")
    penalty = fields.Float(string="Penalty %", readonly=True)

    @api.onchange("grade_table_line_id", "marks")
    def _compute_per_by_table_line(self):
        for record in self:
            record.penalty = 0.0

            if record.grade_table_line_id:
                record.percentage = record.grade_table_line_id.percentage
                record.grade_table_id = (
                    record.grade_table_line_id.grade_table_id
                )
                continue

            if not record.marks:
                record.percentage = 0.0
                continue

            points = record.grade_assigment_id.point
            if not points:
                record.percentage = 0.0
                continue

            if record.marks > points:
                raise ValidationError(
                    _("Marks should be less than or equal to %s", points)
                )

            percentage = record.marks * 100.0 / points
            assignment = self.env["op.assignment"].search(
                [
                    (
                        "grading_assignment_id",
                        "=",
                        record.grade_assigment_id.id,
                    )
                ],
                limit=1,
            )

            if assignment and record.gradebook_id.student_id:
                submission = assignment.assignment_sub_line.filtered(
                    lambda line: (
                        line.student_id == record.gradebook_id.student_id
                        and line.state == "accept"
                    )
                ).sorted(
                    key=lambda line: (
                        line.submission_date or fields.Datetime.now(),
                        line.id,
                    )
                )[-1:]

                if submission:
                    record.penalty = submission.penalty
                    percentage *= 1 - submission.penalty / 100.0

            record.percentage = percentage
