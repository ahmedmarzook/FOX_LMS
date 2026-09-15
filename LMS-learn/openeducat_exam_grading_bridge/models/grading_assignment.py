# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import _, models
from odoo.exceptions import ValidationError


class GradingAssignment(models.Model):
    _inherit = "grading.assignment"

    def create_gradeline(self):
        self.ensure_one()

        action = super().create_gradeline()

        if self.assignment_type.assign_type != "exam":
            return action

        exam = self.env["op.exam"].search(
            [
                ("course_id", "=", self.course_id.id),
                ("subject_id", "=", self.subject_id.id),
                ("state", "in", ["result_updated", "done"]),
            ],
            order="end_time desc, id desc",
            limit=1,
        )
        if not exam:
            raise ValidationError(
                _("No completed exam result was found for this course and subject.")
            )
        if exam.total_marks <= 0:
            raise ValidationError(
                _("The selected exam must have a total mark greater than zero.")
            )
        if self.point <= 0:
            raise ValidationError(
                _("The grading assignment points must be greater than zero.")
            )

        attendees_by_student = {
            attendee.student_id.id: attendee
            for attendee in exam.attendees_line
        }

        grade_lines = self.env["gradebook.line"].search(
            [("grade_assigment_id", "=", self.id)]
        )
        for line in grade_lines:
            attendee = attendees_by_student.get(line.gradebook_id.student_id.id)
            if not attendee:
                continue

            exam_marks = attendee.marks if attendee.status == "present" else 0.0
            line.marks = exam_marks * self.point / exam.total_marks

        grade_lines._compute_per_by_table_line()
        return action
