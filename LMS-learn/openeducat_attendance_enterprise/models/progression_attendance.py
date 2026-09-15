# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import api, fields, models


class StudentProgression(models.Model):
    _inherit = "op.student.progression"

    attendance_lines = fields.One2many(
        "op.attendance.line", "progression_id", string="Progression Attendance"
    )
    total_attendance = fields.Integer(
        string="Total Attendance", compute="_compute_total_attendance", store=True
    )

    @api.depends("attendance_lines")
    def _compute_total_attendance(self):
        for record in self:
            record.total_attendance = len(record.attendance_lines)
