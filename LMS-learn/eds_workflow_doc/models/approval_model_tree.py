"""
Created on Apr 1, 2019

@author: Zuhair Hammadi
"""

from odoo import models, fields


class ApprovalModelTree(models.Model):
    _name = "approval.model.tree"
    _description = _name
    _order = "sequence,id"

    approval_model_id = fields.Many2one(
        "approval.model", required=True, ondelete="cascade"
    )
    sequence = fields.Integer()
    field_id = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id','=', parent.model_id),('ttype','not in',['one2many'])]",
    )
