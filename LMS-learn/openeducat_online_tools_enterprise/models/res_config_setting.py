# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    automatic_email = fields.Boolean(
        string='Automatic Email',
        config_parameter='calendar.automaticemail',
    )
