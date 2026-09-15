"""
Created on Dec 28, 2016

@author: zuhair
"""

from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class Group(models.Model):
    _inherit = "res.groups"

    allow_delegation = fields.Boolean("Allow Delegation")
    delegation_template_ids = fields.Many2many(
        "mail.template",
        "res_groups_delegation_templates",
        "group_id",
        "template_id",
        "Delegation Email Templates",
    )
    name2 = fields.Char()

    allow_multiple_delegation = fields.Boolean(
        "Allow Multiple Delegation", default=False
    )
    restricted_access = fields.Boolean("Allow in Restricted Access")

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name2 or record.full_name))
        return result
