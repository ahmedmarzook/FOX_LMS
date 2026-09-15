###############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StudentMigrate(models.TransientModel):
    _name = "student.migrate"
    _description = "Student Migrate"

    date = fields.Date(default=fields.Date.today, required=True)
    course_from_id = fields.Many2one('op.course', required=True)
    course_to_id = fields.Many2one('op.course')
    batch_id = fields.Many2one('op.batch')
    optional_sub = fields.Boolean()
    student_ids = fields.Many2many('op.student', required=True)
    course_completed = fields.Boolean()

    @api.onchange('course_from_id')
    def student_by_course(self):
        self.student_ids = False

        if self.course_from_id:
            return {
                'domain': {
                    'student_ids': [
                        ('course_detail_ids.course_id', '=', self.course_from_id.id),
                        ('course_detail_ids.state', '=', 'running')
                    ]
                }
            }

    @api.constrains('course_from_id', 'course_to_id')
    def _check_courses(self):
        for rec in self:
            if rec.course_from_id == rec.course_to_id:
                raise ValidationError(_("From Course must not equal To Course"))

            if not rec.course_to_id and not rec.course_completed:
                raise ValidationError(_("Invalid migration request"))

    def student_migrate_forward(self):

        act_type = self.env.ref(
            'openeducat_activity.op_activity_type_3',
            raise_if_not_found=False
        )

        for rec in self:
            for student in rec.student_ids:

                # find course line
                for line in student.course_detail_ids.filtered(
                        lambda l: l.course_id == rec.course_from_id
                ):
                    line.state = 'finished'

                # activity log
                self.env['op.activity'].create({
                    'student_id': student.id,
                    'type_id': act_type.id if act_type else False,
                    'date': rec.date,
                    'description': _(
                        'Migration from %s to %s' %
                        (rec.course_from_id.name,
                         rec.course_to_id.name if rec.course_to_id else 'Completed')
                    )
                })

                if not rec.course_completed and rec.course_to_id:

                    self.env['op.student.course'].create({
                        'student_id': student.id,
                        'course_id': rec.course_to_id.id,
                        'batch_id': rec.batch_id.id,
                        'subject_ids': [(6, 0, rec.course_to_id.subject_ids.ids)]
                    })

                    reg = self.env['op.subject.registration'].create({
                        'student_id': student.id,
                        'batch_id': rec.batch_id.id,
                        'course_id': rec.course_to_id.id,
                        'min_unit_load': rec.course_to_id.min_unit_load or 0.0,
                        'max_unit_load': rec.course_to_id.max_unit_load or 0.0,
                        'state': 'draft',
                    })

                    reg.get_subjects()

                    if not rec.optional_sub:
                        reg.action_submitted()
                        reg.action_approve()
