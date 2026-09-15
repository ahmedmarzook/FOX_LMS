# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import models


class TranscriptConfig(models.Model):
    _inherit = "op.student.progression"

    def print_report(self):
        self.ensure_one()
        return self.env.ref(
            "openeducat_exam_gpa_enterprise.action_report_transcript"
        ).report_action(self)
