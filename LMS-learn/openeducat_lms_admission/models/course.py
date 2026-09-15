# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class OpCourse(models.Model):
    _inherit = 'op.course'

    is_enroll_user = fields.Boolean(string='Enroll User')
    online_course_created = fields.Boolean(
        string='Online Course Created',
        copy=False,
    )

    def create_online_course(self):
        self.write({
            'online_course': True,
            'online_course_created': True,
        })
        return True
