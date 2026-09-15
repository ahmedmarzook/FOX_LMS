# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpAssignment(models.Model):
    _inherit = "op.assignment"

    rubric_template_id = fields.Many2one(
        "op.rubric.template",
        string="Rubrics Template",
        domain="[('state', '=', 'in_use')]",
        ondelete="restrict",
    )

    @api.constrains(
        "rubric_template_id",
        "point",
        "rubric_template_id.rubric_element_line",
        "rubric_template_id.rubric_element_line.point",
        "rubric_template_id.rubric_element_line.percentage",
    )
    def _check_rubric_distribution(self):
        for record in self:
            template = record.rubric_template_id
            if not template:
                continue

            if template.rubrics_type == "points":
                total = sum(template.rubric_element_line.mapped("point"))
                if not fields.Float.is_zero(
                    total - record.point,
                    precision_digits=2,
                ):
                    raise ValidationError(
                        _(
                            "The rubric points total must equal the assignment "
                            "points. Rubric total: %(rubric)s, assignment "
                            "points: %(assignment)s.",
                            rubric=total,
                            assignment=record.point,
                        )
                    )

            elif template.rubrics_type == "percent":
                total = sum(
                    template.rubric_element_line.mapped("percentage")
                )
                if not fields.Float.is_zero(
                    total - 100.0,
                    precision_digits=2,
                ):
                    raise ValidationError(
                        _(
                            "The rubric percentage total must equal 100%%. "
                            "Current total: %(total)s%%.",
                            total=total,
                        )
                    )
