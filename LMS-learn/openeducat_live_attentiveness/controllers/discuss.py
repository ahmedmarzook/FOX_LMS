# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import fields, http
from odoo.http import request

from odoo.addons.openeducat_live.controllers.discuss import (
    DiscussController as LiveDiscussController,
)


class LiveAttentivenessController(LiveDiscussController):

    def _channel(self, channel_id):
        return request.env["discuss.channel"].sudo().browse(
            int(channel_id)
        ).exists()

    def _event(self, channel):
        return channel.live_calendar_id.exists() if channel else False

    def _partner(self):
        return request.env.user.partner_id if request.env.user else False

    @http.route()
    def session_welcome(self, channel_id, values=None):
        result = super().session_welcome(channel_id, values)
        if result is not True:
            return result

        channel = self._channel(channel_id)
        event = self._event(channel)
        partner = self._partner()
        if event and partner:
            request.env["channel.logs"].sudo().search(
                [
                    ("meeting_id", "=", event.id),
                    ("partner_id", "=", partner.id),
                ],
                limit=1,
            ) or request.env["channel.logs"].sudo().create({
                "partner_id": partner.id,
                "join_time": fields.Datetime.now(),
                "meeting_id": event.id,
            })
        return result

    @http.route(
        "/openeducat_live_attentiveness/context",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def attentiveness_context(self, channel_id):
        channel = self._channel(channel_id)
        event = self._event(channel)
        if not channel:
            return {"error": "channel_not_found"}
        if not event:
            return {"error": "calendar_event_not_found"}
        return {
            "channel": channel.id,
            "calendar": event.id,
            "meeting_locked": channel.live_meeting_locked,
            "ended": event.live_meeting_ended,
        }

    @http.route(
        "/openeducat_live_attentiveness/start",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def start_interval(self, channel_id):
        channel = self._channel(channel_id)
        event = self._event(channel)
        partner = self._partner()
        if not channel or not event or not partner:
            return False

        channel_log = request.env["channel.logs"].sudo().search(
            [
                ("meeting_id", "=", event.id),
                ("partner_id", "=", partner.id),
            ],
            limit=1,
        )
        if not channel_log:
            channel_log = request.env["channel.logs"].sudo().create({
                "partner_id": partner.id,
                "join_time": fields.Datetime.now(),
                "meeting_id": event.id,
            })

        open_log = request.env["log.attentive"].sudo().search(
            [
                ("logs_id", "=", channel_log.id),
                ("end_time", "=", False),
            ],
            limit=1,
        )
        if open_log:
            return open_log.id

        log = request.env["log.attentive"].sudo().create({
            "start_time": fields.Datetime.now(),
            "logs_id": channel_log.id,
        })
        return log.id

    @http.route(
        "/openeducat_live_attentiveness/end",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def end_interval(self, log_id):
        log = request.env["log.attentive"].sudo().browse(
            int(log_id)
        ).exists()
        if not log:
            return False
        if not log.end_time:
            log.end_time = fields.Datetime.now()
        return True

    @http.route(
        "/openeducat_live_attentiveness/raised-hand",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def raised_hand(self, channel_id):
        channel = self._channel(channel_id)
        event = self._event(channel)
        partner = self._partner()
        if not event or not partner:
            return False

        channel_log = request.env["channel.logs"].sudo().search(
            [
                ("meeting_id", "=", event.id),
                ("partner_id", "=", partner.id),
            ],
            limit=1,
        )
        if not channel_log:
            channel_log = request.env["channel.logs"].sudo().create({
                "partner_id": partner.id,
                "join_time": fields.Datetime.now(),
                "meeting_id": event.id,
            })
        channel_log.raised_hand += 1
        return channel_log.raised_hand

    @http.route(
        "/openeducat_live_attentiveness/add-guests",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def add_guests(self, calendar_id, guests=None):
        event = request.env["calendar.event"].browse(
            int(calendar_id)
        ).exists()
        if not event:
            return False
        for guest_name in guests or []:
            guest_name = (guest_name or "").strip()
            if not guest_name or guest_name == "Anonymous":
                continue
            request.env["meeting.guest"].sudo().search(
                [
                    ("guest", "=", guest_name),
                    ("meeting_guest_id", "=", event.id),
                ],
                limit=1,
            ) or request.env["meeting.guest"].sudo().create({
                "guest": guest_name,
                "meeting_guest_id": event.id,
            })
        return True

    @http.route(
        "/openeducat_live_attentiveness/end-meeting",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def end_meeting(self, channel_id):
        channel = self._channel(channel_id)
        event = self._event(channel)
        if not channel or not event:
            return False

        member = request.env["discuss.channel.member"].sudo().search(
            [
                ("channel_id", "=", channel.id),
                ("partner_id", "=", request.env.user.partner_id.id),
                ("live_is_host", "=", True),
            ],
            limit=1,
        )
        if not member and not request.env.user.has_group("base.group_system"):
            return {"error": "host_required"}

        event.action_end_live_meeting()
        return True
