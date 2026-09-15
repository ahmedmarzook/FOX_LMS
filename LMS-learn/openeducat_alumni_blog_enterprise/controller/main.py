# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import http

from odoo.addons.openeducat_alumni_enterprise.controller.main import AlumniWeb


class AlumniBlog(AlumniWeb):

    @http.route()
    def alumni_detail(self, alumni, **kwargs):
        response = super().alumni_detail(alumni=alumni, **kwargs)
        published_posts = alumni.sudo().blog_post_ids.filtered(
            lambda post: post.website_published
        )
        response.qcontext.update({
            "blogpost": published_posts,
        })
        return response
