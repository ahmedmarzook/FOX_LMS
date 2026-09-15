# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class OpAdmission(models.Model):
    _inherit = 'op.admission'

    def enroll_student(self):
        result = super().enroll_student()
        enrollment_model = self.env['op.course.enrollment']

        for admission in self:
            course = admission.course_id
            user = admission.student_id.user_id
            if not course or not course.is_enroll_user or not user:
                continue

            existing_enrollment = enrollment_model.search_count([
                ('course_id', '=', course.id),
                ('user_id', '=', user.id),
            ])
            if not existing_enrollment:
                enrollment_model.create({
                    'course_id': course.id,
                    'user_id': user.id,
                    'enrollment_date': fields.Datetime.now(),
                    'state': 'in_progress',
                })

        return result
