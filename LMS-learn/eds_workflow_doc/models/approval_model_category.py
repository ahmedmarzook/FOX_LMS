"""
Created on Apr 3, 2019

@author: Zuhair Hammadi
"""

from odoo import models, fields


class ApprovalModelCategory(models.Model):
    _name = "approval.model.category"
    _description = _name

    name = fields.Char(required=True, translate=True)
    menu_id = fields.Many2one("ir.ui.menu", readonly=True)
