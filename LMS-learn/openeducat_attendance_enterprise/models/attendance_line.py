# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import api, fields, models


class OpAttendanceLine(models.Model):
    _inherit = "op.attendance.line"

    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    session_id = fields.Many2one(related="attendance_id.session_id", store=True)
    progression_id = fields.Many2one("op.student.progression", string="Progression No")

    def action_onboarding_attendance_lines_layout(self):
        self.env.company.onboarding_attendance_lines_layout_state = "done"
        return {"type": "ir.actions.act_window_close"}

    @api.onchange("student_id")
    def onchange_student_attendance_progression(self):
        for record in self:
            record.progression_id = False
            if record.student_id:
                progression = self.env["op.student.progression"].search(
                    [("student_id", "=", record.student_id.id)], limit=1
                )
                record.progression_id = progression
