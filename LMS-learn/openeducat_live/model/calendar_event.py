from secrets import choice

from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    is_start_meeting = fields.Boolean(string="Meeting Started", default=False)
    is_password = fields.Char(string="Meeting Password")
    is_meeting = fields.Boolean(string="Create Live Meeting", default=False)
    channel_id = fields.Many2one(
        "discuss.channel",
        string="Discuss Channel",
        ondelete="set null",
    )
    course_id = fields.Many2one("op.course", string="Course")
    subject_id = fields.Many2one("op.subject", string="Subject")
    batch_id = fields.Many2one("op.batch", string="Batch")

    def _generate_live_password(self):
        return "".join(
            choice("abcdefghijkmnopqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ23456789")
            for _index in range(10)
        )

    def _live_channel_url(self):
        self.ensure_one()
        if not self.channel_id:
            return False
        invitation_url = self.channel_id.invitation_url
        if invitation_url:
            if invitation_url.startswith("http"):
                return invitation_url
            return f"{self.get_base_url()}{invitation_url}"
        return f"{self.get_base_url()}/discuss/channel/{self.channel_id.id}"

    def _ensure_live_channel(self):
        for event in self:
            if not event.is_meeting:
                continue
            if not event.channel_id:
                password = event.is_password or event._generate_live_password()
                channel = self.env["discuss.channel"].create({
                    "name": event.name or "Live Meeting",
                    "channel_type": "channel",
                    "default_display_mode": "video_full_screen",
                    "live_password": password,
                    "live_password_locked": True,
                })
                event.with_context(skip_live_sync=True).write({
                    "channel_id": channel.id,
                    "is_password": password,
                })
            event.channel_id.live_calendar_id = event.id

    def _sync_live_members(self):
        for event in self.filtered("channel_id"):
            existing_partner_ids = event.channel_id.channel_member_ids.partner_id.ids
            values = [
                {
                    "channel_id": event.channel_id.id,
                    "partner_id": partner.id,
                    "live_is_host": partner == event.user_id.partner_id,
                }
                for partner in event.partner_ids
                if partner.id not in existing_partner_ids
            ]
            if values:
                self.env["discuss.channel.member"].sudo().create(values)

    def _sync_live_meeting(self):
        for event in self:
            if not event.is_meeting:
                continue
            event._ensure_live_channel()
            url = event._live_channel_url()
            event.with_context(skip_live_sync=True).write({
                "videocall_location": url,
                "online_meeting": True,
                "is_password": event.channel_id.live_password,
            })
            event.channel_id.name = event.name
            event._sync_live_members()
            for attendee in event.attendee_ids:
                attendee.write({
                    "attendee_meeting_url": url,
                    "apw": event.is_password,
                })

    def action_create_meet(self):
        self.ensure_one()
        self._sync_live_meeting()
        self.is_start_meeting = True
        return {
            "type": "ir.actions.act_url",
            "url": self.videocall_location,
            "target": "self",
        }

    @api.onchange("is_meeting")
    def _onchange_is_meeting(self):
        if not self.is_meeting:
            self.videocall_location = False
            self.is_password = False
        elif not self.is_password:
            self.is_password = self._generate_live_password()

    @api.model_create_multi
    def create(self, vals_list):
        events = super().create(vals_list)
        events.filtered("is_meeting")._sync_live_meeting()
        return events

    def write(self, vals):
        result = super().write(vals)
        if not self.env.context.get("skip_live_sync"):
            relevant = {
                "is_meeting",
                "is_password",
                "name",
                "partner_ids",
                "user_id",
                "channel_id",
            }
            if relevant.intersection(vals):
                self.filtered("is_meeting")._sync_live_meeting()
        return result

    def unlink(self):
        channels = self.mapped("channel_id")
        result = super().unlink()
        channels.sudo().unlink()
        return result
