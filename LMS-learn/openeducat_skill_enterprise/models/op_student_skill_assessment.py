# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpStudentSkillAssessment(models.Model):
    _name = "op.student.skill.assessment"
    _description = "Student Skill Assessment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        string="Name",
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _("New"),
        tracking=True,
    )
    student_skill_type_id = fields.Many2one(
        "op.student.skill.type",
        string="Skill Assessment Type",
        required=True,
        tracking=True,
    )
    date = fields.Date(
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    student_id = fields.Many2one(
        "op.student",
        required=True,
        tracking=True,
        ondelete="cascade",
    )
    user_id = fields.Many2one(
        "res.users",
        string="Assessed By",
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    student_skill_assessment_line = fields.One2many(
        "op.student.skill.assessment.line",
        "student_skill_assessment_id",
        string="Skills",
        copy=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("schedule", "Scheduled"),
            ("cancel", "Cancelled"),
            ("done", "Done"),
        ],
        string="State",
        default="draft",
        required=True,
        tracking=True,
    )

    @api.onchange("student_skill_type_id")
    def _onchange_student_skill_type_id(self):
        for assessment in self:
            commands = [(5, 0, 0)]
            if assessment.student_skill_type_id:
                commands.extend(
                    (
                        0,
                        0,
                        {
                            "student_skill_id": skill.id,
                            "student_skill_type_id": assessment.student_skill_type_id.id,
                        },
                    )
                    for skill in assessment.student_skill_type_id.student_skills_line
                )
            assessment.student_skill_assessment_line = commands

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code(
                        "op.student.skill.assessment"
                    )
                    or _("New")
                )
        return super().create(vals_list)

    def act_draft(self):
        self.write({"state": "draft"})

    def act_schedule(self):
        self.write({"state": "schedule"})

    def act_done(self):
        for assessment in self:
            if not assessment.student_skill_assessment_line:
                raise ValidationError(
                    _("Add at least one skill before completing the assessment.")
                )

            existing_lines = {
                line.student_skills_id.id: line
                for line in assessment.student_id.student_skill_line
            }
            create_commands = []

            for assessment_line in assessment.student_skill_assessment_line:
                values = {
                    "student_skill_type_id": assessment.student_skill_type_id.id,
                    "student_skills_id": assessment_line.student_skill_id.id,
                    "student_skill_level_id": assessment_line.student_skill_level_id.id,
                }
                existing_line = existing_lines.get(
                    assessment_line.student_skill_id.id
                )
                if existing_line:
                    existing_line.write(values)
                else:
                    create_commands.append((0, 0, values))

            if create_commands:
                assessment.student_id.write(
                    {"student_skill_line": create_commands}
                )
            assessment.state = "done"

    def act_cancel(self):
        self.write({"state": "cancel"})
