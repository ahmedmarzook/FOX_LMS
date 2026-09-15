# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import http
from odoo.http import request

from odoo.addons.openeducat_alumni_enterprise.controller.main import AlumniWeb


class AlumniEvent(AlumniWeb):

    @http.route()
    def alumni_detail(self, alumni, **kwargs):
        response = super().alumni_detail(alumni=alumni, **kwargs)
        if hasattr(response, 'qcontext') and response.qcontext is not None:
            events = request.env['event.event'].sudo().search([
                ('alumni_event_id', '=', alumni.id),
                ('website_published', '=', True),
            ])
            response.qcontext['alumnievents'] = events
        return response
