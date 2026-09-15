# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class OpStudentSkillName(models.Model):
    _name = "op.student.skill.name"
    _description = "Student Skill Name"
    _order = "name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True, index=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
        ondelete="cascade",
    )
    skill_category_type_id = fields.Many2one(
        "op.skill.category",
        string="Skill Type",
        required=True,
        ondelete="restrict",
    )
    active = fields.Boolean(default=True)
    self_assessed = fields.Boolean()

    _sql_constraints = [
        (
            "skill_name_code_company_unique",
            "unique(code, company_id)",
            "The skill code must be unique per company.",
        ),
    ]
