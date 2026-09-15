from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpQuiz(models.Model):
    _inherit = "op.quiz"

    face_tracking = fields.Boolean(string="Face Tracking")
    warning_limit = fields.Integer(string="Warning Limit", default=5)
    warning_state = fields.Selection(
        [
            ("open", "In-Progress After Warning"),
            ("hold", "Permission From Admin"),
            ("submit", "Submit"),
        ],
        string="Warning State",
        default="hold",
        required=True,
    )
    face_sensitivity = fields.Float(string="Sensitivity", default=0.3)
    copy_paste_allow = fields.Boolean(string="Copy/Paste Allow")
    question_time_out = fields.Integer(string="Question Time Out")
    take_screenshot = fields.Selection(
        [
            ("random", "Random"),
            ("time_interval", "Time Interval"),
        ],
        string="Take Screenshot",
    )
    particular_interval = fields.Integer(
        string="Take Screenshots",
        default=1,
    )
    random_start = fields.Integer(string="Start", default=1)
    random_end = fields.Integer(string="End", default=2)

    @api.constrains("face_sensitivity")
    def _check_face_sensitivity(self):
        for quiz in self:
            if not 0 < quiz.face_sensitivity < 1:
                raise ValidationError(
                    _("Sensitivity must be between 0 and 1.")
                )

    @api.constrains("warning_limit")
    def _check_warning_limit(self):
        for quiz in self:
            if quiz.warning_limit < 5:
                raise ValidationError(
                    _("Warning limit cannot be less than 5.")
                )

    @api.constrains("question_time_out")
    def _check_question_time_out(self):
        for quiz in self:
            if quiz.question_time_out < 0:
                raise ValidationError(
                    _("Question time out must be positive.")
                )

    @api.constrains("particular_interval", "take_screenshot")
    def _check_particular_interval(self):
        for quiz in self:
            if (
                quiz.take_screenshot == "time_interval"
                and quiz.particular_interval < 1
            ):
                raise ValidationError(
                    _("Screenshot interval must be greater than 0.")
                )

    @api.constrains("random_start", "random_end", "take_screenshot")
    def _check_random_interval(self):
        for quiz in self:
            if quiz.take_screenshot != "random":
                continue
            if quiz.random_start < 1 or quiz.random_end < 1:
                raise ValidationError(
                    _("Screenshot interval must be greater than 0.")
                )
            if quiz.random_start >= quiz.random_end:
                raise ValidationError(
                    _("Start time must be less than end time.")
                )


class OpQuizResult(models.Model):
    _inherit = "op.quiz.result"

    warning_line_ids = fields.One2many(
        "op.quiz.result.warning",
        "result_id",
        string="Warning Lines",
        copy=False,
    )


class OpQuizResultWarning(models.Model):
    _name = "op.quiz.result.warning"
    _description = "Quiz Anti-Cheating Warning"
    _order = "warning_no, id"

    result_id = fields.Many2one(
        "op.quiz.result",
        string="Result",
        required=True,
        ondelete="cascade",
        index=True,
    )
    warning_no = fields.Integer(string="Warning Number", required=True)
    warning_name = fields.Char(string="Name", required=True)
    time = fields.Char(string="Time")
    warning_attachment = fields.Binary(
        string="Attachment",
        attachment=True,
    )
