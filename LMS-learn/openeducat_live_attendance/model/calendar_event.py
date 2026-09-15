from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    register_id = fields.Many2one(
        "op.attendance.register",
        string="Attendance Register",
    )
    sheet_id = fields.Many2one(
        "op.attendance.sheet",
        string="Attendance Sheet",
        domain="[('register_id', '=', register_id)]",
    )

    @api.onchange("register_id")
    def _onchange_register_id(self):
        if not self.register_id:
            self.sheet_id = False
            return {
                "domain": {
                    "sheet_id": [],
                    "subject_id": [],
                }
            }

        self.course_id = self.register_id.course_id
        self.batch_id = self.register_id.batch_id
        if self.register_id.subject_id:
            self.subject_id = self.register_id.subject_id

        sheets = self.env["op.attendance.sheet"].search(
            [("register_id", "=", self.register_id.id)],
            order="attendance_date desc, id desc",
        )
        self.sheet_id = sheets[:1]
        return {
            "domain": {
                "sheet_id": [("id", "in", sheets.ids)],
                "subject_id": [
                    ("id", "in", self.course_id.subject_ids.ids)
                ],
            }
        }

    @api.onchange("sheet_id")
    def _onchange_sheet_id(self):
        if self.sheet_id and self.sheet_id.register_id != self.register_id:
            self.register_id = self.sheet_id.register_id

    def write(self, vals):
        result = super().write(vals)
        for event in self:
            if event.channel_id:
                event.channel_id.live_sheet_id = event.sheet_id.id or 0
        return result

    @api.model_create_multi
    def create(self, vals_list):
        events = super().create(vals_list)
        for event in events:
            if event.channel_id:
                event.channel_id.live_sheet_id = event.sheet_id.id or 0
        return events


class OpAttendanceSheet(models.Model):
    _inherit = "op.attendance.sheet"

    attendance_sheet_date = fields.Char(
        string="Attendance Sheet Date",
        compute="_compute_attendance_sheet_date",
    )
    date_time = fields.Datetime(
        string="Date Time",
        default=fields.Datetime.now,
    )

    @api.depends("name", "attendance_date", "date_time")
    def _compute_attendance_sheet_date(self):
        for record in self:
            date_value = record.attendance_date or fields.Date.context_today(record)
            record.attendance_sheet_date = (
                f"{record.name or ''} "
                f"{fields.Date.to_string(date_value)}"
            ).strip()
