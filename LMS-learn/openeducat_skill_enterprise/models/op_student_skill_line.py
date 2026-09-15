# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class OpStudentSkillLine(models.Model):
    _name = "op.student.skill.line"
    _description = "Student Skill Line"
    _rec_name = "student_skills_id"
    _order = "student_skill_type_id, student_skills_id"

    student_id = fields.Many2one(
        "op.student",
        required=True,
        ondelete="cascade",
        index=True,
    )
    student_skill_type_id = fields.Many2one(
        "op.student.skill.type",
        required=True,
        string="Skill Type",
        ondelete="restrict",
    )
    student_skills_id = fields.Many2one(
        "op.student.skill",
        required=True,
        domain="[('student_skill_type_id', '=', student_skill_type_id)]",
        string="Skill",
        ondelete="restrict",
    )
    student_skill_level_id = fields.Many2one(
        "op.student.skill.level",
        required=True,
        domain="[('student_skill_type_id', '=', student_skill_type_id)]",
        string="Skill Level",
        ondelete="restrict",
    )
    progress = fields.Integer(
        related="student_skill_level_id.progress",
        store=True,
        readonly=True,
    )

    _sql_constraints = [
        (
            "student_skill_unique",
            "unique(student_id, student_skills_id)",
            "A skill can only be added once for each student.",
        ),
    ]
