# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpRubricsTemplate(models.Model):
    _name = "op.rubric.template"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Rubrics Template Configuration"
    _order = "name"

    name = fields.Char(string="Name", required=True, tracking=True)
    rubric_element_line = fields.One2many(
        "op.rubric.element",
        "rubrics_template_id",
        string="Rubrics Elements",
        copy=True,
    )
    rubrics_type = fields.Selection(
        [
            ("no_points", "No Points"),
            ("points", "Points"),
            ("percent", "Percent"),
        ],
        string="Rubrics Type",
        default="points",
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_use", "In Use"),
            ("cancel", "Cancelled"),
        ],
        string="State",
        default="draft",
        required=True,
        tracking=True,
    )

    def act_in_use(self):
        for record in self:
            if not record.rubric_element_line:
                raise ValidationError(
                    _("Add at least one rubric element before using a template.")
                )

            if record.rubrics_type == "percent":
                total = sum(
                    record.rubric_element_line.mapped("percentage")
                )
                if not fields.Float.is_zero(
                    total - 100.0,
                    precision_digits=2,
                ):
                    raise ValidationError(
                        _(
                            "The distributed percentage must equal 100%%. "
                            "Current total: %(total)s%%.",
                            total=total,
                        )
                    )

            record.state = "in_use"
        return True

    def act_cancel(self):
        self.write({"state": "cancel"})
        return True

    def act_re_open(self):
        self.write({"state": "draft"})
        return True

    @api.onchange("rubrics_type")
    def _onchange_rubrics_type(self):
        for record in self:
            for element in record.rubric_element_line:
                if record.rubrics_type != "points":
                    element.point = 0.0
                if record.rubrics_type != "percent":
                    element.percentage = 0.0
