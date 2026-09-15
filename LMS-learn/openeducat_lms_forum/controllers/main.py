# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import http
from odoo.http import request

from odoo.addons.openeducat_lms.controllers.main import OpenEduCatLms


class OpenEduCatLmsForum(OpenEduCatLms):

    @http.route()
    def course(self, course, **kwargs):
        response = super().course(course, **kwargs)
        posts = request.env['forum.post'].search([
            ('forum_id', '=', course.forum_id.id),
            ('parent_id', '=', False),
        ], order='create_date desc') if course.forum_id else request.env['forum.post']
        response.qcontext.update({'post_ids': posts})
        return response
