# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpCourse(models.Model):
    _inherit = 'op.course'

    forum_id = fields.Many2one(
        'forum.forum',
        string='Forum',
        copy=False,
        ondelete='set null',
        index=True,
    )
    forum_post_ids = fields.One2many(
        'forum.post',
        'course_id',
        string='Forum Posts',
    )
    forum_count = fields.Integer(
        string='Forum Posts',
        compute='_compute_forum_count',
    )

    @api.depends('forum_post_ids')
    def _compute_forum_count(self):
        for course in self:
            course.forum_count = len(course.forum_post_ids)

    def action_create_forum(self):
        Forum = self.env['forum.forum'].sudo()
        for course in self:
            if self.env.user.karma < 7:
                raise ValidationError(_(
                    'Your account does not have enough forum karma. '
                    'Please verify your email from the Forum application first.'
                ))
            if not course.forum_id:
                course.forum_id = Forum.create({'name': course.name})
        return True

    def get_forum(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id(
            'website_forum.action_forum_post'
        )
        action['domain'] = [('forum_id', '=', self.forum_id.id)]
        action['context'] = {
            **self.env.context,
            'default_forum_id': self.forum_id.id,
            'default_course_id': self.id,
        }
        return action
