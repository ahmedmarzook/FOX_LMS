from odoo import fields, models


class OpJobPost(models.Model):
    _inherit = "op.job.post"

    alumni_student_id = fields.Many2one(
        "op.student",
        string="Alumni Owner",
        copy=False,
        index=True,
        ondelete="set null",
    )
