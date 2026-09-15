# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class ScholarshipStages(models.Model):
    _name = "scholarship.stages"
    _description = "Scholarship Stage"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string="Folded in Kanban")
