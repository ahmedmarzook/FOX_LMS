# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpAssignmentSubLine(models.Model):
    _inherit = "op.assignment.sub.line"

    rubric_element_line = fields.One2many(
        "op.assignment.rubric.sub.line",
        "assignment_sub_id",
        string="Rubric Elements",
        copy=True,
    )
    state = fields.Selection(
        selection_add=[("to_assess", "To Assess")],
        ondelete={"to_assess": "set default"},
    )

    def act_to_assess(self):
        for record in self:
            record.state = "to_assess"
            template = record.assignment_id.rubric_template_id
            if not template:
                continue

            existing_elements = record.rubric_element_line.mapped(
                "rubric_element_id"
            )
            commands = []
            for element in template.rubric_element_line:
                if element in existing_elements:
                    continue

                maximum = 0.0
                if element.rubrics_type == "points":
                    maximum = element.point
                elif element.rubrics_type == "percent":
                    maximum = element.percentage

                commands.append(
                    (
                        0,
                        0,
                        {
                            "rubric_element_id": element.id,
                            "rubrics_type": element.rubrics_type,
                            "maximum": maximum,
                        },
                    )
                )

            if commands:
                record.write({"rubric_element_line": commands})
        return True

    def act_accept(self):
        for record in self:
            template = record.assignment_id.rubric_template_id
            if template:
                if template.rubrics_type == "points":
                    record.marks = sum(
                        record.rubric_element_line.mapped("point")
                    )
                elif template.rubrics_type == "percent":
                    percentage = sum(
                        record.rubric_element_line.mapped("percentage")
                    )
                    record.marks = (
                        record.assignment_id.point * percentage / 100.0
                    )
        return super().act_accept()


class OpAssignmentRubricSubLine(models.Model):
    _name = "op.assignment.rubric.sub.line"
    _description = "Assignment Rubric Sub Line"
    _order = "id"

    rubric_element_id = fields.Many2one(
        "op.rubric.element",
        string="Element",
        required=True,
        ondelete="restrict",
    )
    assignment_sub_id = fields.Many2one(
        "op.assignment.sub.line",
        string="Assignment Submission",
        required=True,
        ondelete="cascade",
        index=True,
    )
    marks = fields.Integer(string="Marks")
    rubrics_type = fields.Selection(
        [
            ("no_points", "No Points"),
            ("points", "Points"),
            ("percent", "Percent"),
        ],
        string="Rubrics Type",
        default="points",
        required=True,
    )
    maximum = fields.Float(string="Out of", readonly=True)
    point = fields.Float(string="Point")
    percentage = fields.Float(string="Percentage")

    @api.constrains("point", "percentage", "rubric_element_id")
    def _check_scores(self):
        for record in self:
            if record.point < 0 or record.percentage < 0:
                raise ValidationError(
                    _("Rubric scores cannot be negative.")
                )

            if (
                record.rubrics_type == "points"
                and record.point > record.rubric_element_id.point
            ):
                raise ValidationError(
                    _(
                        "The given point must not exceed %(maximum)s for "
                        "%(element)s.",
                        maximum=record.rubric_element_id.point,
                        element=record.rubric_element_id.name,
                    )
                )

            if (
                record.rubrics_type == "percent"
                and record.percentage
                > record.rubric_element_id.percentage
            ):
                raise ValidationError(
                    _(
                        "The given percentage must not exceed %(maximum)s%% "
                        "for %(element)s.",
                        maximum=record.rubric_element_id.percentage,
                        element=record.rubric_element_id.name,
                    )
                )
