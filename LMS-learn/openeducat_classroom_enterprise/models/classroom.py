# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class OpClassroom(models.Model):
    _inherit = "op.classroom"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        index=True,
    )
