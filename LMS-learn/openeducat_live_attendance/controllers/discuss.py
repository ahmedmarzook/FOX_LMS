# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import http
from odoo.http import request

from odoo.addons.openeducat_live.controllers.discuss import (
    DiscussController as LiveDiscussController,
)


class LiveAttendanceController(LiveDiscussController):

    @http.route()
    def session_welcome(self, channel_id, values=None):
        values = values or {}
        channel = request.env["discuss.channel"].sudo().browse(
            int(channel_id)
        ).exists()

        if channel:
            channel._live_add_user(values)
            user_id = channel.live_user_id
            event = channel.live_calendar_id
            sheet = event.sheet_id if event else False

            if user_id and sheet and not channel.live_meeting_locked:
                student = request.env["op.student"].sudo().search(
                    [("user_id", "=", user_id)],
                    limit=1,
                )
                if student:
                    request.env["op.attendance.line"].sudo().search(
                        [
                            ("student_id", "=", student.id),
                            ("attendance_id", "=", sheet.id),
                        ],
                        limit=1,
                    ) or request.env["op.attendance.line"].sudo().create({
                        "student_id": student.id,
                        "attendance_id": sheet.id,
                        "present": True,
                    })

        return super().session_welcome(channel_id, values)

    @http.route(
        "/openeducat_live_attendance/registers",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def get_registers(self):
        return request.env["op.attendance.register"].search_read(
            [],
            ["name", "course_id", "batch_id", "subject_id"],
            order="name",
        )

    @http.route(
        "/openeducat_live_attendance/sheets",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def get_sheets(self, register_id):
        register = request.env["op.attendance.register"].browse(
            int(register_id)
        ).exists()
        if not register:
            return []
        return request.env["op.attendance.sheet"].search_read(
            [("register_id", "=", register.id)],
            ["name", "attendance_date", "attendance_sheet_date", "state"],
            order="attendance_date desc, id desc",
        )

    @http.route(
        "/openeducat_live_attendance/create-sheet",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def create_sheet(self, register_id):
        register = request.env["op.attendance.register"].browse(
            int(register_id)
        ).exists()
        if not register:
            return {"error": "register_not_found"}

        sheet = request.env["op.attendance.sheet"].create({
            "register_id": register.id,
        })
        return {
            "id": sheet.id,
            "name": sheet.name,
            "attendance_sheet_date": sheet.attendance_sheet_date,
        }

    @http.route(
        "/openeducat_live_attendance/set-sheet",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def set_sheet(self, channel_id, sheet_id):
        channel = request.env["discuss.channel"].browse(
            int(channel_id)
        ).exists()
        sheet = request.env["op.attendance.sheet"].browse(
            int(sheet_id)
        ).exists()
        if not channel:
            return {"error": "channel_not_found"}
        if not sheet:
            return {"error": "sheet_not_found"}
        if not channel.live_calendar_id:
            return {"error": "calendar_event_not_found"}

        event = channel.live_calendar_id
        event.write({
            "register_id": sheet.register_id.id,
            "sheet_id": sheet.id,
        })
        return {
            "sheet": sheet.id,
            "register": sheet.register_id.id,
            "event": event.id,
        }

    @http.route(
        "/openeducat_live_attendance/context",
        type="jsonrpc",
        auth="user",
        methods=["POST"],
    )
    def attendance_context(self, channel_id):
        channel = request.env["discuss.channel"].browse(
            int(channel_id)
        ).exists()
        if not channel:
            return {"error": "channel_not_found"}

        event = channel.live_calendar_id.exists()
        if not event:
            return {"error": "calendar_event_not_found"}

        return {
            "channel": channel.id,
            "event": event.id,
            "register": event.register_id.id or False,
            "sheet": event.sheet_id.id or False,
        }
