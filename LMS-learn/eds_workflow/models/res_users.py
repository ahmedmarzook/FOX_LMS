"""
Created on Sep 18, 2018

@author: Zuhair Hammadi
"""

from odoo import models, fields, api


class User(models.Model):
    _inherit = "res.users"

    wkf_groups_ids = fields.Many2many("res.groups", compute="_calc_wkf_groups_ids")

    @api.depends("group_ids")
    def _calc_wkf_groups_ids(self):
        field = "active_groups_ids" in self and "active_groups_ids" or "group_ids"
        for record in self:
            record.wkf_groups_ids = record[field]

    def get_display_name(self):
        if "employee_ids" in self and self.employee_ids:
            return self.employee_ids[:1].display_name

        return self.display_name
