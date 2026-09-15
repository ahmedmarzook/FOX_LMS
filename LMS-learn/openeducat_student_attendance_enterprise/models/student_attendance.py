# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class StudentAttendance(models.Model):
    _inherit = "op.attendance.line"
    _order = "check_in desc, id desc"

    def _default_student(self):
        return self.env["op.student"].search(
            [("user_id", "=", self.env.uid)],
            limit=1,
        )

    attendance_id = fields.Many2one(
        "op.attendance.sheet",
        string="Attendance Sheet",
        tracking=True,
        ondelete="cascade",
    )
    student_id = fields.Many2one(
        "op.student",
        string="Student",
        default=_default_student,
        required=True,
        ondelete="cascade",
        index=True,
    )
    check_in = fields.Datetime(
        string="Attendance Time",
        default=fields.Datetime.now,
        readonly=True,
        required=True,
        index=True,
    )

    def display_name_get(self):
        return [
            (
                attendance.id,
                f"{attendance.student_id.name} - "
                f"{fields.Datetime.to_string(attendance.check_in)}",
            )
            for attendance in self
        ]


class OpAttendanceSheet(models.Model):
    _inherit = "op.attendance.sheet"

    def enable_kiosk(self):
        self.write({"state": "start"})
