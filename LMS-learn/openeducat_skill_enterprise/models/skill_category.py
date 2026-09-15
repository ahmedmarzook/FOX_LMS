# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class OpSkillCategory(models.Model):
    _name = "op.skill.category"
    _description = "Skills Category"
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
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "skill_category_code_company_unique",
            "unique(code, company_id)",
            "The skill category code must be unique per company.",
        ),
    ]
