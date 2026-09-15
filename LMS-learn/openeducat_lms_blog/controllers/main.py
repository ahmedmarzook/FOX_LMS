# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import http
from odoo.http import request

from odoo.addons.openeducat_lms.controllers.main import OpenEduCatLms


class OpenEduCatLmsBlog(OpenEduCatLms):

    @http.route()
    def course(self, course, **kwargs):
        response = super().course(course, **kwargs)
        blog_posts = request.env['blog.post'].sudo().search([
            ('course_id', '=', course.id),
            ('website_published', '=', True),
        ], order='post_date desc, id desc')
        if hasattr(response, 'qcontext'):
            response.qcontext.update({'blog_post_ids': blog_posts})
        return response
