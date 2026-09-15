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
    _inherit = "op.course"

    challenge_ids = fields.Many2many('gamification.challenge',
                                     string='Gamification Challenge')
    course_attempt_reward = fields.Integer("Attempt Reward")

    def _action_set_course_done(self):
        gains = sum(self.mapped('course_attempt_reward'))
        if not gains:
            return False
        return self.env.user.sudo().add_karma(gains)


class OpMaterial(models.Model):
    _inherit = "op.material"

    quiz_attempt_reward = fields.Integer("Attempt Reward")

    def _action_set_quiz_material_done(self):
        gains = sum(self.mapped('quiz_attempt_reward'))
        if not gains:
            return False
        return self.env.user.sudo().add_karma(gains)
