# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from secrets import choice
from string import digits

from odoo import _, api, exceptions, fields, models


class OpStudent(models.Model):
    _inherit = "op.student"

    @api.model
    def _default_random_barcode(self):
        return "".join(choice(digits) for _ in range(8))

    barcode = fields.Char(
        string="Badge ID",
        help="ID used for student identification",
        default=_default_random_barcode,
        copy=False,
        index=True,
    )
    pin = fields.Char(
        string="PIN",
        default="0000",
        help="PIN used to sign in from Kiosk Mode",
        copy=False,
    )
    attendance_ids = fields.One2many(
        "op.attendance.line",
        "student_id",
        string="Attendances",
    )
    last_attendance_id = fields.Many2one(
        "op.attendance.line",
        compute="_compute_last_attendance_id",
    )

    _sql_constraints = [
        (
            "barcode_uniq",
            "unique(barcode)",
            "The Badge ID must be unique.",
        ),
    ]

    def generate_random_barcode(self):
        for student in self:
            student.barcode = "".join(choice(digits) for _ in range(8))

    @api.model
    def attendance_scan(self, barcode):
        student = self.search([("barcode", "=", barcode)], limit=1)
        if student and student.course_detail_ids:
            return {
                "student_id": student.id,
                "student_name": student.name,
            }
        return {
            "warning": _(
                "No student corresponding to barcode %(barcode)s",
                barcode=barcode,
            ),
        }

    @api.model
    def get_attendance_sheets(self, student_id):
        student = self.browse(int(student_id)).exists()
        if not student:
            return [{}, {}]

        sheets = {}
        for course_detail in student.course_detail_ids:
            registers = self.env["op.attendance.register"].search([
                ("course_id", "=", course_detail.course_id.id),
                ("batch_id", "=", course_detail.batch_id.id),
            ])
            open_sheets = self.env["op.attendance.sheet"].search([
                ("register_id", "in", registers.ids),
                ("state", "=", "start"),
            ])
            for sheet in open_sheets:
                attended_student_ids = sheet.attendance_line.mapped("student_id").ids
                if student.id not in attended_student_ids:
                    sheets[sheet.id] = sheet.name

        selected_id = max(sheets) if sheets else False
        return [sheets, {"is_selected": selected_id}]

    @api.depends("attendance_ids", "attendance_ids.check_in")
    def _compute_last_attendance_id(self):
        for student in self:
            student.last_attendance_id = self.env["op.attendance.line"].search(
                [("student_id", "=", student.id)],
                order="check_in desc, id desc",
                limit=1,
            )

    @api.constrains("pin")
    def _verify_pin(self):
        for student in self:
            if student.pin and not student.pin.isdigit():
                raise exceptions.ValidationError(
                    _("The PIN must be a sequence of digits.")
                )

    def attendance_manual(self, next_action, entered_pin=None, att_id=0):
        self.ensure_one()
        if entered_pin != self.pin:
            return {"warning": _("Wrong PIN")}
        return self.attendance_action(next_action, att_id)

    def attendance_action(self, next_action, att_id=0):
        self.ensure_one()
        action = self.env.ref(
            "openeducat_student_attendance_enterprise."
            "student_attendance_action_greeting_message"
        ).sudo().read()[0]
        action.update({
            "previous_attendance_change_date": (
                self.last_attendance_id.check_in
                if self.last_attendance_id
                else False
            ),
            "student_name": self.name,
            "barcode": self.barcode,
            "next_action": next_action,
        })

        student = self.with_user(self.user_id) if self.user_id else self
        attendance = student.sudo().attendance_action_change(att_id)
        action["attendance"] = attendance.sudo().read()[0]
        return {"action": action}

    def attendance_action_change(self, att_id=0):
        self.ensure_one()
        return self.env["op.attendance.line"].sudo().create({
            "student_id": self.id,
            "check_in": fields.Datetime.now(),
            "attendance_id": int(att_id) if att_id else False,
        })
