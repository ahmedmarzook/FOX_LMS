# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpCourse(models.Model):
    _name = "op.course"
    _inherit = "op.course"

    survey_ids = fields.One2many('survey.survey', 'course_id', string='Survey')

    def get_survey(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "survey.action_survey_form"
        )
        action["domain"] = [("course_id", "=", self.id)]
        action["context"] = {
            **self.env.context,
            "default_course_id": self.id,
        }
        return action
