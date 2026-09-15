from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpAssignment(models.Model):
    _inherit = "op.assignment"

    late_submission_id = fields.Many2one(
        "late.submission",
        string="Late Submission Criteria",
        ondelete="set null",
    )
    mark_update = fields.Boolean(string="Marks Updated", copy=False)
    hide = fields.Boolean(compute="_compute_hide")
    attempt = fields.Selection(
        [
            ("first_graded", "First Graded Attempt"),
            ("last_graded", "Last Graded Attempt"),
            ("lowest_grade", "Lowest Grade"),
            ("highest_grade", "Highest Grade"),
            ("average_of_graded", "Average of Graded Attempts"),
        ],
        string="Score Attempt Using",
        default="first_graded",
        required=True,
    )

    @api.depends("grade", "grade.grade_table_ids")
    def _compute_hide(self):
        for record in self:
            record.hide = bool(
                not record.grade or record.grade.grade_table_ids
            )

    def _accepted_attempts_for_student(self, student):
        self.ensure_one()
        return self.assignment_sub_line.filtered(
            lambda line: (
                line.student_id == student and line.state == "accept"
            )
        ).sorted(key=lambda line: (line.submission_date or fields.Datetime.now(), line.id))

    def _selected_attempt_values(self, attempts):
        self.ensure_one()
        if not attempts:
            return False

        if self.attempt_type == "single" or self.attempt == "first_graded":
            selected = attempts[0]
            return selected.marks, selected.obtained_mark
        if self.attempt == "last_graded":
            selected = attempts[-1]
            return selected.marks, selected.obtained_mark
        if self.attempt == "lowest_grade":
            selected = min(attempts, key=lambda line: line.marks)
            return selected.marks, selected.obtained_mark
        if self.attempt == "highest_grade":
            selected = max(attempts, key=lambda line: line.marks)
            return selected.marks, selected.obtained_mark

        count = len(attempts)
        return (
            sum(attempts.mapped("marks")) / count,
            sum(attempts.mapped("obtained_mark")) / count,
        )

    def update_mark(self):
        for assignment in self:
            grading_assignment = assignment.grading_assignment_id
            if not grading_assignment:
                continue

            for student in assignment.allocation_ids:
                attempts = assignment._accepted_attempts_for_student(student)
                values = assignment._selected_attempt_values(attempts)
                if not values:
                    continue

                gradebook = self.env["gradebook.gradebook"].search(
                    [
                        ("student_id", "=", student.id),
                        ("academic_year_id", "=", assignment.year_id.id),
                        ("course_id", "=", assignment.course_id.id),
                    ],
                    limit=1,
                )
                if not gradebook:
                    continue

                grade_line = self.env["gradebook.line"].search(
                    [
                        ("gradebook_id", "=", gradebook.id),
                        ("grade_assigment_id", "=", grading_assignment.id),
                    ],
                    limit=1,
                )
                if not grade_line:
                    continue

                grade_line.write(
                    {
                        "marks": values[0],
                        "obtained_marks": values[1],
                    }
                )
                grade_line._compute_per_by_table_line()

            assignment.mark_update = True
        return True


class OpAssignmentSubLine(models.Model):
    _inherit = "op.assignment.sub.line"

    obtained_mark = fields.Float(string="Obtained Marks", readonly=True)
    penalty = fields.Float(string="Penalty %", readonly=True)
    late_submit = fields.Boolean(
        string="Late Submission",
        compute="_compute_late_submission",
        store=True,
    )

    @api.depends(
        "marks",
        "submission_date",
        "assignment_id.submission_date",
        "assignment_id.point",
        "assignment_id.late_submission_id",
        "assignment_id.late_submission_id.late_sub_line",
        "assignment_id.late_submission_id.late_sub_line.no_of_days",
        "assignment_id.late_submission_id.late_sub_line.penalty",
    )
    def _compute_late_submission(self):
        for record in self:
            record.late_submit = False
            record.penalty = 0.0
            record.obtained_mark = record.marks

            if not record.assignment_id or not record.marks:
                continue

            max_marks = record.assignment_id.point
            if max_marks and record.marks > max_marks:
                raise ValidationError(
                    _("Marks should be less than or equal to %s", max_marks)
                )

            deadline = record.assignment_id.submission_date
            submitted = record.submission_date
            criteria = record.assignment_id.late_submission_id

            if not deadline or not submitted or submitted <= deadline or not criteria:
                continue

            record.late_submit = True
            days_late = (submitted - deadline).days

            matching_line = criteria.late_sub_line.filtered(
                lambda line: days_late <= line.no_of_days
            ).sorted("no_of_days")[:1]

            if matching_line:
                penalty = matching_line.penalty
                record.penalty = penalty
                record.obtained_mark = record.marks * (1 - penalty / 100.0)

    def clear_attempt(self):
        assignments = self.mapped("assignment_id")
        result = self.unlink()
        for assignment in assignments.filtered("mark_update"):
            assignment.update_mark()
        return result
