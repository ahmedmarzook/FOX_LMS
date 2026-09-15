"""
Created on Apr 4, 2019

@author: Zuhair Hammadi
"""

from odoo import models, fields


class ApprovalModelExcel(models.Model):
    _name = "approval.model.excel"
    _description = _name

    name = fields.Char(required=True)
    approval_model_id = fields.Many2one(
        "approval.model", required=True, ondelete="cascade"
    )
    model_id = fields.Many2one(
        "ir.model", related="approval_model_id.model_id", readonly=True
    )

    field_ids = fields.One2many("approval.model.excel.field", "excel_id")

    action_id = fields.Many2one("ir.actions.server", readonly=True)

    def create_action(self):
        if self.action_id:
            return
        self.action_id = self.env["ir.actions.server"].create(
            {
                "name": self.name,
                "model_id": self.approval_model_id.model_id.id,
                "binding_model_id": self.approval_model_id.model_id.id,
                "binding_type": "report",
                "state": "code",
                "code": "action = records.get_excel('%s')" % self._create_external_id(),
            }
        )

    def remove_action(self):
        self.action_id.unlink()
