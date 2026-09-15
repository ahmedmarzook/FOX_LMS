# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class OpStudentSkillAssessmentLine(models.Model):
    _name = "op.student.skill.assessment.line"
    _description = "Student Skill Assessment Line"
    _rec_name = "student_skill_id"
    _order = "student_skill_id"

    student_skill_type_id = fields.Many2one(
        "op.student.skill.type",
        string="Skill Assessment Type",
        required=True,
        ondelete="cascade",
    )
    student_skill_id = fields.Many2one(
        "op.student.skill",
        string="Skill",
        domain="[('student_skill_type_id', '=', student_skill_type_id)]",
        required=True,
        ondelete="cascade",
    )
    student_skill_level_id = fields.Many2one(
        "op.student.skill.level",
        string="Skill Level",
        domain="[('student_skill_type_id', '=', student_skill_type_id)]",
        required=True,
        ondelete="restrict",
    )
    student_skill_assessment_id = fields.Many2one(
        "op.student.skill.assessment",
        string="Assessment",
        required=True,
        ondelete="cascade",
        index=True,
    )
    progress = fields.Integer(
        related="student_skill_level_id.progress",
        store=True,
        readonly=True,
    )
