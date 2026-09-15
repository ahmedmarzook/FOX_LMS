# -*- coding: utf-8 -*-
from odoo import fields, models


class OpCourse(models.Model):
    _inherit = 'op.course'

    doctor_name = fields.Char(
        string='Doctor Name',
        help='Name of the doctor associated with this course.',
    )

    course_attachment_ids = fields.Many2many(
        'ir.attachment',
        'op_course_attachment_rel',
        'course_id',
        'attachment_id',
        string='Attach Course Files',
        help='Files, images, or links attached to this course. Use the '
             "upload button to add files/images, or 'Add URL' to link an "
             'external resource.',
    )
    course_attachment_count = fields.Integer(
        string='Attachment Count',
        compute='_compute_course_attachment_count',
    )

    def _compute_course_attachment_count(self):
        for course in self:
            course.course_attachment_count = len(course.course_attachment_ids)

    def action_add_attachment_url(self):
        """Open a small wizard to attach an external file/image by URL."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Attachment by URL',
            'res_model': 'op.course.attach.url.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_course_id': self.id},
        }
