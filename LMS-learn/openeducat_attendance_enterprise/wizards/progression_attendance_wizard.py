# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################


from odoo import api, fields, models


class ProgressAttendanceWiz(models.TransientModel):
    """ Progression Attendance """
    _name = "attendance.progress.wizard"
    _description = "Attendance Progress Wizard"

    @api.model
    def _get_default_student(self):
        ctx = self._context
        active_ids = ctx.get('active_ids') or []
        if ctx.get('active_model') == 'op.student.progression' and active_ids:
            return self.env['op.student.progression'].browse(active_ids[0]).student_id

    student_id = fields.Many2one('op.student',
                                 string="Student Name",
                                 default=_get_default_student)
    attendance_ids = fields.Many2many('op.attendance.line',
                                      string='Attendance')

    def Add_attendance(self):
        progressions = self.env['op.student.progression'].browse(
            self.env.context.get('active_ids', [])
        )
        for progression in progressions:
            progression.attendance_lines = [(6, 0, self.attendance_ids.ids)]
        return {'type': 'ir.actions.act_window_close'}
