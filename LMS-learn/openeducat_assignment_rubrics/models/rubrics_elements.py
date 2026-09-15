# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class OpRubricsElements(models.Model):
    _name = "op.rubric.element"
    _description = "Rubrics Element"
    _order = "id"

    name = fields.Char(string="Name", required=True, translate=True)
    rubrics_type = fields.Selection(
        related="rubrics_template_id.rubrics_type",
        store=True,
        readonly=True,
    )
    rubrics_template_id = fields.Many2one(
        "op.rubric.template",
        string="Rubric Template",
        required=True,
        ondelete="cascade",
        index=True,
    )
    description = fields.Text(string="Feedback", translate=True)
    point = fields.Float(string="Point")
    percentage = fields.Float(string="Percentage")

    @api.constrains("point", "percentage")
    def _check_values(self):
        for record in self:
            if record.point < 0 or record.percentage < 0:
                raise ValidationError(
                    "Rubric points and percentages cannot be negative."
                )
            if record.percentage > 100:
                raise ValidationError(
                    "Rubric percentage cannot exceed 100%."
                )
