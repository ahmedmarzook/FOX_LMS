from datetime import datetime

from odoo import http
from odoo.http import request


class DiscussController(http.Controller):

    def _channel(self, channel_id):
        return request.env["discuss.channel"].sudo().browse(int(channel_id)).exists()

    @http.route(
        "/openeducat_live/session/welcome",
        type="jsonrpc",
        auth="public",
        methods=["POST"],
    )
    def session_welcome(self, channel_id, values=None):
        channel = self._channel(channel_id)
        if not channel:
            return "not-found"
        values = values or {}
        channel._live_add_user(values)
        if channel.live_meeting_locked:
            return "lock-meeting"
        if channel.live_password_locked and channel.live_password != values.get("password"):
            return "incorrect-password"
        return True

    @http.route(
        "/openeducat_live/session/lock-meeting",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def lock_meeting(self, channel_id, locked):
        channel = self._channel(channel_id)
        if not channel:
            return False
        channel._live_set_meeting_lock(bool(locked))
        return True

    @http.route(
        "/openeducat_live/session/lock-password",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def lock_password(self, channel_id, locked):
        channel = self._channel(channel_id)
        if not channel:
            return False
        channel._live_set_password_lock(bool(locked))
        return True

    @http.route(
        "/openeducat_live/session/check-lock",
        type="jsonrpc",
        auth="public",
        methods=["POST"],
    )
    def check_lock(self, channel_id):
        channel = self._channel(channel_id)
        if not channel:
            return {"meeting_locked": False, "password_locked": False}
        return {
            "meeting_locked": channel.live_meeting_locked,
            "password_locked": channel.live_password_locked,
        }

    @http.route(
        "/openeducat_live/session/create-password",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def create_password(self, channel_id):
        channel = self._channel(channel_id)
        if not channel:
            return False
        channel._live_create_password()
        event = request.env["calendar.event"].sudo().create({
            "name": f"Meeting {channel.id}",
            "is_meeting": True,
            "is_password": channel.live_password,
            "start": datetime.now(),
            "stop": datetime.now(),
            "channel_id": channel.id,
        })
        event._sync_live_meeting()
        return {
            "password": channel.live_password,
            "calendar": event.id,
            "url": event.videocall_location,
        }

    @http.route(
        "/openeducat_live/session/get-password",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def get_password(self, channel_id):
        channel = self._channel(channel_id)
        return channel.live_password if channel else False

    @http.route(
        "/openeducat_live/session/update-emoji",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def update_emoji(self, session_id, emoji):
        session = request.env["discuss.channel.rtc.session"].sudo().browse(
            int(session_id)
        ).exists()
        if not session:
            return False
        session.update_live_emoji(emoji)
        return True

    @http.route(
        "/openeducat_live/session/current-host",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def current_host(self, channel_id, partner_id=None):
        channel = self._channel(channel_id)
        if not channel or not partner_id:
            return False
        member = request.env["discuss.channel.member"].sudo().search(
            [
                ("channel_id", "=", channel.id),
                ("partner_id", "=", int(partner_id)),
            ],
            limit=1,
        )
        return bool(member.live_is_host)
