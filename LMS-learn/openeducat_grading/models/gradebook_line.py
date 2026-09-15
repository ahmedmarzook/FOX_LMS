# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class GradebookLine(models.Model):
    _name = 'gradebook.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Grade Book Line"
    _rec_name = "gradebook_id"

    academic_year_id = fields.Many2one('op.academic.year', string='Academic Year',
                                       required=True, tracking=True)
    academic_term_id = fields.Many2one('op.academic.term', string='Term',
                                       required=True, tracking=True)
    course_id = fields.Many2one('op.course', string="Course",
                                required=True, tracking=True)
    subject_id = fields.Many2one('op.subject', string="Subject",
                                 tracking=True)
    assignment_type_id = fields.Many2one('grading.assignment.type',
                                         string="Assignment Type",
                                         required=True, tracking=True)
    grade_table_id = fields.Many2one('op.grade.table', string="Grade Table",
                                     tracking=True)
    grade_table_line_id = fields.Many2one('op.grade.table.line',
                                          string="Grade Table Line",
                                          tracking=True)
    gradebook_id = fields.Many2one('gradebook.gradebook', string='Student',
                                   tracking=True)
    percentage = fields.Float('Percentage',
                              compute='_compute_per_by_table_line',
                              default=0.0, store=True)
    grade_assigment_id = fields.Many2one('grading.assignment', 'Assignment',
                                         required=True, tracking=True)
    marks = fields.Float('Marks', tracking=True)
    hide = fields.Boolean(string='Hide', compute='_compute_grade_type')
    hide_sub = fields.Boolean(compute='_compute_assignment_type')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'), ('final', 'Final'), ('in_review', 'In Review'),
            ('cancelled', 'Cancelled')
        ], default='draft', tracking=True
    )
    state_hide = fields.Boolean(string='State Hide', compute='_compute_mark_readonly')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    @api.onchange('grade_table_line_id', 'marks')
    def _compute_per_by_table_line(self):
        for record in self:
            if record.grade_table_line_id:
                record.percentage = record.grade_table_line_id.percentage
                record.grade_table_id = record.grade_table_line_id.grade_table_id
            elif record.marks:
                if record.marks <= record.grade_assigment_id.point:
                    record.percentage = (record.marks * 100 / record.
                                         grade_assigment_id.point)
                else:
                    raise ValidationError(
                        _("Marks should be less than or equal to {}".format(
                            record.grade_assigment_id.point)))

            else:
                record.percentage = 0.0

    @api.onchange('academic_year_id')
    def terms_by_year(self):
        if self.academic_year_id:
            lists = []
            year_id = self.env['op.academic.year'].search([
                ('id', '=', self.academic_year_id.id)])
            for i in year_id.academic_term_ids:
                lists.append(i.id)
            domain = {'academic_term_id': [('id', 'in', lists)]}
            result = {'domain': domain}
            return result

    @api.depends(
        'grade_assigment_id',
        'grade_assigment_id.grade',
        'grade_assigment_id.grade.grade_table_ids',
    )
    def _compute_grade_type(self):
        for record in self:
            record.grade_table_id = record.grade_assigment_id.grade
            record.hide = bool(
                record.grade_table_id and record.grade_table_id.grade_table_ids
            )

    @api.onchange('grade_assigment_id')
    def _onchange_grade_assigment_id(self):
        grade_lines = self.grade_assigment_id.grade.grade_table_ids
        return {'domain': {'grade_table_line_id': [('id', 'in', grade_lines.ids)]}}

    @api.depends('assignment_type_id', 'assignment_type_id.assign_type')
    def _compute_assignment_type(self):
        for record in self:
            record.hide_sub = (
                record.assignment_type_id.assign_type == 'attendance'
            )

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for GradeBook Line'),
            'template': '/openeducat_grading/static/xls/gradebook_line.xls'
        }]

    def action_draft(self):
        for obj in self:
            obj.state = 'draft'
        return True

    def action_final(self):
        for obj in self:
            obj.state = 'final'
        return True

    def action_in_review(self):
        for obj in self:
            obj.state = 'in_review'
        return True

    def action_cancelled(self):
        for obj in self:
            obj.state = 'cancelled'
        return True

    @api.depends('grade_assigment_id', 'grade_assigment_id.state')
    def _compute_mark_readonly(self):
        for record in self:
            record.state_hide = (
                record.grade_assigment_id.state != 'grading_started'
            )
