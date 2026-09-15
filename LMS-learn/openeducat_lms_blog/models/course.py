# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import api, fields, models


class OpCourse(models.Model):
    _inherit = 'op.course'

    blog_id = fields.Many2one(
        'blog.blog',
        string='Blog',
        copy=False,
        ondelete='set null',
    )
    blog_post_ids = fields.One2many(
        'blog.post',
        'course_id',
        string='Blog Posts',
    )
    blogs_count = fields.Integer(
        string='Blog Posts',
        compute='_compute_blog_count',
    )

    @api.depends('blog_post_ids')
    def _compute_blog_count(self):
        for record in self:
            record.blogs_count = len(record.blog_post_ids)

    def action_create_blog(self):
        for record in self:
            if not record.blog_id:
                record.blog_id = self.env['blog.blog'].create({
                    'name': record.name,
                })
        return True

    def get_blog(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id(
            'website_blog.action_blog_post'
        )
        action['domain'] = [('course_id', '=', self.id)]
        action['context'] = {
            **self.env.context,
            'default_blog_id': self.blog_id.id,
            'default_course_id': self.id,
        }
        return action
