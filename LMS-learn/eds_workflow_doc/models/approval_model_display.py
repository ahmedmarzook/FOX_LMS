"""
Created on Mar 31, 2019

@author: Zuhair Hammadi
"""

from odoo import models, fields


class ApprovalModelDisplay(models.Model):
    _name = "approval.model.display"
    _description = _name
    _order = "sequence,id"

    approval_model_id = fields.Many2one(
        "approval.model", required=True, ondelete="cascade"
    )
    name = fields.Char("Label")
    sequence = fields.Integer()
    field_id = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id','=', parent.model_id), ('state','=', 'manual'),('ttype','not in',['one2many'])]",
    )

    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )
