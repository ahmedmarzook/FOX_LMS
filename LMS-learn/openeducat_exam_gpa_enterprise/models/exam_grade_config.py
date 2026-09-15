# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import api, fields, models


class ResultRecords(models.Model):
    _inherit = "op.result.line"

    grade_point = fields.Float(
        string="Grade Point",
        compute="_compute_grade_point",
        store=True,
    )
    credit = fields.Float(
        string="Subject Credit",
        related="exam_id.subject_id.subject_credit",
        store=True,
        readonly=True,
    )
    qp = fields.Float(
        string="Quality Points",
        compute="_compute_qp",
        store=True,
    )

    @api.depends("grade")
    def _compute_grade_point(self):
        configurations = self.env["op.grade.configuration"].search([])
        points_by_grade = {
            configuration.result: configuration.grade_point
            for configuration in configurations
        }
        for record in self:
            record.grade_point = points_by_grade.get(record.grade, 0.0)

    @api.depends("grade_point", "credit")
    def _compute_qp(self):
        for record in self:
            record.qp = record.grade_point * record.credit


class OpeneducatMarksheetLineGpa(models.Model):
    _inherit = "op.marksheet.line"

    total_points = fields.Float(
        string="Total Points",
        compute="_compute_gpa",
        store=True,
    )
    gpa_count = fields.Float(
        string="GPA",
        compute="_compute_gpa",
        store=True,
    )

    @api.depends("result_line.qp", "result_line.credit")
    def _compute_gpa(self):
        for record in self:
            total_points = sum(record.result_line.mapped("qp"))
            total_credit = sum(record.result_line.mapped("credit"))
            record.total_points = total_points
            record.gpa_count = total_points / total_credit if total_credit else 0.0


class OpenducatSubjectCredit(models.Model):
    _inherit = "op.subject"

    subject_credit = fields.Float(
        string="Credit Hours",
        default=5.0,
    )


class OpenducatGradeConfig(models.Model):
    _inherit = "op.grade.configuration"

    grade_point = fields.Float(string="Grade Point")
