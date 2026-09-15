from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    logs_line = fields.One2many(
        "channel.logs",
        "meeting_id",
        string="Channel Logs",
    )
    guest_line = fields.One2many(
        "meeting.guest",
        "meeting_guest_id",
        string="Guest Logs",
    )
    total_guest = fields.Integer(
        string="Total Guests",
        compute="_compute_live_kpis",
        store=True,
    )
    total_student = fields.Integer(
        string="Total Participants",
        compute="_compute_live_kpis",
        store=True,
    )
    total_member = fields.Integer(
        string="Total Members",
        compute="_compute_live_kpis",
        store=True,
    )
    meeting_start_time = fields.Datetime(string="Meeting Start Time")
    meeting_end_time = fields.Datetime(string="Meeting End Time")
    meeting_duration = fields.Float(
        string="Meeting Duration",
        compute="_compute_live_duration",
        store=True,
    )
    meeting_attentive_percentage = fields.Float(
        string="Meeting Attentiveness",
        compute="_compute_live_kpis",
        store=True,
        digits=(16, 2),
    )
    live_meeting_ended = fields.Boolean(
        string="Live Meeting Ended",
        default=False,
    )

    @api.depends("meeting_start_time", "meeting_end_time")
    def _compute_live_duration(self):
        for event in self:
            if event.meeting_start_time and event.meeting_end_time:
                delta = event.meeting_end_time - event.meeting_start_time
                event.meeting_duration = delta.total_seconds() / 3600.0
            else:
                event.meeting_duration = 0.0

    @api.depends(
        "logs_line",
        "logs_line.attentive_percentage",
        "guest_line",
    )
    def _compute_live_kpis(self):
        for event in self:
            percentages = event.logs_line.mapped("attentive_percentage")
            event.total_student = len(event.logs_line)
            event.total_guest = len(event.guest_line)
            event.total_member = event.total_student + event.total_guest
            event.meeting_attentive_percentage = (
                sum(percentages) / len(percentages)
                if percentages
                else 0.0
            )

    def action_end_live_meeting(self):
        for event in self:
            now = fields.Datetime.now()
            open_logs = event.logs_line.mapped("visibility_line").filtered(
                lambda log: not log.end_time
            )
            open_logs.write({"end_time": now})
            event.write({
                "meeting_start_time": event.meeting_start_time or event.start,
                "meeting_end_time": now,
                "stop": now,
                "live_meeting_ended": True,
            })
        return True


class ChannelLogs(models.Model):
    _name = "channel.logs"
    _description = "Live Meeting Participant Log"
    _order = "join_time desc"

    partner_id = fields.Many2one(
        "res.partner",
        string="Attendee",
        required=True,
        ondelete="cascade",
    )
    join_time = fields.Datetime(
        string="Joining Time",
        default=fields.Datetime.now,
    )
    meeting_id = fields.Many2one(
        "calendar.event",
        string="Meeting",
        required=True,
        ondelete="cascade",
    )
    visibility_line = fields.One2many(
        "log.attentive",
        "logs_id",
        string="Attention Loss Intervals",
    )
    total_time = fields.Float(
        string="Unfocused Time (Seconds)",
        compute="_compute_total_time",
        store=True,
    )
    attentive_percentage = fields.Float(
        string="Attentiveness Percentage",
        compute="_compute_attentive_percentage",
        store=True,
        digits=(16, 2),
    )
    raised_hand = fields.Integer(string="Raised Hand Count")

    _sql_constraints = [
        (
            "unique_partner_meeting",
            "unique(partner_id, meeting_id)",
            "A participant can only have one log per meeting.",
        ),
    ]

    @api.depends("visibility_line.time_log")
    def _compute_total_time(self):
        for record in self:
            record.total_time = sum(record.visibility_line.mapped("time_log"))

    @api.depends(
        "total_time",
        "meeting_id.meeting_start_time",
        "meeting_id.meeting_end_time",
        "meeting_id.start",
        "meeting_id.stop",
    )
    def _compute_attentive_percentage(self):
        for record in self:
            start = record.meeting_id.meeting_start_time or record.meeting_id.start
            end = record.meeting_id.meeting_end_time or record.meeting_id.stop
            if not start or not end or end <= start:
                record.attentive_percentage = 100.0
                continue
            duration = (end - start).total_seconds()
            unfocused = min(record.total_time, duration)
            record.attentive_percentage = max(
                0.0,
                100.0 * (duration - unfocused) / duration,
            )


class MeetingGuest(models.Model):
    _name = "meeting.guest"
    _description = "Live Meeting Guest"

    guest = fields.Char(string="Guest", required=True)
    meeting_guest_id = fields.Many2one(
        "calendar.event",
        string="Meeting",
        required=True,
        ondelete="cascade",
    )


class LogAttentive(models.Model):
    _name = "log.attentive"
    _description = "Meeting Attentiveness Interval"
    _order = "start_time desc"

    start_time = fields.Datetime(
        string="Start Time",
        required=True,
        default=fields.Datetime.now,
    )
    end_time = fields.Datetime(string="End Time")
    logs_id = fields.Many2one(
        "channel.logs",
        string="Participant Log",
        required=True,
        ondelete="cascade",
    )
    time_log = fields.Float(
        string="Time (Seconds)",
        compute="_compute_time_log",
        store=True,
    )

    @api.depends("start_time", "end_time")
    def _compute_time_log(self):
        for record in self:
            if record.start_time and record.end_time:
                record.time_log = max(
                    0.0,
                    (record.end_time - record.start_time).total_seconds(),
                )
            else:
                record.time_log = 0.0
