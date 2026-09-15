# -*- coding: utf-8 -*-
from odoo import fields, models


class OpCourse(models.Model):
    _inherit = 'op.course'

    doctor_name = fields.Char(
        string='Doctor Name',
        help='Name of the doctor associated with this course.',
    )
