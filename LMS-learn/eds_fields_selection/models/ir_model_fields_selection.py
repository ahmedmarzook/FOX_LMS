"""
Created on Jun 24, 2020

@author: Zuhair Hammadi
"""

from odoo import models


class IrModelSelection(models.Model):
    _inherit = "ir.model.fields.selection"

    def _update_selection(self, model_name, field_name, selection):
        if model_name in self.env:
            field = self.env[model_name]._fields.get(field_name)
            if field and self.pool.ready and not isinstance(field.selection, list):
                field_id = self.env["ir.model.fields"]._get(model_name, field_name)
                if field_id.state != "manual":
                    return
        return super(IrModelSelection, self)._update_selection(
            model_name, field_name, selection
        )
