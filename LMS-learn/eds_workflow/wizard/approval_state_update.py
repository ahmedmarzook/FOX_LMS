"""
Created on May 22, 2019

@author: Zuhair Hammadi
"""

from odoo import models, fields


class ChangeDocumentStatus(models.TransientModel):
    _name = "approval.state.update"
    _description = "Change Document Status"

    state = fields.Char(required=True, string="Status")
    res_model = fields.Char(required=True)
    res_ids = fields.Json(required=True)

    def action_update(self):
        records = self.env[self.res_model].browse(self.res_ids)

        # Store old states before update
        old_states = {}
        for record in records:
            old_states[record.id] = record.state

        # Update the state
        records.write({"state": self.state})

        # Log superuser intervention
        model_id = self.env["ir.model"]._get_id(self.res_model)
        for record in records:
            if old_states.get(record.id) != self.state:
                self.env["approval.log"].sudo().create(
                    {
                        "record_id": record.id,
                        "user_id": self.env.user.id,
                        "date": fields.Datetime.now(),
                        "state": self.state,
                        "model_id": model_id,
                        "description": "Status updated by superuser using 'Update Status' feature",
                    }
                )

        return {"type": "ir.actions.act_window_close"}
