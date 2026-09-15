# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class ForumPost(models.Model):
    _inherit = 'forum.post'

    course_id = fields.Many2one(
        'op.course',
        string='Course',
        index=True,
        ondelete='set null',
    )
