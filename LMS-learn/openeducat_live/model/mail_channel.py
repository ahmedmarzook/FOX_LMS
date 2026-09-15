from secrets import choice

from odoo import fields, models


class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    live_meeting_locked = fields.Boolean(string="Lock Meeting")
    live_password_locked = fields.Boolean(
        string="Lock Password",
        default=True,
    )
    live_password = fields.Char(string="Meeting Password")
    live_user_id = fields.Integer(string="Temporary User ID")
    live_sheet_id = fields.Integer(string="Sheet ID")
    live_calendar_id = fields.Many2one(
        "calendar.event",
        string="Calendar Event",
        ondelete="set null",
    )

    def _live_set_meeting_lock(self, locked):
        self.write({"live_meeting_locked": bool(locked)})

    def _live_set_password_lock(self, locked):
        self.write({"live_password_locked": bool(locked)})

    def _live_add_user(self, values):
        user_id = (values or {}).get("users_id")
        if user_id:
            self.write({"live_user_id": int(user_id)})

    def _live_add_sheet(self, sheet_id):
        self.write({"live_sheet_id": int(sheet_id or 0)})

    def _live_create_password(self):
        password = "".join(
            choice("abcdefghijkmnopqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ23456789")
            for _index in range(10)
        )
        self.write({
            "live_password": password,
            "live_password_locked": True,
        })
        return password


class DiscussChannelMember(models.Model):
    _inherit = "discuss.channel.member"

    live_is_host = fields.Boolean(string="Meeting Host")
