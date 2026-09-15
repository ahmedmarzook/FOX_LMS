# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import http
from odoo.http import request


class LiveAssignmentController(http.Controller):

    @http.route(
        "/openeducat_live_assignment/context",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def assignment_context(self, channel_id):
        channel = request.env["discuss.channel"].browse(
            int(channel_id)
        ).exists()
        if not channel:
            return {"error": "channel_not_found"}

        event = channel.live_calendar_id.exists()
        if not event:
            return {"error": "calendar_event_not_found"}

        return {
            "course": event.course_id.id or False,
            "subject": event.subject_id.id or False,
            "batch": event.batch_id.id or False,
            "event": event.id,
            "channel": channel.id,
        }
