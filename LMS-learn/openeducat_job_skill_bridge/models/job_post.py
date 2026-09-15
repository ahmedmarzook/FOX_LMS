# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpJobPost(models.Model):
    _inherit = "op.job.post"

    skill_ids = fields.Many2many(
        "op.student.skill.name",
        string="Skills",
    )


class OpSkillLine(models.Model):
    _name = "op.skill.line"
    _description = "Student Self-Assessed Skill"
    _order = "student_id, skill_type_id"
    _rec_name = "skill_type_id"

    skill_type_id = fields.Many2one(
        "op.student.skill.name",
        string="Skill",
        required=True,
        ondelete="restrict",
        domain="[('self_assessed', '=', True)]",
    )
    student_id = fields.Many2one(
        "op.student",
        string="Student",
        required=True,
        ondelete="cascade",
        index=True,
    )
    level_id = fields.Many2one(
        "op.student.skill.level.name",
        string="Level",
        required=True,
        ondelete="restrict",
    )
    progress = fields.Integer(
        related="level_id.progress",
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        ondelete="cascade",
        index=True,
    )

    @api.constrains("progress")
    def _check_progress(self):
        for record in self:
            if not 0 <= record.progress <= 100:
                raise ValidationError(
                    _("Skill progress must be between 0 and 100.")
                )

    _sql_constraints = [
        (
            "student_self_assessed_skill_unique",
            "unique(student_id, skill_type_id)",
            "The same self-assessed skill cannot be added twice for a student.",
        ),
    ]


class OpStudent(models.Model):
    _inherit = "op.student"

    skill_line = fields.One2many(
        "op.skill.line",
        "student_id",
        string="Self-Assessed Skills",
        copy=True,
    )
