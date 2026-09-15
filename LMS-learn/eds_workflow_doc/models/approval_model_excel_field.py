"""
Created on Apr 4, 2019

@author: Zuhair Hammadi
"""

from odoo import models, fields


class ApprovalModelExcelField(models.Model):
    _name = "approval.model.excel.field"
    _description = _name
    _order = "sequence,id"

    excel_id = fields.Many2one(
        "approval.model.excel", required=True, ondelete="cascade"
    )
    field_id = fields.Many2one(
        "ir.model.fields",
        required=True,
        domain="[('model_id','=', parent.model_id)]",
        ondelete="cascade",
    )
    sequence = fields.Integer()
