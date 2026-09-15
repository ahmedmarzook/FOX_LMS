# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

import statistics

from odoo import api, fields, models


class AssignmentStatistics(models.TransientModel):
    _name = "assignment.statistics"
    _description = "Assignment Statistics"

    assignment_name = fields.Char(readonly=True)
    assignment_point = fields.Float(readonly=True)
    count = fields.Integer(readonly=True)
    minimum_value = fields.Float(readonly=True)
    maximum_value = fields.Float(readonly=True)
    sta_range = fields.Float(readonly=True)
    average = fields.Float(readonly=True)
    median = fields.Float(readonly=True)
    std_deviation = fields.Float(readonly=True)
    variances = fields.Float(readonly=True)
    graded = fields.Integer(readonly=True)
    need_grade = fields.Integer(readonly=True)
    grade_distribution = fields.Text(readonly=True)

    @api.model
    def default_get(self, field_names):
        values = super().default_get(field_names)
        active_id = self.env.context.get('active_id')
        if not active_id:
            return values
        lines = self.env['gradebook.line'].search([
            ('grade_assigment_id', '=', active_id)
        ])
        assignment = self.env['grading.assignment'].browse(active_id).exists()
        grades = [
            line.marks if line.marks else line.grade_table_line_id.percentage
            for line in lines
            if line.marks or line.grade_table_line_id
        ]
        distribution = []
        if assignment and assignment.course_id.grade_scale_id:
            for grade_type in assignment.course_id.grade_scale_id.op_grade_type_ids:
                qty = self.env['gradebook.line'].search_count([
                    ('grade_assigment_id', '=', active_id),
                    ('percentage', '>=', grade_type.min_percentage),
                    ('percentage', '<=', grade_type.max_percentage),
                ])
                distribution.append(
                    f"{grade_type.min_percentage} - {grade_type.max_percentage}: {qty}"
                )
        values.update({
            'assignment_name': assignment.name if assignment else False,
            'assignment_point': assignment.point if assignment else 0.0,
            'count': len(lines),
            'minimum_value': min(grades) if grades else 0.0,
            'maximum_value': max(grades) if grades else 0.0,
            'sta_range': (max(grades) - min(grades)) if grades else 0.0,
            'average': (sum(grades) / len(grades)) if grades else 0.0,
            'median': statistics.median(grades) if grades else 0.0,
            'std_deviation': statistics.stdev(grades) if len(grades) > 1 else 0.0,
            'variances': statistics.variance(grades) if len(grades) > 1 else 0.0,
            'graded': len(grades),
            'need_grade': len(lines) - len(grades),
            'grade_distribution': '\n'.join(distribution),
        })
        return values


class StudentStatistics(models.TransientModel):
    _name = "student.statistics"
    _description = "Student Statistics"

    student_name = fields.Char(readonly=True)
    gradebook_name = fields.Char(readonly=True)
    graded = fields.Integer(readonly=True)
    grades_published = fields.Integer(readonly=True)
    need_grading = fields.Integer(readonly=True)
    grades_archieve = fields.Integer(readonly=True)
    grades_given_att = fields.Integer(readonly=True)
    att_grades_publish = fields.Integer(readonly=True)
    grade_att = fields.Integer(readonly=True)
    att_grades_archive = fields.Integer(readonly=True)

    @api.model
    def default_get(self, field_names):
        values = super().default_get(field_names)
        gradebook_id = self.env.context.get('active_id')
        if not gradebook_id:
            return values
        gradebook = self.env['gradebook.gradebook'].browse(gradebook_id).exists()
        assignment_lines = self.env['gradebook.line'].search([
            ('gradebook_id', '=', gradebook_id),
            ('assignment_type_id.assign_type', '!=', 'attendance'),
        ])
        attendance_lines = self.env['gradebook.line'].search([
            ('gradebook_id', '=', gradebook_id),
            ('assignment_type_id.assign_type', '=', 'attendance'),
        ])
        assignment_graded = assignment_lines.filtered(
            lambda line: line.marks or line.grade_table_line_id
        )
        attendance_graded = attendance_lines.filtered(lambda line: line.marks)
        values.update({
            'student_name': gradebook.student_id.name if gradebook else False,
            'gradebook_name': gradebook.name if gradebook else False,
            'graded': len(assignment_graded),
            'grades_published': self.env['gradebook.line'].search_count([
                ('gradebook_id', '=', gradebook_id),
                ('assignment_type_id.assign_type', '!=', 'attendance'),
                ('grade_assigment_id.state', '=', 'grades_published'),
            ]),
            'need_grading': len(assignment_lines) - len(assignment_graded),
            'grades_archieve': self.env['gradebook.line'].search_count([
                ('gradebook_id', '=', gradebook_id),
                ('assignment_type_id.assign_type', '!=', 'attendance'),
                ('grade_assigment_id.state', '=', 'grades_published'),
                ('grade_assigment_id.active', '=', False),
            ]),
            'grades_given_att': len(attendance_graded),
            'att_grades_publish': self.env['gradebook.line'].search_count([
                ('gradebook_id', '=', gradebook_id),
                ('assignment_type_id.assign_type', '=', 'attendance'),
                ('grade_assigment_id.state', '=', 'grades_published'),
                ('grade_assigment_id.active', '=', True),
            ]),
            'grade_att': len(attendance_lines) - len(attendance_graded),
            'att_grades_archive': self.env['gradebook.line'].search_count([
                ('gradebook_id', '=', gradebook_id),
                ('assignment_type_id.assign_type', '=', 'attendance'),
                ('grade_assigment_id.state', '=', 'grades_published'),
                ('grade_assigment_id.active', '=', False),
            ]),
        })
        return values
