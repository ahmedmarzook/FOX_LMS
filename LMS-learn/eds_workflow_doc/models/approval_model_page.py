"""
Created on Apr 1, 2019

@author: Zuhair Hammadi
"""

from odoo import models, fields, api


class ApprovalModelPage(models.Model):
    _name = "approval.model.page"
    _description = _name
    _order = "sequence,id"

    approval_model_id = fields.Many2one(
        "approval.model", required=True, ondelete="cascade"
    )
    name = fields.Char("Label", required=True)
    sequence = fields.Integer()
    field_id = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id','=', parent.model_id), ('state','=', 'manual'),('ttype','=','one2many')]",
    )
    editable = fields.Selection([("top", "top"), ("bottom", "bottom")])
    model_id = fields.Many2one("ir.model", compute="_calc_model_id")
    page_field_ids = fields.One2many("approval.model.page.field", "page_id")

    @api.depends("field_id")
    def _calc_model_id(self):
        IrModel = self.env["ir.model"]
        for record in self:
            record.model_id = IrModel._get(record.field_id.relation)

    @api.onchange("field_id")
    def _onchange_field_id(self):
        if self.field_id and not self.name:
            self.name = self.field_id.field_description
