from odoo import _, http
from odoo.exceptions import UserError
from odoo.http import request


class WebData(http.Controller):

    @http.route("/quiz/config", type="jsonrpc", auth="user", website=True)
    def anti_cheating(self, result_id, **kwargs):
        if not result_id:
            return {}

        record_id = int(result_id)
        result = request.env["op.quiz.result"].sudo().browse(record_id).exists()
        quiz = (
            result.quiz_id
            if result
            else request.env["op.quiz"].sudo().browse(record_id).exists()
        )
        if not quiz:
            return {}

        return {
            "face_tracking": int(bool(quiz.face_tracking)),
            "copy_paste_allow": int(bool(quiz.copy_paste_allow)),
            "take_screenshot": (
                1 if quiz.take_screenshot == "time_interval" else 0
            ),
            "question_count": len(quiz.line_ids),
            "question_time_out": quiz.question_time_out,
            "warning_limit": quiz.warning_limit,
            "warning_state": quiz.warning_state,
            "sensitivity": quiz.face_sensitivity,
            "random_start": quiz.random_start,
            "random_end": quiz.random_end,
            "result_warning_state": quiz.state,
            "particular_interval": quiz.particular_interval,
        }

    @http.route("/check/state", type="jsonrpc", auth="user", website=True)
    def check_state(self, result_id):
        result = request.env["op.quiz.result"].sudo().browse(
            int(result_id)
        ).exists()
        return {"state": result.state} if result and result.state == "hold" else False

    @http.route("/quiz/hold", type="http", auth="public", website=True)
    def cancel(self):
        return request.render("openeducat_quiz_anti_cheating.quiz_hold")

    @http.route(
        "/create/attachment",
        type="jsonrpc",
        auth="user",
        website=True,
    )
    def create_attachment(self, file, file_name, name=None, exam=None):
        result = request.env["op.quiz.result"].sudo().browse(
            int(exam)
        ).exists()
        if not result:
            return False

        request.env["ir.attachment"].sudo().create({
            "name": file_name or name or "Quiz screenshot",
            "type": "binary",
            "datas": file,
            "res_model": "op.quiz.result",
            "res_id": result.id,
        })
        return True

    @http.route(
        "/warning/quite",
        type="jsonrpc",
        auth="user",
        website=True,
    )
    def warning_quite(self, result_id, warning_state):
        result = request.env["op.quiz.result"].sudo().browse(
            int(result_id)
        ).exists()
        if result:
            result.write({"state": warning_state})
        return bool(result)

    @http.route("/camera/access", type="jsonrpc", auth="user", website=True)
    def camera_access(self):
        raise UserError(_("Camera access required."))

    @http.route(
        "/warning/line",
        type="jsonrpc",
        auth="user",
        website=True,
    )
    def create_warning_line(
        self,
        warning_no,
        w_name,
        result_id,
        time,
        file,
        **kwargs,
    ):
        result = request.env["op.quiz.result"].sudo().browse(
            int(result_id)
        ).exists()
        if not result:
            return False

        request.env["op.quiz.result.warning"].sudo().create({
            "result_id": result.id,
            "warning_no": int(warning_no or 0),
            "warning_name": w_name,
            "time": time,
            "warning_attachment": file,
        })
        return True
