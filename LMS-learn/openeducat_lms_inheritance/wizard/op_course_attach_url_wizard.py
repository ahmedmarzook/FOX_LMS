# -*- coding: utf-8 -*-

import base64
import mimetypes

from odoo import _, fields, models
from odoo.exceptions import UserError


class OpCourseAttachUrlWizard(models.TransientModel):
    _name = 'op.course.attach.url.wizard'
    _description = 'Attach Course File or URL'

    course_id = fields.Many2one(
        'op.course',
        string='Course',
        required=True,
    )

    attachment_type = fields.Selection(
        [
            ('file', 'File'),
            ('url', 'URL'),
        ],
        string='Attachment Type',
        required=True,
        default='file',
    )

    name = fields.Char(
        string='Title',
        required=True,
    )

    datas = fields.Binary(
        string='File',
        attachment=False,
    )

    filename = fields.Char(
        string='Filename',
    )

    url = fields.Char(
        string='URL',
        help='Link to an external file, image, video, or resource.',
    )

    def action_confirm(self):
        self.ensure_one()

        if not self.course_id:
            raise UserError(_('Please select a course.'))

        # ---------------------------------------------------------
        # FILE
        # ---------------------------------------------------------
        if self.attachment_type == 'file':

            if not self.datas:
                raise UserError(
                    _('Please select a file to upload.')
                )

            filename = self.filename or self.name or 'course_attachment'

            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'

            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': self.datas,
                'mimetype': mimetype,
                'res_model': 'op.course',
                'res_id': self.course_id.id,
            })

        # ---------------------------------------------------------
        # URL
        # ---------------------------------------------------------
        elif self.attachment_type == 'url':

            url = (self.url or '').strip()

            if not url:
                raise UserError(
                    _('Please enter a URL.')
                )

            if not (
                    url.startswith('http://')
                    or url.startswith('https://')
            ):
                raise UserError(
                    _('Please enter a valid URL starting with http:// or https://')
                )

            attachment = self.env['ir.attachment'].create({
                'name': self.name,
                'type': 'url',
                'url': url,
                'res_model': 'op.course',
                'res_id': self.course_id.id,
            })

        else:
            raise UserError(
                _('Please select an attachment type.')
            )

        # Link attachment to course
        self.course_id.course_attachment_ids = [
            (4, attachment.id)
        ]

        return {'type': 'ir.actions.act_window_close'}
