# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import api, fields, models


class BlogPost(models.Model):
    _inherit = "blog.post"

    course_id = fields.Many2one(
        'op.course',
        string='Course',
        index=True,
        ondelete='set null',
    )

    @api.onchange('blog_id')
    def _onchange_blog_id(self):
        """Keep the LMS course synchronized with the selected blog."""
        for record in self:
            if not record.blog_id:
                record.course_id = False
                continue
            record.course_id = self.env['op.course'].search(
                [('blog_id', '=', record.blog_id.id)],
                limit=1,
            )
