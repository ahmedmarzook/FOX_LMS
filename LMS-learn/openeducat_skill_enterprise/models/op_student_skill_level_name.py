# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class OpStudentSkillLevelName(models.Model):
    _name = "op.student.skill.level.name"
    _description = "Student Skill Level Name"
    _order = "progress, name"

    name = fields.Char(required=True, translate=True)
    progress = fields.Integer(required=True)

    @api.constrains("progress")
    def _check_progress(self):
        for record in self:
            if not 0 <= record.progress <= 100:
                raise ValidationError("Progress must be between 0 and 100.")
