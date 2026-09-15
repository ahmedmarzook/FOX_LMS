"""
Created on Apr 1, 2019

@author: Zuhair Hammadi
"""

from odoo import models, fields


class ApprovalModelPageField(models.Model):
    _name = "approval.model.page.field"
    _description = _name
    _order = "sequence,id"

    sequence = fields.Integer()
    page_id = fields.Many2one("approval.model.page", required=True, ondelete="cascade")
    field_id = fields.Many2one(
        "ir.model.fields",
        required=True,
        domain="[('model_id','=', parent.model_id), ('state','=', 'manual')]",
        ondelete="cascade",
    )
    tree_invisible = fields.Boolean()
    form_invisible = fields.Boolean()
