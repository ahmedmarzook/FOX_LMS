# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import api, fields, models


class StudentProgression(models.Model):
    _inherit = "op.student.progression"

    marksheet_lines = fields.One2many(
        comodel_name="op.marksheet.line",
        inverse_name="progression_id",
        string="Progression Marksheet",
    )
    total_marksheet_line = fields.Integer(
        string="Total Marksheet",
        compute="_compute_calculate_total_marksheet_line",
        store=True,
    )

    @api.depends("marksheet_lines")
    def _compute_calculate_total_marksheet_line(self):
        for record in self:
            record.total_marksheet_line = len(record.marksheet_lines)
